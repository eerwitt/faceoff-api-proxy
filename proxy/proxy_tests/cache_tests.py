import uuid
from django.test import Client, LiveServerTestCase
from applications.models import Application
from proxy import general_config
from proxy.cache import SimpleInMemoryCacheStore
from proxy.utils import application_hasher

__author__ = 'nick'


class CacheTests(LiveServerTestCase):
    def setUp(self):
        self.client = Client()

    def testCacheStartup(self):
        self.assertIsInstance(general_config().cache.store, SimpleInMemoryCacheStore)

    def testCacheParametersIgnoreRule(self):
        resp = self.client.get("/cache/ignore_parameter", {"foo": "bar", "ignore_this": "test1"})
        self.assertEqual("foo: bar ignore_this: test1", resp.content.decode())
        resp = self.client.get("/cache/ignore_parameter", {"foo": "bat", "ignore_this": "test2"})
        self.assertEqual("foo: bat ignore_this: test2", resp.content.decode())
        resp = self.client.get("/cache/ignore_parameter", {"foo": "bat", "ignore_this": "test3"})
        self.assertEqual("foo: bat ignore_this: test2", resp.content.decode())  # Note it's cached with "test2"

    def testCacheRoundOffParameterRule(self):
        resp = self.client.get("/cache/rounded_parameter", {"rounded": 12.3456789, "not_rounded": 12.3456789})
        resp_content = resp.content.decode()
        resp = self.client.get("/cache/rounded_parameter", {"rounded": 12.3459999, "not_rounded": 12.3456789})
        self.assertEqual(resp_content, resp.content.decode())  # this should be the same result since we cache a rounded response

    def testCache(self):
        resp = self.client.get("/cache/always_random")
        resp2 = self.client.get("/cache/always_random")
        resp3 = self.client.get("/cache/always_random")
        resp4 = self.client.get("/cache/always_random")
        self.assertEqual(resp.content, resp2.content)
        self.assertEqual(resp2.content, resp3.content)
        self.assertEqual(resp3.content, resp4.content)

        # this always returns a different number, so if we get the same thing 4 times we know we're getting a cached
        # result

        # now let's pass in a parameter to bust the cache and see it return something else (to make sure it really is
        # random)
        resp5 = self.client.get("/cache/always_random?cache=buster")
        self.assertNotEqual(resp.content.decode(), resp5.content)

    def testTruncateParameterRuleCache(self):
        resp = self.client.get("/cache/truncate_parameter?name=nick")
        self.assertEqual(resp.content.decode(), "Hello nick")
        resp2 = self.client.get("/cache/truncate_parameter?name=nickvlku")
        self.assertEqual(resp2.content.decode(), "Hello nick")  # we have truncate name to 4 so it should still return nick
        resp3 = self.client.get("/cache/truncate_parameter?name=nickvlku&foo=bar")
        self.assertEqual(resp3.content.decode(), "Hello nickvlku")  # we don't ignore foo so this goes back to the service
        resp4 = self.client.get("/cache/truncate_parameter?name=nick&foo=bar")
        self.assertEqual(resp4.content.decode(), "Hello nickvlku")  # we went to foo=bar&name=nickvlku so this returns nickvlku

    def testInvalidateCacheView(self):
        a = Application()
        a.id = uuid.uuid4().hex
        a.client_secret = uuid.uuid4().hex
        a.super_application = True
        a.name = "Test Super App"
        a.redirect_uri = "/"
        a.created_by = "nick"
        a.save()

        sig = application_hasher(a, "secret")
        post_data = {
            'uncache_type': 'user_request',
            'user_id': 123
        }

        resp = self.client.post("/cache/invalidate?client_id=%s&signature=%s&verify=%s" % (a.id, sig, "secret"), data=post_data)
        self.assertEqual('{"message": "OK"}', resp.content.decode())

