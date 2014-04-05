import hmac
import random
import string
import urllib

try:
    from urllib.parse import urlparse
except:
    import urlparse

import binascii
from hashlib import sha1
from django.test import TestCase
from django.test.client import RequestFactory
from applications.models import Application
from proxy.authentication.utils import verify_request
from proxy.authentication.exceptions import AuthenticationError
from proxy.utils import load_class_from_name, get_all_http_request_headers, get_content_request_headers_only, application_hasher
from proxy.proxy_tests import RequestMock

__author__ = 'nick'



class BasicTestClass(object):
    test_class = "foo"


class UtilsTestCase(TestCase):

    def testLoadClassFromName(self):
        clazz = load_class_from_name("proxy.tests.BasicTestClass")
        self.assertEqual(clazz.__name__, "BasicTestClass")
        impl = clazz()
        self.assertEqual(impl.test_class, "foo")
        impl.test_class = "bar"
        self.assertEqual(impl.test_class, "bar")

    def testLoadBadClassFromName(self):
        self.assertRaises(ImportError, load_class_from_name, ("proxy.fakepackage.TotallyFakeClassName"))
        self.assertRaises(AttributeError, load_class_from_name, ("proxy.tests.TotallyFakeClassName"))

    def testGetAllHttpRequestHeaders(self):
        r = RequestMock().request(HTTP_ACCEPT="application/json", CONTENT_TYPE="text/html")
        proxied_header = get_all_http_request_headers(r)
        self.assertIn("ACCEPT", proxied_header)
        self.assertIn("CONTENT-TYPE", proxied_header)
        self.assertNotIn("HTTP_ACCEPT", proxied_header)
        self.assertEqual(proxied_header.get('ACCEPT'), "application/json")
        self.assertEqual(proxied_header.get('CONTENT-TYPE'), "text/html")
        self.assertNotIn("wsgi.version", proxied_header)

        custom_headers = {"X-FOO": "BAR", "X-BAZ": "BAT"}

        proxied_headers_with_custom = get_all_http_request_headers(r, custom_headers=custom_headers)
        self.assertIn("ACCEPT", proxied_header)
        self.assertIn("CONTENT-TYPE", proxied_header)
        self.assertNotIn("HTTP_ACCEPT", proxied_header)
        self.assertEqual(proxied_header.get('ACCEPT'), "application/json")
        self.assertEqual(proxied_header.get('CONTENT-TYPE'), "text/html")

        self.assertIn("X-FOO", proxied_headers_with_custom)
        self.assertIn("X-BAZ", proxied_headers_with_custom)
        self.assertEqual(proxied_headers_with_custom.get('X-FOO'), "BAR")
        self.assertNotIn("wsgi.version", proxied_headers_with_custom)

    def testGetContentHeadersOnly(self):
        r = RequestMock().request(HTTP_ACCEPT="application/json", CONTENT_TYPE="text/html")

        content_header = get_content_request_headers_only(r)
        self.assertIn("CONTENT-TYPE", content_header)
        self.assertNotIn("CONTENT_TYPE", content_header)
        self.assertNotIn("ACCEPT", content_header)
        self.assertEqual(content_header.get('CONTENT-TYPE'), "text/html")

        custom_headers = {"X-FOO": "BAR", "X-BAZ": "BAT"}
        custom_content_header = get_content_request_headers_only(r, custom_headers=custom_headers)
        self.assertIn("CONTENT-TYPE", custom_content_header)
        self.assertNotIn("CONTENT_TYPE", custom_content_header)
        self.assertNotIn("ACCEPT", custom_content_header)
        self.assertEqual(custom_content_header.get('CONTENT-TYPE'), "text/html")
        self.assertIn("X-FOO", custom_content_header)
        self.assertIn("X-BAZ", custom_content_header)
        self.assertEqual(custom_content_header.get('X-FOO'), "BAR")

    def testApplicationHasher(self):
        a = Application()
        a.id = "abc"
        a.client_secret = "def"
        signature = application_hasher(a, "signature")
        self.assertEqual("11b2d248b0f026bf61d02dbc4d0a6edb", signature)

    def testCorrectlySignedAuthVerifySignature(self):
        a = Application()
        a.id = "test_id"
        a.client_secret = "test_secret"
        parameters = {
            "test_param_1": random.randint(0,100),
            "test_param_2": ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(10))
        }

        parameters['signature'] = self.__build_signature(a.id, a.client_secret, parameters)

        r = RequestFactory().get("/test", parameters)

        self.assertEqual(a, verify_request(r, a))  # this is a valid request so the app should come back

    def testIncorrectlySignedAuthVerifySignature(self):
        a = Application()
        a.id = "test_id"
        a.client_secret = "test_secret"
        parameters = {
            "test_param_1": random.randint(0,100),
            "test_param_2": ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(10))
        }

        parameters['signature'] = self.__build_signature(a.id, "bad_secret", parameters)

        r = RequestFactory().get("/test", parameters)

        # this throws an error since it isn't a valid signature
        self.assertRaises(AuthenticationError, lambda: verify_request(r, a))

    def __build_signature(self, key, secret, parameters):
        # let's make the signature manually the way we expect
        query_string = urllib.urlencode(parameters)
        key = "%s&%s" % (key, secret)
        signed_hash = hmac.new(key, query_string, sha1)
        signed_signature = binascii.b2a_base64(signed_hash.digest())[:-1]
        return signed_signature
