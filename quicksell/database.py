"""Database setup and connection."""


from contextlib import contextmanager
from contextvars import ContextVar
from os import environ

from sqlalchemy.engine import create_engine
from sqlalchemy.exc import OperationalError, SQLAlchemyError
from sqlalchemy.orm import sessionmaker
from sqlalchemy.schema import MetaData

session_context = ContextVar('session')


class Session:
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
	session = Session()
	metadata = MetaData()

	@classmethod
	def connect(cls):
		cls.engine = create_engine(
			Database.URI, connect_args=Database.CONNECT_ARGS, future=True
		)
		try:
			cls.engine.connect()
		except OperationalError as e:
			raise TimeoutError("Database connection failed") from e
		cls.sessionmaker = sessionmaker(cls.engine, autoflush=False, future=True)

	@classmethod
	@contextmanager
	def start_session(cls):
		session = cls.sessionmaker()
		token = session_context.set(session)
		yield
		try:
			session.commit()
		except SQLAlchemyError:
			session.rollback()
			raise
		finally:
			session.close()
			session_context.reset(token)

	@classmethod
	def create_tables(cls):
		cls.metadata.create_all(bind=cls.engine)
