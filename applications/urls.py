from django.conf.urls import url, patterns
from rest_framework.urlpatterns import format_suffix_patterns
from applications import views

urlpatterns = patterns('',
                       url(r'^applications/$',views.ApplicationList.as_view()),
                       url(r'^applications/(?P<pk>[0-9]+)/$', views.ApplicationDetail.as_view()),
)

urlpatterns = format_suffix_patterns(urlpatterns, allowed=['json', 'api'])
