from django.conf.urls import patterns, url
from proxy.cache.views import invalidate_cache_view
from proxy.utils import load_class_from_name

import logging

logger = logging.getLogger(__name__)


class CacheManager(object):
    def __init__(self, config):
        try:
            cache_store = load_class_from_name(config.get("function"))
            self.store = cache_store(config=config)
            self.endpoint_configs = {}
            self.config = config
            logger.info("Using cache store: %s" % config.get('function'))
        except Exception, e:
            logger.error("Could not initialize Cache with %s", config, exc_info=True)

    def enable_caching_for_endpoint(self, endpoint, endpoint_cfg):
        if 'cache' in endpoint_cfg and endpoint_cfg.get('cache', False):
            self.endpoint_configs[endpoint] = endpoint_cfg

    def add_invalidation_endpoint(self):
        logger.info("Invalidate cache url endpoint: %s" % self.config.get('invalidation_url', '^cache/invalidate$'))
        return patterns('proxy.cache.views',
                        url(self.config.get('invalidation_url', '^cache/invalidate$'),
                            invalidate_cache_view))

    def get_from_cache(self, pattern, request):
        return self.endpoint_configs.get(pattern)


class NoCacheManager(CacheManager):
    def __init__(self):
        logger.info("Face/Off deployed with no caching")

    def add_endpoint(self, endpoint, cfg):
        pass

    def add_invalidation_endpoint(self):
        pass

    def get_from_cache(self, request):
        return None