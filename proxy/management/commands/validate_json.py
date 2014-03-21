import os
import logging
import sys

from termcolor import colored
from optparse import make_option

from django.conf import settings
from django.core.management.base import BaseCommand

from faceoff import __file__ as cfg_dir
from proxy.faceoff import add_proxies_from_data, load_config
from proxy import general_config


__author__ = 'nick'


logger = logging.getLogger(__name__)


class Command(BaseCommand):

    option_list = BaseCommand.option_list + (
        make_option('--cfg_file',
            dest='cfg_file',
            default=None,
            help='Config file to validate (default is configured one)'),
        )

    help = "Validates JSON for the configured endpoints file (or overwritten by param)"

    def handle(self, *args, **options):
        cfg_file_name = options['cfg_file']
        if cfg_file_name is None:
            cfg_file_name = settings.API_CONF_FILE

        cfg_file = os.path.abspath(os.path.join(os.path.dirname(cfg_dir), cfg_file_name))

        print("Validating configuration file: %s" % cfg_file)

        try:
            config = load_config(cfg_file)
        except IOError, e:
            print colored("IOError: Could not open file for reading %s" % e, "red", None, ['bold'])
            sys.exit(-1)
        except Exception, e:
            print colored("File doesn't seem to valid JSON %s" % e, "red", None, ['bold'])
            sys.exit(-1)

        print colored("File Exists", "green")
        print colored("File is valid JSON", "green")

        add_proxies_from_data(config)

        if general_config().errors_during_init:
            print colored("JSON file has errors during init", "red", None, ['bold'])
            sys.exit(-1)
        else:
            print colored("JSON file is verified correct", "green", None, ['bold'])
            sys.exit(0)