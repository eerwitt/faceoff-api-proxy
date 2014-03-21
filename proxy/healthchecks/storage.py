from django.conf import settings
from redis import StrictRedis, ConnectionError
from proxy.utils import str2bool, convert_variable_to_env_setting

import logging

logger = logging.getLogger(__name__)


class HealthCheckStorage(object):
    """
    You should extend this class if you would like your own health check storage adapter.  All methods here need
    to be implemented.
    """

    def __init__(self, **kwargs):
        """
        This method handles the initialization of your health check store.  It is run once at Face/Off startup.
        """
        pass

    def store_result(self, health_check):
        """
        This stores the result of the health check for the test.  It gets passed in a HealthCheckResponse object.
        """
        pass

    def store(self, name, server, passed):
        """
        This is a simpler store that just sets a boolean representing "passed" for a server at an endpoint.
        """
        pass

    def get_result(self, name, server):
        """
        This method returns the status of the server for an endpoint as a boolean.  True if it is up, False if it is not.
        If the status is unknown, return "Unknown"
        """
        return None

    def get_service_status(self, service):
        """
        This method returns the status of the overall endpoint service. True if it is up, False if it is not.
        If the status is unknown, return "Unknown"
        """
        return False

    def store_service_status(self, service, passed):
        """
        This method returns the status of the overall endpoint service. True if it is up, False if it is not.
        If the status is unknown, return "Unknown"
        """

        pass


class RedisHealthCheckStorage(HealthCheckStorage):
    """
    A Redis health check store implementation for Face/Off.  Settings are either loaded from settings.py or from
    the Face/Off endpoints.json configuration file.
    """

    def __init__(self, **kwargs):

        super(RedisHealthCheckStorage, self).__init__(**kwargs)

        redis_conf = kwargs.get('redis')
        use_settings = False

        if redis_conf.get('use_settings', False):
            use_settings = True
            redis_conf = settings.HEALTH_CHECK_REDIS

        self.redis = StrictRedis(host=convert_variable_to_env_setting(redis_conf.get('host', 'localhost')),
                                 port=redis_conf.get('port'),
                                 db=redis_conf.get('db'),
                                 password=redis_conf.get('password'),
                                 socket_timeout=.3)

        if use_settings:
            logger.info("Configuring Face/Off healthcheck store with REDIS using settings.py")
        else:
            logger.info("Configuring Face/Off healthcheck store with REDIS using JSON settings")

        logger.info("Face/Off with REDIS healthcheck settings: redis://%s:%s/%s" % (redis_conf.get('host'),
                                                                                    redis_conf.get('port'),
                                                                                    redis_conf.get('db')))

    def store_result(self, health_check):
        self.store(health_check.name.lower(), health_check.server.lower(), health_check.passed)

    def store(self, name, server, passed):
        try:
            self.redis.set('%s|%s' % (name.lower(), server.lower()), passed)
        except ConnectionError, ce:
            logger.warning("Got a timeout error trying to store from Redis for %s:%s " % (name, server),  exc_info=True)

    def store_service_status(self, service, passed):
        try:
            self.redis.set(service.lower(), passed)
        except ConnectionError, ce:
            logger.warning("Got a timeout error trying to store_service_status from Redis for %s" % service, exc_info=True)

    def get_result(self, name, server):
        try:
            result = self.redis.get('%s|%s', name.lower(), server.lower())
        except ConnectionError, ce:
            logger.warning("Got a timeout error trying to get_result from Redis for %s:%s " % (name, server), exc_info=True)
            result = None

        if result is None:
            return "Unknown"
        else:
            return str2bool(result.lower())

    def get_service_status(self, service):
        try:
            result = self.redis.get(service.lower())
        except ConnectionError, ce:
            logger.warning("Got a timeout error trying to get_service_status from Redis for %s" % service , exc_info=True)
            result = None

        if result is None:
            return "Unknown"
        else:
            return str2bool(result.lower())