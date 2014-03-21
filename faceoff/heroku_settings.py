import os
import urlparse
import dj_database_url
from proxy.utils import str2bool

DATABASES = dict()
DATABASES['default'] = dj_database_url.config()

# Honor the 'X-Forwarded-Proto' header for request.is_secure()
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Use either of these 3 Redis Addons or default to localhost
if "REDISCLOUD_URL" in os.environ:
    redis_url = urlparse.urlparse(os.environ.get("REDISCLOUD_URL"))
elif "OPENREDIS_URL" in os.environ:
    redis_url = urlparse.urlparse(os.environ.get("OPENREDIS_URL"))
elif "REDISTOGO_URL" in os.environ:
    redis_url = urlparse.urlparse(os.environ.get("REDISTOGO_URL"))
else:
    redis_url = urlparse.urlparse('redis://localhost:6379/')

HEALTH_CHECK_REDIS = {
    "host": redis_url.hostname,
    "port": redis_url.port,
    "db": 0,
    "password": redis_url.password
}


CACHE_REDIS = {
    "host": redis_url.hostname,
    "port": redis_url.port,
    "db": 1,
    "password": redis_url.password
}


debug_mode = str2bool(os.environ.get('DEBUG', "False"))
DEBUG = debug_mode

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
