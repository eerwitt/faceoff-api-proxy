# These are test views, only used in TESTING environment
from django.conf.urls import patterns, url
from proxy.proxy_tests.views import user_test, app_test, simple_test, round_robin_test, slow_test, status_code, custom_faceoff_headers, get_params_request, cache_ignore_parameter_rule, cache_always_random, cache_truncate_parameter, transformers_cache_headers, transformers_missing_cache_headers, get_array_params_request, cache_rounded_parameter_rule, transformers_test_replace, transformers_request_test


def add_testing_urls(url_patterns):
    url_patterns += patterns('',
                # Simple test
                url(r'^tests/simple', simple_test),
                # Round robin test
                url(r'^tests/round_robin/(?P<server_number>[0-9]+)/$', round_robin_test),
                # Auth Tests
                url(r'^tests/test_user/', user_test),
                url(r'^tests/test_app/', app_test),
                # Slow response test
                url(r'^tests/slow/', slow_test),
                # Passing appropriate server status codes test
                url(r'^tests/status_code/(?P<status_code>[0-9]+)/$', status_code),
                # Passing appropriate Face/Off headers
                url(r'^tests/faceoff_headers', custom_faceoff_headers),
                url(r'^tests/get_param.*', get_params_request),
                url(r'^tests/get_array_param.*', get_array_params_request),
                url(r'^tests/cache/ignore_parameter.*', cache_ignore_parameter_rule),
                url(r'^tests/cache/always_random.*', cache_always_random),
                url(r'^tests/cache/truncate_parameter.*', cache_truncate_parameter),
                url(r'^tests/cache/rounded_parameter.*', cache_rounded_parameter_rule),
                url(r'^tests/transformers/cache_headers.*', transformers_cache_headers),
                url(r'^tests/transformers/no_cache_headers.*', transformers_missing_cache_headers),
                url(r'^tests/transformers/replace_response.*', transformers_test_replace),
                url(r'^tests/transformers/request_test.*', transformers_request_test)

    )
    return url_patterns