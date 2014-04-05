from functools import partial
import json
import datetime
import logging
import requests

from requests.exceptions import ConnectionError, Timeout, SSLError

from django.utils.timezone import utc
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.views.generic import View

from proxy import __version__
from proxy import general_config
from proxy.authentication.appkey_providers import AuthenticationError
from proxy.cache.stores import CacheKeyMaker
from proxy.exceptions import FaceOffException
from proxy.signals import pre_is_allowed_check, post_is_allowed_check, pre_healthcheck, post_healthcheck, pre_get_real_url_to_call, post_get_real_url_to_call, pre_auth_flow, post_auth_flow
from proxy.transformers.exceptions import TransformerException
from proxy.utils import load_class_from_name, get_all_http_request_headers, get_content_request_headers_only, hop_headers, dthandler, str2bool, parse_basic_auth, convert_variable_to_env_setting, init_classes_with_params_from_dict

logger = logging.getLogger(__name__)


def index(request):
    return HttpResponse(json.dumps({"welcome": "proxy"}), content_type="application/json")


class SimpleProxyHealthCheck(View):

    cfg = None
    endpoints = []
    domain_name = ""
    startup_time = None

    @classmethod
    def as_view(cls, **initkwargs):
        initkwargs['endpoints'] = initkwargs.get('cfg').get('endpoints', [])
        initkwargs['domain_name'] = general_config().domain_name
        initkwargs['startup_time'] = datetime.datetime.now(tz=utc)
        view = super(SimpleProxyHealthCheck, cls).as_view(**initkwargs)
        return view

    def dispatch(self, request, *args, **kwargs):
        health_check_results = None
        if str2bool(request.GET.get('details', "False")):
            if general_config().health_check is not None:
                health_check_results = {}
                for endpoint_url in self.endpoints:
                    endpoint = self.endpoints.get(endpoint_url)
                    if endpoint is not None:
                        health_check_results[endpoint.get('name').lower()] = general_config().health_check.get_service_status(endpoint.get('name').lower())

        res = {"success": True,
           "number_of_endpoints": len(self.endpoints),
           "domain_name": self.domain_name,
           "version": __version__,
           "startup_time": self.startup_time }

        if health_check_results is not None:
            res['endpoint_statuses'] = health_check_results

        return HttpResponse(json.dumps(res, default=dthandler), content_type="application/json")


