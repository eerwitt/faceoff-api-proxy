import json
from django.http import HttpResponse
from applications import application_cache
from proxy.utils import application_hasher


def require_parameters(parameters):
    def require_me_yo(f):
        def wrap(request, *args, **kwargs):
            for parameter in parameters:
                if parameter not in request.REQUEST:
                    return HttpResponse("Required Parameter Missing", status=422)
            
            return f(request, *args, **kwargs)
        wrap.__doc__ = f.__doc__
        wrap.__name__ = f.__name__
        return wrap
    return require_me_yo


def require_signed_request(f):
    def wrap(request, *args, **kwargs):
        client_id = request.GET.get('client_id', None)
        signature = request.GET.get('signature', None)
        verify = request.GET.get('verify', None)
        if client_id is None or signature is None or verify is None:
            return HttpResponse(json.dumps({"error": "422", "message": "required parameter missing"}), content_type="application/json", status=422)
        try:
            app = application_cache().get(client_id)
        except:
            return HttpResponse(json.dumps({"error": "4031", "message": "auth failure"}), content_type="application/json", status=403)

        verified_signature = application_hasher(app, verify)
        if verified_signature != signature:
            return HttpResponse(json.dumps({"error": "4032", "message": "auth failure"}), content_type="application/json", status=403)

        return f(request, app, *args, **kwargs)

    return wrap