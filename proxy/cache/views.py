import json
import logging
from django.http import HttpResponse

from proxy import general_config
from proxy.cache.stores import UserCacheKeyMaker

from faceoff.decorators import require_signed_request

logger = logging.getLogger(__name__)


@require_signed_request
def invalidate_cache_view(request, application):
    if not application.super_application:
        return HttpResponse(json.dumps({"error": 403, "message": "auth_error"}), content_type="application/json", status=403)
    uncache_type = request.POST.get('uncache_type')
    if uncache_type == 'user_request':
        # user use case
        try:
            user_id = request.POST.get('user_id')
            u = general_config().user_provider.find(id=user_id, force_no_cache=True)
            if u is None:
                return HttpResponse(json.dumps({"error": 404, "message": "user not found with id " + user_id}), content_type="application/json", status=404)
            cache_key = UserCacheKeyMaker(u)
            cache_key.invalidate_with_key()
            return HttpResponse(json.dumps({"message": "OK"}), content_type="application/json", status=200)
        except Exception, e:
            logger.exception("Could not uncache", e)
            return HttpResponse(json.dumps({"error": "500"}), content_type="application/json", status=500)
    else:
        # TODO: Add the normal use case for API Caching (right now we only do user caching)
        pass

    return HttpResponse(json.dumps({"message": "OK"}), content_type="application/json", status=200)
