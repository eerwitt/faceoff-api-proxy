from requests import ConnectionError
import requests
from proxy.utils import parse_basic_auth, convert_variable_to_env_setting


class HealthCheckResponse(object):
    """
    This response from a health check includes detailed messages and an overall state.  All Health Check implementations
    should return an instance of this.
    """
    passed = True
    code = 200
    descriptive_message = ""
    technical_message = ""
    server = ""
    name = ""

    def __init__(self, passed=True, code=200, server="", name=""):
        self.passed = passed
        self.code = code
        self.server = server
        self.name = name

    def __str__(self):
        return "%s:%s:%s:%s:%s" % (self.passed, self.server, self.code, self.descriptive_message, self.technical_message)

    def __repr__(self):
        return "<HealthCheckResponse: %s:%s:%s:%s:%s>" % (self.passed, self.server,  self.code, self.descriptive_message, self.technical_message)


class HealthCheck(object):
    """
    The base HealthCheck object that all health checks should extend.  At minimum, the health check method needs to be
    implemented.
    """
    def __init__(self, server=None, name=None):
        self.server = convert_variable_to_env_setting(server)
        self.name = name


    def healthcheck(self, server=None, **kwargs):
        """
        Override this method when you are writing your own health checks.

        It should return a HealthCheckResponse.
        """
        return HealthCheckResponse()


class HeadCheck(HealthCheck):
    """
    A simple health check that does a HEAD request at the API endpoint.  I
    """
    def healthcheck(self, server=None, **kwargs):

        if server is None:
            server = convert_variable_to_env_setting(self.server)

        try:
            basic_auth_params = parse_basic_auth(server)
            if "login" in basic_auth_params:
                resp = requests.head(server, auth=(basic_auth_params['login'], basic_auth_params['password']))
            else:
                resp = requests.head(server)
            if resp.ok:
                return HealthCheckResponse(server=server, name=self.name)
            else:
                health_check_response = HealthCheckResponse(name=self.name, server=server, code=resp.status_code, passed=False)
                return health_check_response

        except ConnectionError, e:
            health_check_response = HealthCheckResponse(code=999, passed=False)
            health_check_response.descriptive_message = "Connection Refused"
            health_check_response.technical_message = "connection refused"
            health_check_response.server = server
            health_check_response.name = self.name
            return health_check_response
