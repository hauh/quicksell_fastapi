"""Gunicorn configuration file."""

import json
import multiprocessing

from quicksell.database import Database
from quicksell.models import Category

bind = '0.0.0.0:8000'
backlog = 2048
worker_class = 'uvicorn.workers.UvicornWorker'
workers = multiprocessing.cpu_count() * 2 + 1
worker_connections = 1000
timeout = 30
keepalive = 3
accesslog = '-'


def on_starting(_):
	Database.connect()
	Database.migrate()
	with Database.start_session():
		if not Database.session.query(Category).first():
			with open('assets/categories.json', 'r', encoding='utf-8') as f:
				Category.populate(json.loads(f.read()))
