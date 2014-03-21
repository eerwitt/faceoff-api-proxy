import json
import os
from django.test import TestCase, RequestFactory
from applications.models import Application
from proxy.authentication import AppKeyProvider, SuperAppKeyProvider, AuthenticationError
from proxy.faceoff import init_global_config


class AuthenticationTestCase(TestCase):
    fixtures = ['users.json', 'applications.json']

    def setUp(self):
        self.factory = RequestFactory()
        self.init_global_config()

    def init_global_config(self):
        proxy_module = os.path.abspath(os.path.join(os.path.dirname(__file__),".."))

        f = open(os.path.join(proxy_module, "tests", "test_config.json"), 'r')
        config = json.loads(f.read())
        f.close()

        init_global_config(config.get('general', {}))

    def testAppKeyProviderValidAppId(self):
        app = Application.objects.filter(super_application=False)
        self.assertEqual(len(app), 1)
        app = app[0]
        self.assertEqual(app.super_application, False)
        client_id = app.id
        r = self.factory.get(path="/", data={"client_id": client_id})

        provider = AppKeyProvider()
        self.assertEqual(provider.authorize(r), app)

    def testAppKeyProviderInvalidAppId(self):
        r = self.factory.get(path="/", data={"client_id": "bad-app-id"})
        provider = AppKeyProvider()
        result = provider.authorize(r)
        self.assertIsInstance(result, AuthenticationError)

        r = self.factory.get(path="/")
        result = provider.authorize(r)
        self.assertIsInstance(result, AuthenticationError)

    def testSuperAppKeyProviderValidSuperAppId(self):
        app = Application.objects.filter(super_application=True)
        self.assertEqual(len(app), 1)
        app = app[0]
        self.assertEqual(app.super_application, True)
        client_id = app.id
        r = self.factory.get(path="/", data={"client_id": client_id})

        provider = SuperAppKeyProvider()
        self.assertEqual(provider.authorize(r), app)

    def testSuperAppKeyProviderInvalidNonSuperAppId(self):
        app = Application.objects.filter(super_application=False)
        self.assertEqual(len(app), 1)
        app = app[0]
        self.assertEqual(app.super_application, False)
        client_id = app.id
        r = self.factory.get(path="/", data={"client_id": client_id})

        provider = SuperAppKeyProvider()
        result = provider.authorize(r)
        self.assertIsInstance(result, AuthenticationError)
