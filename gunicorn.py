import os

workers = os.environ.get('GUNICORN_WORKERS', 9)
backlog = os.environ.get('GUNICORN_BACKLOG', 512)
timeout = os.environ.get('GUNICORN_WORKER_TIMEOUT', 15)
graceful_timeout = os.environ.get('GUNICORN_WORKER_TIMEOUT', 15)
loglevel = os.environ.get('LOG_LEVEL', "info")
worker_class = "gevent"
preload_app = True
