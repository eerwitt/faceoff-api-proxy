from proxy import general_config

__author__ = 'nick'
import logging
import hashlib

try:
    import cPickle as pickle
except:
    import pickle


from django.conf import settings
from redis import StrictRedis, ConnectionError
from proxy.utils import convert_variable_to_env_setting


logger = logging.getLogger(__name__)


class CacheKeyMaker(object):

    def __init__(self, request=None):
        if request is not None:
            self.set_request(request)
        else:
            self.request = None
            self.cache_components = {}
            self.hash_key = None

    def set_request(self, request):
        self.request = request
        self.cache_components = {
            'GET': dict(request.GET),
            'POST': dict(request.POST),
            'PATH': request.path,
            'EXTRA': None
        }
        self.hash_key = None

    def build_key(self, force_rebuild=False):
        if self.hash_key is None or force_rebuild:
            source_key = settings.SECRET_KEY + ":"
            source_key += "%s:" % self.cache_components.get('PATH')
            source_key += "%s:" % self.cache_components.get('GET')
            source_key += "%s:" % self.cache_components.get('POST')
            source_key += "%s" % self.cache_components.get('EXTRA')
            self.hash_key = hashlib.sha224(source_key.encode('utf-8')).hexdigest()
            logger.debug("Hash_Key for %s created as %s" % (source_key, self.hash_key))

        return self.hash_key

    def store_with_key(self, value):
        general_config().cache.store.store(self.build_key(), value)

    def get_with_key(self):
        return general_config().cache.store.retrieve(self.build_key())

    def invalidate_with_key(self):
        general_config().cache.store.invalidate(self.build_key())


class SimpleCacheKeyMaker(CacheKeyMaker):

    def __init__(self, base_key):
        self.base_key = base_key
        self.hash_key = None
        self.build_key(force_rebuild=True)

    def build_key(self, force_rebuild=False):
        if force_rebuild:
            source_key = settings.SECRET_KEY + ":"
            source_key += self.base_key
            self.hash_key = hashlib.sha224(source_key).hexdigest()
            logger.debug("Simple hash_Key for %s created as %s" % (source_key, self.hash_key))

        return self.hash_key

    def set_request(self, request):
        raise NotImplementedError()


class UserCacheKeyMaker(CacheKeyMaker):
    def __init__(self, user):
        self.user = user
        self.hash_keys = []
        self.build_key(force_rebuild=True)

    def build_key(self, force_rebuild=False):
        if force_rebuild:
            source_key = settings.SECRET_KEY+":user_request:user_id="+str(self.user['id'])
            self.hash_keys.append(hashlib.sha224(source_key.encode('utf-8')).hexdigest())

        return self.hash_keys

    def get_with_key(self):
        for hash_key in self.build_key():
            result = general_config().cache.store.retrieve(hash_key)
            if result is not None:
                return result

    def store_with_key(self, value):
        for hash_key in self.build_key():
            general_config().cache.store.store(hash_key, value)

    def invalidate_with_key(self):
        for hash_key in self.build_key():
            general_config().cache.store.invalidate(hash_key)


class APICacheStore(object):

    def __init__(self, *args, **kwargs):
        pass

    def retrieve(self, key):
        return None

    def store(self, key, value, ttl=None):
        pass

    def invalidate(self, key):
        pass

    def flush(self):
        pass


class SimpleInMemoryCacheStore(APICacheStore):

    def __init__(self, *args, **kwargs):
        self.cache = {}
        super(SimpleInMemoryCacheStore, self).__init__(*args, **kwargs)

    def retrieve(self, key):
        return self.cache.get(key, None)

    def store(self, key, value, ttl=None):
        self.cache[key] = value

    def invalidate(self, key):
        try:
            del self.cache[key]
        except:
            pass

    def flush(self):
        self.cache = {}


class RedisAPICacheStore(APICacheStore):

    def __init__(self, *args, **kwargs):
        self.config = kwargs.get('config', {})
        self.ttl = self.config.get('ttl', 300)

        super(RedisAPICacheStore, self).__init__(*args, **kwargs)
        if self.config.get("use_settings", False):
            redis_settings = settings.CACHE_REDIS
        else:
            redis_settings = self.config.get('parameters')


        host = convert_variable_to_env_setting(redis_settings.get('host', "localhost"))
        port = redis_settings.get('port', 6379)
        db = redis_settings.get('db', 0)
        pw = redis_settings.get('password', None)

        timeout = redis_settings.get('timeout', .3)

        self.redis = StrictRedis(host=host,
                                 port=port,
                                 db=db,
                                 password=pw,
                                 socket_timeout=timeout)

        if self.config.get('use_settings'):
            logger.info("Configuring Face/Off API cache with REDIS using settings.py")
        else:
            logger.info("Configuring Face/Off API cache with REDIS using JSON settings")

        logger.info("Face/off API cache settings: redis://%s:%s/%s with ttl %s" %
                    (host, port, db, self.ttl))

    def retrieve(self, key):
        try:
            resp = self.redis.get(key)
            if resp is not None:
                return pickle.loads(resp)
            else:
                return None
        except ConnectionError as e:
            logger.warning("Got a timeout error trying to get from Redis API Cache", exc_info=True)
            return None

    def store(self, key, value, ttl=None):
        if ttl is None:
            ttl = self.ttl
        try:
            self.redis.set(key, pickle.dumps(value))
            if ttl > 0:
                self.redis.expire(key, ttl)
        except ConnectionError as e:
            logger.warning("Got a timeout error trying to store into Redis API Cache", exc_info=True)

    def invalidate(self, key):
        try:
            self.redis.delete(key)
        except ConnectionError as e:
            logger.warning("Got a timeout error trying to store invalidate Redis API Cache", exc_info=True)

    def flush(self):
        try:
            self.redis.flushall()
        except ConnectionError as e:
            logger.warning("Got a timeout error trying to flush Redis API Cache", exc_info=True)
