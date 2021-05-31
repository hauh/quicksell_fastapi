"""Listings related database models."""

import enum
from datetime import datetime, timedelta

from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column
from sqlalchemy.types import JSON, TIMESTAMP, Boolean, Enum, Integer, String

from .base import Model, UUIDColumn, foreign_key

DEFAULT_LISTING_EXPIRATION_TIME = timedelta(days=30)


def set_expiration_date():
	return datetime.now() + DEFAULT_LISTING_EXPIRATION_TIME


class Listing(Model):
	"""Listing model."""

	class State(enum.Enum):
		"""Listing's poissble states."""

		draft = 0, 'Draft'
		active = 1, 'Active'
		sold = 2, 'Sold'
		closed = 3, 'Closed'
		deleted = 4, 'Deleted'

	uuid = UUIDColumn()
	seller_id = foreign_key('Profile')
	state = Column(Enum(State), nullable=False, default=State.active)

	ts_expires = Column(TIMESTAMP, nullable=False, default=set_expiration_date)

	title = Column(String, nullable=False)
	description = Column(String, nullable=False, default='')
	price = Column(Integer, nullable=False, default=0)
	is_new = Column(Boolean, nullable=False, default=False)
	quantity = Column(Integer, nullable=False, default=1)
	properties = Column(JSON)

	sold = Column(Integer, nullable=False, default=0)
	views = Column(Integer, nullable=False, default=0)

	category = Column(String, nullable=False, default='No category')
	location = Column(String)
	photos = Column(String)

	seller = relationship('Profile', lazy=False)
