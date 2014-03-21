from django.test import TestCase
from proxy.analytics import StatsDAnalytics

__author__ = 'nick'


class AnalyticsTests(TestCase):

    def testStatsdNameSafety(self):
        invalid_name = "https://www.vlku.com/test?a=123&b=456"
        fixed_name = StatsDAnalytics.convert_to_valid_statsd_name(invalid_name)
        self.assertEqual(fixed_name, "https---www.vlku.com-test-a=123-b=456")
        self.assertEqual(None, StatsDAnalytics.convert_to_valid_statsd_name(None))
        self.assertEqual("foobar", StatsDAnalytics.convert_to_valid_statsd_name("foobar"))
