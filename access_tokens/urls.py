from django.conf.urls import url, patterns

urlpatterns = patterns('',
                       url(r'^authorization/$', 'access_tokens.views.authorization')
                       )
