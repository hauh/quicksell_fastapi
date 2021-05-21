"""Database setup and connection."""

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

engine = create_engine(
	"sqlite:///./sql_app.db",
	connect_args={"check_same_thread": False}
)
make_session = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_session() -> Session:
	try:
		s = make_session()
		yield s
	finally:
		s.close()
