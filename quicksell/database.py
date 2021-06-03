"""Database setup and connection."""

from os import environ

from sqlalchemy.engine import create_engine
from sqlalchemy.orm import Session, sessionmaker

engine = create_engine(
	"postgresql://{user}:{password}@{host}:5432/{host}".format(
		user=environ['POSTGRES_USER'],
		password=environ['POSTGRES_PASSWORD'],
		host=environ['POSTGRES_DB'],
	),
	future=True
)
session_maker = sessionmaker(
	autocommit=False, autoflush=False, bind=engine, future=True
)


def get_session() -> Session:
	with session_maker() as session:
		yield session
