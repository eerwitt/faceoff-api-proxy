from time import sleep
from termcolor import colored
from proxy import general_config
from proxy.healthchecks import HealthCheckRunner

__author__ = 'nick'

import json
import logging
from proxy.faceoff import init_global_config
from django.core.management.base import BaseCommand

logger = logging.getLogger(__name__)

#TODO Health Checks should use the same logic to get CFG file as the app with an override for file


class Command(BaseCommand):
    args = 'cfg_file <frequency>'
    help = "Start the health check process for the config file specified"

    def handle(self, *args, **options):
        if len(args) < 1:
            print("Please specify a configuration file")
            exit()
        cfg_file = args[0]
        try:
            frequency = int(args[1])
        except:
            frequency = 60

        logger.info("Starting Face/Off Healthcheck for " + cfg_file)
        f = open(cfg_file, 'r')
        config = json.loads(f.read())
        f.close()

        health_check_runners = []

        init_global_config(config.get('general',{}))
        for endpoint_key in config.get('endpoints', {}):
            endpoint = config.get('endpoints').get(endpoint_key)
            name = endpoint.get('name')
            server_cfg = endpoint.get('server')
            servers = server_cfg.get('servers')
            health_check_function = server_cfg.get('health_check', {}).get('function', "proxy.healthchecks.checks.HeadCheck")

            health_check_runners.append(HealthCheckRunner(name, health_check_function, servers))

            logger.info("Health Check for %s, servers: %s, function: %s" % ( name, servers, health_check_function))

        while True:
            for r in health_check_runners:
                results = r.run()
                pretty_result = []
                server_statuses = []
                for result in results:
                    server_statuses.append(result.passed)
                    pretty_result.append("%s:%s:%s" % (r.name, result.server, result.passed))

                if False in server_statuses:
                    if True in server_statuses:
                        logger.warning(colored("SERVICE IS PARTIALLY UP", "yellow") + "  Result: %s: %s" % (r.name, pretty_result))
                    else:
                        logger.warning(colored("SERVICE IS DOWN", "red") + " Healthcheck Result: %s: %s " % (r.name, pretty_result))
                else:
                    logger.info(colored("SERVICE IS UP", "green") + " Healthcheck Result: %s: %s " % (r.name, pretty_result))


            sleep(frequency)



