"""Database setup and connection."""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

engine = create_engine(
	"sqlite:///./sql_app.db",
	connect_args={"check_same_thread": False}
)
make_session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
ModelBase = declarative_base()


def session():
	try:
		s = make_session()
		yield s
	finally:
		s.close()
