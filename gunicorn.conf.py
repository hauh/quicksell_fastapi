"""Gunicorn configuration file."""

import multiprocessing

from uvicorn.workers import UvicornWorker

UvicornWorker.CONFIG_KWARGS['root_path'] = '/api'

bind = '0.0.0.0:8000'
backlog = 2048
worker_class = 'uvicorn.workers.UvicornWorker'
workers = multiprocessing.cpu_count() * 2 + 1
worker_connections = 1000
timeout = 30
keepalive = 3
accesslog = '-'
