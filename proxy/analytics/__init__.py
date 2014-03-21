from proxy.utils import convert_variable_to_env_setting
import logging
import statsd
__author__ = 'nick'


logger = logging.getLogger(__name__)


class Analytics(object):
    """
    The base Analytics store class.  If you are implementing your own store, you should override these methods.
    """
    def __init__(self, *args, **kwargs):
        """
        This gives you the opportunity to initialize your store.  It is run *once* at Face/Off startup.
        """
        pass

    def increment(self, name, amount=1):
        """
        Increment the current stat.
        """
        pass

    def decrement(self, name, amount=1):
        """
        Decrement the current stat
        """
        pass

    def time(self, name, value):
        """
        How long a certain operation/stat takes logged.
        """
        pass


class NoOpAnalytics(Analytics):
    """
    A NoOp store that only outputs to the log at INFO level.
    """

    def increment(self, name, amount=1):
        super(NoOpAnalytics, self).increment(name, amount)
        logger.info("%s incremented %s" % (name, amount))

    def decrement(self, name, amount=1):
        super(NoOpAnalytics, self).decrement(name, amount)
        logger.info("%s decremented %s" % (name, amount))

    def time(self, name, value):
        super(NoOpAnalytics, self).time(name, value)
        logger.info("%s took %s" % (name, value))


class ChainedAnalytics(Analytics):
    """
    ChainedAnalyticsStore is used internally by Face/Off to chain multiple analytic stores together.  You shouldn't
    have to worry about this if you are writing your own store.
    """

    def __init__(self, analytics=[]):
        self.analytics = analytics

    def add_analytic(self, analytic_class):
        self.analytics.append(analytic_class)

    def increment(self, name, amount=1):
        map(lambda x: x.increment(name, amount), self.analytics)

    def decrement(self, name, amount=1):
        map(lambda x: x.decrement(name, amount), self.analytics)

    def time(self, name, value):
        map(lambda x: x.time(name, value), self.analytics)


class StatsDAnalytics(Analytics):
    """
    A StatsD analytics store implementation
    """
    def __init__(self, *args, **kwargs):
        host = convert_variable_to_env_setting(kwargs.get('host'))
        prefix = convert_variable_to_env_setting(kwargs.get('prefix'))
        try:
            port = int(convert_variable_to_env_setting(kwargs.get('port')))
        except:
            port = None
        logger.info("Attempting to configure StatsDAnalytics with %s:%s:%s" % (host, port, prefix))
        if host is not None and prefix is not None and port is not None and not host.startswith("$") and not prefix.startswith("$"):
            self.client = statsd.StatsClient(host, port, prefix=prefix)
            logger.info("Configured StatsDAnalytics with %s:%s:%s" % (host, port, prefix))
        else:
            self.client = None
            logger.warning("StatsDAnalytics NOT configured, incomplete configuration: %s:%s:%s" % (host, port, prefix))

    def increment(self, name, amount=1):
        if self.client is not None and name is not None:
            name = StatsDAnalytics.convert_to_valid_statsd_name(name)
            self.client.incr(name, amount)

    def decrement(self, name, amount=1):
        if self.client is not None and name is not None:
            name = StatsDAnalytics.convert_to_valid_statsd_name(name)
            self.client.decr(name, amount)

    def time(self, name, value):
        if self.client is not None and name is not None:
            name = StatsDAnalytics.convert_to_valid_statsd_name(name)
            self.client.timing(name, value)

    @staticmethod
    def convert_to_valid_statsd_name(name):
        if name is None:
            return name
        name = name.replace(":", "-").replace("/", "-").replace(" ", "-").replace("@", "-").replace("&", "-").replace("?", "-")
        return name