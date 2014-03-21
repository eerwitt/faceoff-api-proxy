import logging
from access_tokens.models import AccessToken
from proxy import general_config
from proxy.authentication import AuthenticationProvider
from proxy.authentication.appkey_providers import AuthenticationError, \
    SuperAppKeyProvider
import json

logger = logging.getLogger(__name__)


def get_access_token_headers(token):

    user = general_config().user_provider.find(id=token.user)

    custom_headers = dict()
    custom_headers['X-FACEOFF-AUTH'] = "Access-Token"
    custom_headers['X-FACEOFF-AUTH-USER-ID'] = token.user
    custom_headers['X-FACEOFF-AUTH-APP-ID'] = token.application.id

    custom_headers['X-FACEOFF-AUTH-APP'] = token.application.to_json()
    custom_headers['X-FACEOFF-AUTH-USER'] = json.dumps(user)
    return custom_headers


class AccessTokenOrSuperUserAuthProvider(AuthenticationProvider):

    def authorize(self, request, *args, **kwargs):
        super_app_key_provider = SuperAppKeyProvider()
        auth_app_object = super_app_key_provider.authorize(request)
        try:
            if auth_app_object.super_application:
                return auth_app_object
        except:
            # its not a super app, try access_token stuff
            pass
        access_token_str = request.REQUEST.get('access_token', None)
        if access_token_str is None:
            return AuthenticationError(error_code=403, message="Missing access_token")
        try:
            token = AccessToken.objects.get(token=access_token_str)
            if token.is_active:
                return token
            else:
                return AuthenticationError(error_code=403, message="Invalid access_token")
        except AccessToken.DoesNotExist:
            return AuthenticationError(error_code=403, message="Invalid access_token")

    def get_headers(self, auth_object):
        if isinstance(auth_object, AccessToken):
            return get_access_token_headers(auth_object)
        try:
            if auth_object.super_application:
                super_app_key_provider = SuperAppKeyProvider()
                return super_app_key_provider.get_headers(auth_object)
        except:
            # its not a super app, try access_token stuff
            pass
        return {}


class AccessTokenAuthProvider(AuthenticationProvider):

    def authorize(self, request, *args, **kwargs):
        access_token_str = request.REQUEST.get('access_token', None)
        if access_token_str is None:
            return AuthenticationError(error_code=403, message="Missing access_token")
        try:
            token = AccessToken.objects.get(token=access_token_str)
            if token.is_active:
                return token
            else:
                return AuthenticationError(error_code=403, message="Invalid access_token")
        except AccessToken.DoesNotExist:
            return AuthenticationError(error_code=403, message="Invalid access_token")

    def get_headers(self, token):
        if isinstance(token, AccessToken):
            return get_access_token_headers(token)
