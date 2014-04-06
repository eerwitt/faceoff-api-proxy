import json
from random import random
from time import sleep
from django.http import HttpResponse


def user_test(request):
    auth_user = request.META.get("HTTP_X_FACEOFF_AUTH_USER")
    try:
        auth_obj = json.loads(auth_user)
        return HttpResponse("Hello %s" % auth_obj.get('full-name'))
    except:
        return HttpResponse("No User")


def return_status_code(request, status_code=200):
    resp = dict()
    resp['test'] = 'status_code'
    resp['status_code'] = int(status_code)
    return HttpResponse(json.dumps(resp), status=int(status_code), content_type="application/json")


def app_test(request):
    auth_user = request.META.get("HTTP_X_FACEOFF_AUTH_JSON")
    try:
        auth_obj = json.loads(auth_user)
        return HttpResponse(auth_obj['name'])
    except:
        return HttpResponse("No App")


def simple_test(request):
    return HttpResponse("Success!")


def round_robin_test(request, server_number):
    return HttpResponse("proxy%s" % server_number)


def slow_test(request):
    sleep(5)
    return HttpResponse("Slept for %s seconds", 5)


def status_code(request, status_code):
    return HttpResponse(status_code, status=int(status_code))


def custom_faceoff_headers(request):
    return HttpResponse("HTTP_X_FORWARDED_HOST:%s" % request.META.get("HTTP_X_FORWARDED_HOST"))


def get_params_request(request):
    if "test_get_param" in request.GET:
        return HttpResponse("test_get_param:%s" % request.GET.get("test_get_param"))
    else:
        return HttpResponse("NO test_get_param found")


def get_array_params_request(request):
    if "test_get_param" in request.GET:
        return HttpResponse("test_get_param:%s" % ",".join(request.GET.getlist("test_get_param")))
    else:
        return HttpResponse("NO test_get_param found")


def cache_ignore_parameter_rule(request):
    return HttpResponse("foo: %s ignore_this: %s" % (request.GET.get('foo', None), request.GET.get("ignore_this", None)))


def cache_rounded_parameter_rule(request):
    return HttpResponse("rounded: %s not_rounded: %s random_value %s" % (request.GET.get('rounded', None), request.GET.get("not_rounded", None), random()))


def cache_always_random(request):
    return HttpResponse(random())


def cache_truncate_parameter(request):
    return HttpResponse("Hello %s" % request.GET.get("name", None))


def transformers_cache_headers(request):
    resp = HttpResponse("Cache headers already set")
    resp['cache-control'] = "max-age=290304000, public"
    return resp


def transformers_missing_cache_headers(request):
    return HttpResponse("No cache headers")


def transformers_test_replace(request):
    return HttpResponse("Hello, nick")


def transformers_request_test(request):
    return HttpResponse("foo param value is: %s" % request.GET.get('foo'))