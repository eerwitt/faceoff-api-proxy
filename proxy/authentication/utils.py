import hmac
import binascii
from hashlib import sha1
from collections import OrderedDict
from proxy.authentication.exceptions import AuthenticationError

try:
    from urllib.parse import parse_qsl
    from urllib.parse import urlencode
except:
    from urlparse import parse_qsl
    from urllib import urlencode



def verify_request(request, application):
    signature = request.GET.get('signature', None)
    if signature is None:
        raise AuthenticationError(error_code=401, message="Missing signature")
    query_string = request.META.get('QUERY_STRING')
    query_string = remove_parameter_from_query_string(query_string, 'signature')
    key = "%s&%s" % (application.id, application.client_secret)
    signed_hash = hmac.new(key.encode(), query_string.encode(), sha1)
    signed_signature = binascii.b2a_base64(signed_hash.digest())[:-1]
    signed_signature = signed_signature.decode()
    if signature == signed_signature:
        return application
    else:
        raise AuthenticationError(error_code=401, message="Invalid signature")


def remove_parameter_from_query_string(query_string, parameter_to_remove):
    query = OrderedDict(parse_qsl(query_string))
    query.pop(parameter_to_remove, None)
    return urlencode(query, True)