class ProxyView(View):
    cfg = None
    analytics = None
    rotation_policy = None
    auth = None
    pattern = None
    auth_provider_class = None
    request_transformers = []
    response_transformers = []
    cached = False
    cache_rules = []
    cache_key = None

    @classmethod
    def as_view(cls, **initkwargs):
        initkwargs = cls.init_analytics(**initkwargs)
        initkwargs = cls.init_backend_servers(**initkwargs)
        initkwargs = cls.init_auth(**initkwargs)
        initkwargs = cls.init_transformers(**initkwargs)
        initkwargs = cls.init_cache(**initkwargs)

        view = super(ProxyView, cls).as_view(**initkwargs)
        return view

    @classmethod
    def init_cache(cls, **initkwargs):
        initkwargs['cached'] = initkwargs.get('cfg', {}).get('cache', {}).get('enabled', False)
        initkwargs['pattern'] = initkwargs.get('cfg', {}).get('pattern')
        initkwargs['cache_rules'] = []
        rules = initkwargs.get('cfg', {}).get('cache',{}).get('rules', {})
        initkwargs['cache_rules'] = init_classes_with_params_from_dict(rules)
        return initkwargs

    @staticmethod
    def __init_classes_with_params_from_dict__(class_dictionary):
        results = {}
        for entity in class_dictionary:
            cls = load_class_from_name(entity)
            inited_cls = cls(**class_dictionary.get(entity, {}))
            results.append(inited_cls)
        return results


    @classmethod
    def init_transformers(cls, **initkwargs):
        transformers_cfg = initkwargs.get('cfg').get('transformers', {})

        request_transformers_cfg = transformers_cfg.get('request_transformers', {})
        response_transformers_cfg = transformers_cfg.get('response_transformers', {})

        initkwargs['request_transformers'] = init_classes_with_params_from_dict(request_transformers_cfg)
        initkwargs['response_transformers'] = init_classes_with_params_from_dict(response_transformers_cfg)
        return initkwargs

    @classmethod
    def init_analytics(cls, **initkwargs):
        initkwargs["analytics"] = general_config().analytics
        return initkwargs

    @classmethod
    def init_backend_servers(cls, **initkwargs):
        server = initkwargs.get('cfg').get('server')
        rotation_policy_clazz = server.get('rotation_policy', "proxy.rotations.RoundRobin")
        RotationPolicyClass = load_class_from_name(rotation_policy_clazz)
        actual_servers = []
        for x in server.get('servers'):
            actual_servers.append(convert_variable_to_env_setting(x))
        initkwargs['rotation_policy'] = RotationPolicyClass(actual_servers)
        return initkwargs

    @classmethod
    def init_auth(cls, **initkwargs):
        auth = initkwargs.get('cfg').get('auth', False)
        initkwargs['auth'] = auth

        if auth:
            auth_backend = initkwargs.get('cfg').get('auth_provider', 'proxy.authentication.AppKeyProvider')
            initkwargs['auth_provider_class'] = load_class_from_name(auth_backend)()
        return initkwargs

    def is_service_up(self):
        pre_healthcheck.send(sender=self, request=self.request)
        status = not (general_config().health_check is not None and not general_config().health_check.get_service_status(self.cfg.get('name').lower()))
        if not status:
            self.analytics.increment("proxy.%s.service.fail" % self.cfg.get('name').lower())
            self.err = {"error": 500, "message": "service_failure"}
        post_healthcheck.send(sender=self, request=self.request, status=status, error=self.err)
        return status

    # Check if the method is allowed and if it requires HTTPS
    def is_allowed(self):
        pre_is_allowed_check.send(sender=self, request=self.request)

        status = True
        if self.request.method not in self._allowed_methods():
            self.analytics.increment("proxy.%s.dispatch.method_not_allowed" % self.cfg.get('name').lower())
            self.err = {"error": 403, "message": "HTTP Method not allowed"}
            status = False
        elif self.cfg.get('https_only', False) and not self.request.is_secure():
            self.analytics.increment("proxy.%s.dispatch.https_required" % self.cfg.get('name').lower())
            self.err = {"error": 403, "message": "HTTP Method not allowed"}
            status = False
        else:
            self.analytics.increment("proxy.%s.dispatch.method_allowed" % self.cfg.get('name').lower())
            self.analytics.increment("proxy.%s.dispatch.method_allowed.%s" % (self.cfg.get('name').lower(), self.request.method.lower()))

        post_is_allowed_check.send(sender=self, request=self.request, status=status, error=self.err)
        return status

    # Gets the real URL and Requests method that Face/Off will be proxying to (with appropriate transformations)
    def get_url_to_call(self):

        url_to_call = self.rotation_policy.pick()

        pre_get_real_url_to_call.send(sender=self, request=self.request, url_to_call=url_to_call)
        web_call = getattr(requests, self.request.method.lower())

        if "@" in url_to_call: # this is a basic AUTH call, mebbe?
            basic_auth_params = parse_basic_auth(url_to_call)
            url_to_call = basic_auth_params.get('url', url_to_call)
            web_call = partial(web_call, auth=(basic_auth_params['login'], basic_auth_params['password']))

        self.analytics.increment("proxy.%s.dispatch.server.get_url" % (self.cfg.get('name').lower(), ))

        #TODO the regex matcher/resolver is a bit of a hack, it only works for one match ($1) - we should make this legit

        if len(self.request.resolver_match.args) > 0:
            matched = self.request.resolver_match.args[0]
            url_to_call = url_to_call.replace("$1", matched)

        self.web_call = web_call
        self.url_to_call = url_to_call

        post_get_real_url_to_call.send(sender=self, request=self.request, url_to_call=url_to_call, web_call=web_call)
        return web_call, url_to_call

    def auth_flow(self, custom_headers, *args, **kwargs):
        pre_auth_flow.send(sender=self, request=self.request, custom_headers=custom_headers, auth=self.auth)
        try:
            if self.auth:
                auth_response = self.auth_provider_class.authorize(self.request, *args, **kwargs)
                if isinstance(auth_response, AuthenticationError):
                    self.analytics.increment("proxy.%s.dispatch.server.auth_failed" % (self.cfg.get('name').lower(), ))
                    self.err = auth_response.to_dict()
                    status = False
                else:
                    custom_headers.update(self.auth_provider_class.get_headers(auth_response))
                    status = True
            else:
                return True
        except Exception as e:
            self.err = {"error": 403, "message": "auth_error"}
            self.analytics.increment("proxy.%s.dispatch.server.user_auth_error.fail" % (self.cfg.get('name').lower(), ))
            status = False

        post_auth_flow.send(sender=self, request=self.request, custom_headers=custom_headers, auth=self.auth, status=status)
        return status

    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        self.request = request
        self.err = None

        custom_headers = {}
        if general_config().domain_name is not None:
            custom_headers = {'X_FORWARDED_HOST': general_config().domain_name}

        self.get_url_to_call()

        if not self.auth_flow(custom_headers, *args, **kwargs):
            return HttpResponse(json.dumps(self.err), content_type="application/json", status=self.err.get('error'))

        if not self.is_allowed():
            return HttpResponse(json.dumps(self.err), content_type="application/json", status=self.err.get('error'))

        if self.cached:
            cache_key_maker = CacheKeyMaker()
            cache_key_maker.set_request(self.request)

            for rule in self.cache_rules:
                rule.run_rule(cache_key_maker)

            cache_key = cache_key_maker.build_key()
            response = general_config().cache.store.retrieve(cache_key)
            if response is not None:
                logger.info("Cache HIT for %s" % cache_key)
                return response
            else:
                logger.info("Cache MISS for %s" % cache_key)

        if not self.is_service_up():
            return HttpResponse(json.dumps(self.err), content_type="application/json", status=self.err.get('error'))

        try:
            request.GET = request.GET.copy()  # make request objects mutable for the transformers
            for transformer in self.request_transformers:
                request = transformer.transform_request(request)

            if request.method.lower() in ['post', 'put']:
                self.web_call = partial(self.web_call, data=request.body, params=request.GET.lists())
            else:
                self.web_call = partial(self.web_call, params=request.GET.lists())

            if self.cfg.get('pass_headers', False):
                self.web_call = partial(self.web_call, headers=get_all_http_request_headers(request, custom_headers))
            else:
                self.web_call = partial(self.web_call, headers=get_content_request_headers_only(request, custom_headers))

            response = self.web_call(self.url_to_call, timeout=general_config().timeout)

            django_resp = HttpResponse(response.text, status=response.status_code)
            for header in response.headers.keys():
                if header not in hop_headers:
                    if header != "content-encoding":
                        django_resp[header] = response.headers.get(header)

            django_resp['content-length'] = len(response.content)
            
            for transformer in self.response_transformers:
                django_resp = transformer.transform_response(django_resp)

            self.analytics.increment("proxy.%s.dispatch.server.success" % (self.cfg.get('name').lower(),))

            if self.cached:
                general_config().cache.store.store(cache_key, django_resp)

            return django_resp
        except TransformerException as e:
            self.analytics.increment("proxy.%s.dispatch.server.transformer_exception.fail" % (self.cfg.get('name').lower(), ))
            err = e.to_dict()
            return HttpResponse(json.dumps(err), content_type="application/json", status=e.error_code)
        except FaceOffException as e:
            self.analytics.increment("proxy.%s.dispatch.server.faceoff_exception.fail" % (self.cfg.get('name').lower(), ))
            err = e.to_dict()
            return HttpResponse(json.dumps(err), content_type="application/json", status=e.error_code)
        except (SSLError, Timeout) as e: # Timeouts are SSLErrors if url is SSL
            err = {"error": "408", "message": "service_time_out"}
            self.analytics.increment("proxy.%s.dispatch.server.service_time_out.fail" % (self.cfg.get('name').lower(), ))
            logger.warning("Service timed out for %s" % self.cfg.get('name') )
            return HttpResponse(json.dumps(err), content_type="application/json", status=408)
        except ConnectionError as e:
            err = {"error": "1", "message": "connection_error"}
            self.analytics.increment("proxy.%s.dispatch.server.connection_error.fail" % (self.cfg.get('name').lower(), ))
            logger.warning("Service connection errored for %s" % self.cfg.get('name') )
            return HttpResponse(json.dumps(err), content_type="application/json", status=502)
        except Exception as e:
            err = {"error": "500", "message": "service_error"}
            self.analytics.increment("proxy.%s.dispatch.server.generic_service_exception.fail" % (self.cfg.get('name').lower(), ))

            return HttpResponse(json.dumps(err), content_type="application/json", status=500)

    def _allowed_methods(self):
        if 'http_method_names' in self.cfg:
            return [x.upper() for x in self.cfg.get('http_method_names')]
        else:
            return ['GET', 'POST', 'OPTIONS', 'DELETE', 'PUT']
