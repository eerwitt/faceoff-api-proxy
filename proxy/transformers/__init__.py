from proxy.transformers.exceptions import TransformerException
from proxy.utils import get_client_ip

__author__ = 'nick'


class Transformer(object):

    def __init__(self, **kwargs):
        self.params = kwargs


class RequestTransformer(Transformer):

    """
    This tranformer runs on the client request and returns a modified request that is then sent to the endpoint
    """
    def transform_request(self, request):
        """
        Implement the transformer here.  The request is passed in and a similar request should be returned.
        """
        return request


class ResponseTransformer(Transformer):

    def __init__(self, **kwargs):
        self.params = kwargs

    """
    This tranformer runs on the backend response and returns a modified response that is then sent back to the client
    """
    def transform_response(self, response):
        """
        Implement the transformer here.  The response is passed in and a similar response should be returned.
        """
        return response


class JSONtoXMLTransformer(RequestTransformer, ResponseTransformer):
    """
    TODO: A currently *unimplemented* transformer.  This is on the TODO list.
    """
    def transform_request(self, request):
        return request

    def transform_response(self, response):
        return response


class AddCacheHeadersIfMissing(ResponseTransformer):

    def transform_response(self, response):
        # making sure we check case insensitive headers 'cause the spec is case insensitive
        # also if you touch the response directly (instead of _headers), it breaks it.
        case_insensitive_keys = set(k.lower() for k in response._headers)
        
        if 'cache-control' not in case_insensitive_keys and 'pragma' not in case_insensitive_keys and 'expires' not in case_insensitive_keys:
            response['cache-control'] = 'no-cache, must-revalidate'
            response['pragma'] = 'no-cache'
            response['expires'] = 'Sat, 14 June 1980 05:00:00 GMT'  # sometime in the past

        return response


class IPWhiteListRequestTransformer(RequestTransformer):

    def transform_request(self, request):
        ip_address = get_client_ip(request)
        if ip_address not in self.params.get('ip_whitelist', []):
            raise TransformerException(error_code=403, message="Some conditions are forbidden")
        else:
            return request
