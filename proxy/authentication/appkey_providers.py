import logging
from applications import application_cache
from proxy import general_config
from proxy.authentication.utils import verify_request
from proxy.authentication.exceptions import AuthenticationError

logger = logging.getLogger(__name__)


class AuthenticationProvider(object):
    def authorize(self, request, *args, **kwargs):
        return False

    def get_headers(self, request, *args, **kwargs):
        custom_headers = dict()
        custom_headers['X-FACEOFF-AUTH'] = "PassThrough"
        return custom_headers


# these authproviders *RETURN* an exception - they should raise it instead -- whyy did i do it like this?????
class AppKeyProvider(AuthenticationProvider):
    def authorize(self, request, *args, **kwargs):
        cfg = general_config()
        application_object = cfg.application_object
        if application_object is None:
            logger.error("You are trying to use the proxy.authentication.AppKeyProvider with no application_object set!")
            return AuthenticationError(error_code=500, message="Internal error")
        else:
            try:
                obj = application_cache().get(request.REQUEST.get('client_id', "MISSING-CLIENT-ID-xyz"))
                if obj is None:
                    return AuthenticationError(error_code=401, message="Invalid client_id")
                return obj
            except Exception, e:
                return AuthenticationError(error_code=401, message="Invalid client_id")
            return AuthenticationError(error_code=401, message="Invalid client_id")

    def get_headers(self, auth_object):
        custom_headers = dict()
        custom_headers['X-FACEOFF-AUTH'] = "appkey"
        custom_headers['X-FACEOFF-AUTH-ID'] = auth_object.id
        custom_headers['X-FACEOFF-AUTH-JSON'] = auth_object.to_json()
        custom_headers['X-FACEOFF-AUTH-APP-ID'] = auth_object.id
        return custom_headers


class SuperAppKeyProvider(AppKeyProvider):

    def authorize(self, request, *args, **kwargs):
        obj = super(SuperAppKeyProvider, self).authorize(request, *args, **kwargs)
        if isinstance(obj, AuthenticationError):
            return obj

        if obj.super_application:
            return obj
        else:
            return AuthenticationError(error_code=403, message="Invalid client_id")

    def get_headers(self, auth_object):
        custom_headers = super(SuperAppKeyProvider, self).get_headers(auth_object)
        custom_headers['X-FACEOFF-AUTH'] = "superappkey"
        custom_headers['X-FACEOFF-AUTH-APP-ID'] = auth_object.id
        return custom_headers


class SignedAppRequestProvider(AppKeyProvider):

    def authorize(self, request, *args, **kwargs):
        try:
            obj = super(SuperAppKeyProvider, self).authorize(request, *args, **kwargs)
            if isinstance(obj, AuthenticationError):
                return obj
            obj = verify_request(request, "signature")
            return obj
        except AuthenticationError, ae:
            return ae
        except Exception, e:
            return AuthenticationError(error_code=500, message="General error")

    def get_headers(self, auth_object):
        custom_headers = dict()
        custom_headers['X-FACEOFF-AUTH'] = "signed_app_request"
        custom_headers['X-FACEOFF-AUTH-ID'] = auth_object.id
        custom_headers['X-FACEOFF-AUTH-JSON'] = auth_object.to_json()
        custom_headers['X-FACEOFF-AUTH-APP-ID'] = auth_object.id
        return custom_headers
