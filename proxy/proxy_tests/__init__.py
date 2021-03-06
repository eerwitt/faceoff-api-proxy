__author__ = 'nick'

from django.core.handlers.base import BaseHandler
from django.test import RequestFactory


class RequestMock(RequestFactory):
    def request(self, **request):
        "Construct a generic request object."
        request = RequestFactory.request(self, **request)
        handler = BaseHandler()
        handler.load_middleware()
        for middleware_method in handler._request_middleware:
            if middleware_method(request):
                raise Exception("Couldn't create request mock object - "
                                "request middleware returned a response")
        return request


from .rotation_tests import *
from .utils_tests import *
from .proxy_tests import *
from ..authentication.tests import *
from .cache_tests import *
from .analytics_tests import *