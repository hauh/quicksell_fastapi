"""Database setup and connection."""

from sqlalchemy.engine import create_engine
from sqlalchemy.orm import Session, sessionmaker

engine = create_engine(
	"sqlite:///./sql_app.db",
	connect_args={"check_same_thread": False},
	future=True
)
session_maker = sessionmaker(
	autocommit=False, autoflush=False, bind=engine, future=True
)


def get_session() -> Session:
	with session_maker() as session:
		yield session
