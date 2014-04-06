from time import sleep
import uuid
import json
from django.test import LiveServerTestCase
from django.test.client import Client
from applications import application_cache
from applications.models import Application
from proxy import general_config
from proxy.authentication.user_finders import MockUserFinder

__author__ = 'nick'


class ProxyTests(LiveServerTestCase):

    def setUp(self):
        self.client = Client()
        self.user_finder = MockUserFinder()
        self.user = self.user_finder.find(id=12)
        a = Application()
        a.id = uuid.uuid4().hex
        a.name = "Test Application"
        a.created_by = self.user['id']
        a.client_secret = uuid.uuid4().hex
        a.redirect_uri = "http://example.com/redirect"
        a.save()
        self.application = a

    def testSimple(self):
        response = self.client.get("/simple")
        self.assertEqual("Success!", response.content.decode('utf-8'))
        self.assertEqual(200, response.status_code)

    def testStatusCodesPassedCorrectly(self):
        response = self.client.get("/status_code/200")
        self.assertEqual(200, response.status_code)

        response = self.client.get("/status_code/500")
        self.assertEqual(500, response.status_code)

        response = self.client.get("/status_code/403")
        self.assertEqual(403, response.status_code)

        response = self.client.get("/status_code/404")
        self.assertEqual(404, response.status_code)

        response = self.client.get("/status_code/418")
        self.assertEqual(418, response.status_code)

    def testFaceoffCustomHeaders(self):
        response = self.client.get("/custom_headers")
        self.assertIn(b"HTTP_X_FORWARDED_HOST", response.content)
        self.assertEqual("HTTP_X_FORWARDED_HOST:%s" % general_config().domain_name, response.content.decode('utf-8'))

    def testAppAuthSuccess(self):
        response = self.client.get("/app", {"client_id": self.application.id})
        self.assertEqual(response.content.decode('utf-8'), "Test Application")

    def testAppAuthFailure(self):
        response = self.client.get("/app", {"client_id": "bad app id"})
        result = json.loads(response.content.decode('utf-8'))
        self.assertEqual(result['error'], 401)
        self.assertEqual(result['message'], "Invalid client_id")
        self.assertEqual(response.status_code, 401)

    def testRoundRobin(self):
        responses = [self.client.get("/round_robin").content.decode('utf-8'),
                     self.client.get("/round_robin").content.decode('utf-8'),
                     self.client.get("/round_robin").content.decode('utf-8'),
                     self.client.get("/round_robin").content.decode('utf-8')]
        self.assertEqual(['proxy1', 'proxy2', 'proxy3', 'proxy1'], responses)

    def testDownedEndpoint(self):
        response = self.client.get("/down_endpoint")
        result = json.loads(response.content.decode('utf-8'))
        self.assertEqual(result['error'], '1')
        self.assertEqual(result['message'], "connection_error")
        self.assertEqual(response.status_code, 502)

    # This test will throw "Django [Errno 32]" Broken pipe errors because Face/Off
    # will break the connection to the other side for taking too long
    def testTimedOutEndpoint(self):
        response = self.client.get("/slow_response")
        result = json.loads(response.content.decode('utf-8'))
        self.assertEqual(result['error'], '408')
        self.assertEqual(result['message'], "service_time_out")
        self.assertEqual(response.status_code, 408)

    def testOneUpRestDown(self):
        response = [self.client.get("/simple_one_works").status_code,
                    self.client.get("/simple_one_works").status_code,
                    self.client.get("/simple_one_works").status_code]

        self.assertEqual([200, 200, 200], response)

    def testGetParamPassedSuccessfully(self):
        response = self.client.get("/get_param?test_get_param=success")
        self.assertEqual(response.content.decode('utf-8'), "test_get_param:success")

    def testGetParamPassedSuccessfullyOnAPost(self):
        response = self.client.post("/get_param?test_get_param=success")
        self.assertEqual(response.content.decode('utf-8'), "test_get_param:success")

    def testGetArrayParamPassedSuccessfully(self):
        response = self.client.get("/get_array_params?test_get_param=success&test_get_param=also_works")
        self.assertEqual(response.content.decode('utf-8'), "test_get_param:success,also_works")

    def testGetArrayParamPassedSuccessfullyOnAPost(self):
        response = self.client.post("/get_array_params?test_get_param=success&test_get_param=also_works")
        self.assertEqual(response.content.decode('utf-8'), "test_get_param:success,also_works")

    def testCacheHeaderAddition(self):
        response = self.client.get("/transformers/response_add_cache_headers_missing")
        self.assertIn('cache-control', response)
        self.assertIn('pragma', response)
        self.assertIn('expires', response)
        self.assertEqual('no-cache, must-revalidate', response['cache-control'])
        self.assertEqual('no-cache', response['pragma'])
        self.assertEqual('Sat, 14 June 1980 05:00:00 GMT', response['expires'])
        self.assertEqual(200, response.status_code)

    def testCacheHeaderNotAdded(self):
        response = self.client.get("/transformers/response_add_cache_headers_already_there")
        self.assertIn('cache-control', response)
        self.assertNotIn('pragma', response)
        self.assertNotIn('expires', response)
        self.assertEqual('max-age=290304000, public', response['cache-control'])

    def testTransformerParameters(self):
        response = self.client.get('/transformers/response_test_parameter_in_transformer')
        self.assertEqual(response.content.decode('utf-8'), "Hello, Foo")

    def testRequestTransformer(self):
        response = self.client.get('/transformers/request_transformer_test')
        self.assertEqual(response.content.decode('utf-8'), 'foo param value is: bar')

    def testApplicationCache(self):
        a = Application()
        a.name = "Test App"
        a.client_secret = "abc"
        a.id = "test-id"
        a.created_by = "Nick"
        a.save()

        application_cache().load_from_db()
        self.assertIn(a, application_cache().all())

    # For these tests valid IPs are 5.5.5.5 and 1.2.3.4
    def testIPWhiteListRequestTransformerWithValidIP(self):
        response = self.client.get('/transformers/ip_white_list', REMOTE_ADDR='5.5.5.5')
        self.assertEqual(response.content.decode('utf-8'), "Success!")

    def testIPWhiteListRequestTransformerWithInvalidIP(self):
        response = self.client.get('/transformers/ip_white_list', REMOTE_ADDR='0.0.0.0')
        result = json.loads(response.content.decode('utf-8'))
        self.assertEqual(result['error'], 403)
        self.assertEqual(result['message'], "Some conditions are forbidden")

    def testIPWhiteListRequestTransformerWithValidProxiedIP(self):
        response = self.client.get('/transformers/ip_white_list', HTTP_X_FORWARDED_FOR='5.5.5.5')
        self.assertEqual(response.content.decode('utf-8'), "Success!")

    def testIPWhiteListRequestTransformerWithInvalidProxiedIP(self):
        response = self.client.get('/transformers/ip_white_list', HTTP_X_FORWARDED_FOR='0.0.0.0')
        result = json.loads(response.content.decode('utf-8'))
        self.assertEqual(result['error'], 403)
        self.assertEqual(result['message'], "Some conditions are forbidden")

    def testIPWhiteListRequestTransformerWithValidProxiedIPAtEndOfChain(self):
        response = self.client.get('/transformers/ip_white_list', HTTP_X_FORWARDED_FOR='0.0.0.0,9.9.9.9,5.5.5.5')
        self.assertEqual(response.content.decode('utf-8'), "Success!")

    def testIPWhiteListRequestTransformerWithValidProxiedIPNotAtEndOfChain(self):
        response = self.client.get('/transformers/ip_white_list', HTTP_X_FORWARDED_FOR='0.0.0.0,5.5.5.5,9.9.9.9')
        result = json.loads(response.content.decode('utf-8'))
        self.assertEqual(result['error'], 403)
        self.assertEqual(result['message'], "Some conditions are forbidden")

    def testIPWhiteListRequestTransformerWithValidIPButInvalidProxiedIP(self):
        response = self.client.get('/transformers/ip_white_list', HTTP_X_FORWARDED_FOR='0.0.0.0', REMOTE_ADDR='5.5.5.5')
        result = json.loads(response.content.decode('utf-8'))
        self.assertEqual(result['error'], 403)
        self.assertEqual(result['message'], "Some conditions are forbidden")

    def testIPWhiteListRequestTransformerWithMalformedForwardedFor(self):
        response = self.client.get('/transformers/ip_white_list', HTTP_X_FORWARDED_FOR='adfsa88134hFk.,!@$')
        result = json.loads(response.content.decode('utf-8'))
        self.assertEqual(result['error'], 403)
        self.assertEqual(result['message'], "Some conditions are forbidden")

    def testIPWhiteListRequestTransformerWithMalformedRemoteAddr(self):
        response = self.client.get('/transformers/ip_white_list', REMOTE_ADDR="JFDAJFSJKSF")
        result = json.loads(response.content.decode('utf-8'))
        self.assertEqual(result['error'], 403)
        self.assertEqual(result['message'], "Some conditions are forbidden")

    def testIPWhiteListRequestTransformerWithNoRemoteAddr(self):
        response = self.client.get('/transformers/ip_white_list', REMOTE_ADDR=None)
        result = json.loads(response.content.decode('utf-8'))
        self.assertEqual(result['error'], 403)
        self.assertEqual(result['message'], "Some conditions are forbidden")


    @classmethod
    def tearDownClass(cls):
        # some tests are long lived (intentionally, for time out tests) so we want to give the live server a few seconds
        # before we turn it off
        sleep(2)