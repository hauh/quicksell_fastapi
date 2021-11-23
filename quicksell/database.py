"""Database manager."""

import logging
from contextlib import contextmanager
from contextvars import ContextVar
from os import environ

from alembic.autogenerate import produce_migrations
from alembic.migration import MigrationContext
from alembic.operations import Operations, ops
from sqlalchemy.engine import create_engine
from sqlalchemy.exc import OperationalError, SQLAlchemyError
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.schema import MetaData

session_context = ContextVar('session')


class RetryingSession(Session):
	"""Retries failed execution an logs exception."""

	def execute(self, *args, retry=False, **kwargs):
		try:
			return super().execute(*args, **kwargs)
		except OperationalError:
			logging.exception("Execution failed")
			if retry:
				raise
			logging.info("Retrying failed query")
			return self.execute(*args, retry=True, **kwargs)


class SessionGetter():
	"""Get current session from ContextVar."""

	def __get__(self, obj, objtype=None):
		return session_context.get()


class Database:
	"""Database connection manager."""

	CONNECT_ARGS = {'connect_timeout': 60}
	URI = 'postgresql://{user}:{password}@{host}:5432/{host}'.format(
		user=environ['POSTGRES_USER'],
		password=environ['POSTGRES_PASSWORD'],
		host=environ['POSTGRES_DB'],
	)

	engine = None
	session = SessionGetter()
	metadata = MetaData()

	@staticmethod
	def connect():
		Database.engine = create_engine(
			Database.URI, connect_args=Database.CONNECT_ARGS, future=True
		)
		try:
			Database.engine.connect()
		except OperationalError as e:
			raise TimeoutError("Database connection failed") from e
		Database.sessionmaker = sessionmaker(
			Database.engine, class_=RetryingSession, autoflush=False, future=True
		)

	@staticmethod
	@contextmanager
	def start_session():
		if not Database.engine:
			Database.connect()
		session = Database.sessionmaker()
		token = session_context.set(session)
		yield
		try:
			session.commit()
		except SQLAlchemyError:
			session.rollback()
		finally:
			session.close()
			session_context.reset(token)

	@staticmethod
	def migrate():
		logging.info("Checking migrations...")
		# pylint: disable=import-outside-toplevel, unused-import
		import quicksell.models  # required to fill metadata
		Database.metadata.create_all(bind=Database.engine)
		context = MigrationContext.configure(Database.engine.connect())
		migrations = produce_migrations(context, Database.metadata)
		if migrations.upgrade_ops.is_empty():
			logging.info("No migrations detected")
			return
		logging.info("Migrating database...")
		operations = Operations(context)
		stack = [migrations.upgrade_ops]
		with context.begin_transaction():
			while stack:
				op = stack.pop(0)
				if isinstance(op, ops.DropTableOp):
					logging.warning("Tables should be dropped manually")
					continue
				if isinstance(op, ops.OpContainer):
					stack.extend(op.ops)
				else:
					operations.invoke(op)
		logging.info("Migrations done")
