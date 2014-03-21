from access_tokens.models import AccessToken
from django.http import HttpResponse
from django.shortcuts import redirect
from faceoff.decorators import require_parameters
from proxy import general_config
from proxy.authentication.appkey_providers import AppKeyProvider, \
    AuthenticationError
import json
import logging

logger = logging.getLogger('proxy')

# TODO THIS NEEDS TO BE REWRITTEN for OPEN SOURCE
@require_parameters(['client_id', 'response_type'])
def authorization(request):
    
    try:
        analytics = general_config().analytics

        client_id = request.GET.get('client_id')
        response_type = request.GET.get('response_type')
        state = request.GET.get('state', '')

        auth_failed = False
        
        try:
            provider = AppKeyProvider()
            a = provider.authorize(request)
            redirect_uri = request.GET.get('redirect_uri', None)
            if redirect_uri is not None:
                if redirect_uri != a.redirect_uri:
                    # require them to be equal for now
                    redirect_uri = None
        except Exception, e:
            logger.error("AUTH ERROR WAS %s" % e)
            auth_failed = True
        if isinstance(a, AuthenticationError):
            auth_failed = True
            
        if auth_failed:
            err = {"error": "4030", "message": "Client id not valid"}
            analytics.increment("proxy.access_tokens.views.authorization.client_id_not_valid.4030.fail")
            return HttpResponse(json.dumps(err), content_type="application/json", status=403)
            
        if response_type == "token":
            if 'facebook_access_token' in request.REQUEST or 'device_id' in request.REQUEST or 'ias_user_id' in request.REQUEST:
                user = None
                try:
                    user = general_config().user_provider.find(facebook_access_token=request.REQUEST.get('facebook_access_token'), device_id=request.REQUEST.get('device_id'), ias_user_id=request.REQUEST.get('ias_user_id'), headers=provider.get_headers(a))
                except Exception, e:
                    err = {"error": "500", "message": "connection error"}
                    analytics.increment("proxy.access_tokens.views.authorization.user_provider_connection_error.500.fail")
                    return HttpResponse(json.dumps(err), content_type="application/json", status=500)

                if user is None:
                    err = {"error": "4032", "message": "user not found"}
                    analytics.increment("proxy.access_tokens.views.authorization.user_not_found.4032.fail")
                    return HttpResponse(json.dumps(err), content_type="application/json", status=403)

                if 'facebook_access_token' in request.REQUEST:
                    analytics.increment("proxy.access_tokens.views.authorization.param.facebook_access_token")
                if 'device_id' in request.REQUEST:
                    analytics.increment("proxy.access_tokens.views.authorization.param.device_id")
                if 'ias_user_id' in request.REQUEST:
                    analytics.increment("proxy.access_tokens.views.authorization.param.ias_user_id")

                t = AccessToken()
                t.user = user.get('id')
                t.application = a
                t.is_active = True
                t.save()

                analytics.increment("proxy.access_tokens.views.authorization.token_created.success")

                if redirect_uri is not None:
                    return redirect("%s#access_token=%s&state=%s&token_type=bearer" % (redirect_uri, t.token, state))
                else:
                    resp_dict = {'access_token': t.token,
                                 'state': state,
                                 'token_type': 'bearer'}
                    return HttpResponse(json.dumps(resp_dict), content_type='application/json')
            else:
                analytics.increment("proxy.access_tokens.views.authorization.parameter_missing.422.fail")
                return HttpResponse("Required Parameter Missing", status=422)
        else:

            analytics.increment("proxy.access_tokens.views.authorization.token_auth_not_implmented.501.fail")

            err = {"error": "501", "message": "Token auth not implemented yet"}
            return HttpResponse(json.dumps(err), content_type="application/json", status=501)

    except Exception, e:
        analytics.increment("proxy.access_tokens.views.authorization.general_failure.%s.500.fail" % e.__class__.__name__)
        err = {"error": "500", "message": "Server Error"}
        return HttpResponse(json.dumps(err), content_type="application/json", status=500)
