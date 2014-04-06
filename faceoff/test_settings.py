import os

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',	      # Face/Off has very limited db requirements (only needed for auth)
        'NAME': 'faceoff_dev',						  # so to make tests quicker, we're gonna use sqlite here.
        'USER': '',									  # Leave blank per http://postgresapp.com/documentation (Python section)
        'PASSWORD': '',								  # Same as above
        'HOST': '',								      # Leave empty for domain sockets or '127.0.0.1' for localhost through TCP.
        'PORT': '',									  # Set to empty string for default.
    }
}

# specify the TEST configuration file, that maps test views for our tests.

API_CONF_FILE = "../proxy/proxy_tests/test_config.json"
DEBUG = True
FIXTURE_DIRS = [os.path.join(os.path.dirname(os.path.abspath(__file__)), '../proxy/proxy_tests/fixtures'),]


SECRET_KEY = "TEST-SECRET-KEY"

HEALTH_CHECK_REDIS = {
    "host": "localhost",
    "port": 6379,
    "db": 0
}

CACHE_REDIS = {
    "host": "localhost",
    "port": 6379,
    "db": 1
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
        },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'standard'
        },
        },
    'loggers': {
        'proxy': {
            'level': 'INFO',
            'handlers': ['console'],
            'propagate': True
        }
    }
}
