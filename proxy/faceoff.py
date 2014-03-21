import collections
import json
import logging
from datetime import datetime
import os

from django.conf.urls import patterns, url
from termcolor import colored
from applications import application_cache

import proxy
from proxy import general_config
from proxy.analytics import ChainedAnalytics
from proxy.cache import CacheManager, NoCacheManager
from proxy.utils import load_class_from_name
from proxy.views import ProxyView, SimpleProxyHealthCheck

logger = logging.getLogger(__name__)


# TODO: This init_global_config method has become a bit of a monster
# TODO: Probably should refactor it
# TODO: For "tests", we should init a much smaller version of this

def init_global_config(general_json_config):
    if hasattr(general_config(), "configuration_complete"):
        return
    start = datetime.now()
    errors = "no"
    logger.info(colored("-------------------------------------------------", "green"))
    logger.info(colored("Face/Off Version %s" % proxy.__version__, "green"))
    logger.info(colored("I'd like to take his face... off.", "green"))
    logger.info(colored("-------------------------------------------------", "green"))

    global_faceoff_config = general_config()
    global_faceoff_config.domain_name = general_json_config.get('domain_name', None)
    env_domain = os.environ.get("FACEOFF_DOMAIN_NAME", None)
    overrode_domain_from_env = False
    if env_domain is not None:
        global_faceoff_config.domain_name = env_domain
        overrode_domain_from_env = True
    if global_faceoff_config.domain_name is None:
        logger.warning("No domain name in your config, which could cause problems with facaded APIs that need it")
    else:
        logger.info("Configuring Face/Off with domain name: %s, Overrode from FACEOFF_DOMAIN_NAME env variable: %s"
                    % (global_faceoff_config.domain_name, overrode_domain_from_env))

    global_faceoff_config.timeout = float(general_json_config.get('timeout', '.500'))
    logger.info("Configuring Face/Off with timeout of %s" % global_faceoff_config.timeout)
    application_object_name = general_json_config.get('application_object', None)
    if application_object_name is not None:
        try:
            application_object = load_class_from_name(application_object_name)
            global_faceoff_config.application_object = application_object
            logger.info("Configuring Face/Off with application object: %s " % application_object_name)
        except Exception, e:
            errors = "some"
            logger.error("Could not load application object with name %s" % (application_object_name,))
    else:
        global_faceoff_config.application_object = None
        logger.warning("No application object!  Can't use AppKeyProvider authentication handle")

    analytic_classes = general_json_config.get('analytics', [])
    analytics = ChainedAnalytics()
    for analytic_class in analytic_classes:
        if isinstance(analytic_class, dict):
            function = analytic_class.get('function')
            parameters = analytic_class.get('parameters')
        elif isinstance(analytic_class, basestring):
            function = analytic_class
            parameters = {}
        else:
            logger.error("Could not load analytics class with config %s" % (analytic_class,))
            errors = "some"
            continue
        try:
            analytics.add_analytic(load_class_from_name(function)(**parameters))
        except Exception, e:
            errors = "some"
            logger.error("Could not load analytics class with name %s because of %s" % (analytic_class, e))

    global_faceoff_config.analytics = analytics
    logger.info("Configuring Face/Off with analytics classes: %s", analytic_classes)

    try:
        user_provider_config = general_json_config.get('user_provider', {})
        user_function = user_provider_config.get('function')
        parameters = user_provider_config.get('parameters', {})
        global_faceoff_config.user_provider = load_class_from_name(user_function)(**parameters)
        logger.info("Configuring Face/Off with user provider config: %s", user_provider_config)

    except Exception, e:
        if general_json_config.get('user_provider') is None:
            logger.warning("There is no user provider class, this means Face/Off can't protect endpoints by consumer keys")
        else:
            errors = "some"
            logger.error("Could not load user provider class with config %s" % (general_json_config.get('user_provider')))

    user_provider_servers = general_json_config.get('user_provider_servers', [])
    global_faceoff_config.user_provider_servers = user_provider_servers

    health_check = general_json_config.get('health_check_storage', {}).get('implementation', None)
    if health_check is not None:
        redis_health_check_config = general_json_config.get('health_check_storage')
        global_faceoff_config.health_check = load_class_from_name(redis_health_check_config.get('implementation'))(**general_json_config.get('health_check_storage'))

    else:
        logger.warning("You have no healthcheck implementation.  This probably means you have no healthchecks!")
        global_faceoff_config.health_check = None

    health_check_url = general_json_config.get("self_health_check_url", "proxy-check")
    logger.info("Proxy self-check URL is %s", health_check_url)

    if "cache" in general_json_config:
        global_faceoff_config.cache = CacheManager(general_json_config.get('cache'))
    else:
        global_faceoff_config.cache = NoCacheManager()

    application_cache().load_from_db()  # fill application_cache
    logger.info("Application in memory cache loaded with %s applications" % (len(application_cache().all()),))
    stop = datetime.now()
    if errors == "some":
        color = "red"
    else:
        color = "green"

    global_faceoff_config.configuration_complete = True
    global_faceoff_config.errors_during_init = errors == "some"

    logger.info(colored("-------------------------------------------------", color))
    logger.info(colored("Face/Off started in %sms with %s errors" % ((stop - start).microseconds, errors), color))
    logger.info(colored("-------------------------------------------------", color))


def load_config(cfg_file):
    logger.info("Using configuration file at %s" % cfg_file)
    f = open(cfg_file, 'r')
    config = json.loads(f.read(), object_pairs_hook=collections.OrderedDict)
    f.close()
    return config


def add_proxies(cfg_file):
    config = load_config(cfg_file)
    return add_proxies_from_data(config)


def add_proxies_from_data(config):
    urlpatterns = []
    init_global_config(config.get('general', {}))

    for key in config.get('endpoints').keys():
        endpoint_cfg = config.get('endpoints').get(key)
        endpoint_cfg['pattern'] = key
        urlpatterns += patterns('proxy.views',
                                url(key, ProxyView().as_view(cfg=endpoint_cfg))
        )
        general_config().cache.enable_caching_for_endpoint(key, endpoint_cfg)

    health_check_url = config.get('general', {}).get("self_health_check_url", "^proxy-check$")
    urlpatterns += patterns('proxy.views',
                            url(health_check_url, SimpleProxyHealthCheck().as_view(cfg=config)))

    invalidation_endpoint = general_config().cache.add_invalidation_endpoint()
    if invalidation_endpoint is not None:
        urlpatterns += invalidation_endpoint

    return urlpatterns

