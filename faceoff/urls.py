import os

from django.conf.urls import patterns, include, url
from django.conf import settings
from access_tokens.views import authorization
from proxy.faceoff import add_proxies
from proxy.views import index

urlpatterns = patterns('',
                       url(r'^$', index),
                       url(r'^', include('applications.urls')),
                       url(r'^tokens', authorization)
)


# Default login/logout views
urlpatterns += patterns('',
                        url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework'))
)

api_cfg = os.path.abspath(os.path.join(os.path.dirname(__file__), settings.API_CONF_FILE))

urlpatterns += add_proxies(api_cfg)

# test views
if settings.TESTING:
    from proxy.proxy_tests.urls import add_testing_urls
    urlpatterns += add_testing_urls(urlpatterns)
