from proxy import general_config
from proxy.utils import load_class_from_name

__author__ = 'nick'


class HealthCheckRunner(object):
    servers = []
    frequency = 1
    health_checks = []

    def __init__(self, name, healthcheck_implementation, servers, **kwargs):
        self.name = name
        self.health_check_class = load_class_from_name(healthcheck_implementation)
        self.servers = servers
        self.health_checks = []
        self.last_set_of_results = []

        for s in self.servers:
            hc_impl = self.health_check_class()
            s = s.replace("$1", "")
            hc_impl.server = s
            hc_impl.name = name
            self.health_checks.append(hc_impl)

    def add_server(self, server):
        self.servers.append(server)
        server.replace("$1", "")
        self.health_checks.append(self.health_check_class(server))

    def run(self):
        results = []
        are_we_up = False
        for h in self.health_checks:
            check = h.healthcheck()
            if check.passed:
                are_we_up = True
            general_config().health_check.store_result(check)
            results.append(check)

        general_config().health_check.store_service_status(h.name, are_we_up)

        self.last_set_of_results = results

        return results