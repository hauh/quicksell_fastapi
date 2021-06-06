"""Listings related database models."""

import enum
from datetime import timedelta

from sqlalchemy import event
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column
from sqlalchemy.types import BigInteger, Boolean, Enum, Integer, String, Text

from .base import LocationMixin, Model, UUIDMixin, foreign_key, sql_ts_now

DEFAULT_LISTING_EXPIRY_TIME = timedelta(days=30).total_seconds()
sql_ts_expires = sql_ts_now + DEFAULT_LISTING_EXPIRY_TIME


class Listing(Model, UUIDMixin, LocationMixin):
	"""Listing model."""

	PAGE_SIZE = 30

	class State(enum.Enum):
		"""Listing's poissble states."""

		draft = 0, 'Draft'
		active = 1, 'Active'
		sold = 2, 'Sold'
		closed = 3, 'Closed'
		deleted = 4, 'Deleted'

	seller_id = foreign_key('Profile', nullable=False)
	category_id = foreign_key('Category', nullable=False)

	state = Column(Enum(State), nullable=False, default=State.active)
	ts_expires = Column(BigInteger, nullable=False, server_default=sql_ts_expires)

	title = Column(String, nullable=False)
	description = Column(Text, nullable=False, default='')
	price = Column(Integer, nullable=False, default=0)
	is_new = Column(Boolean, nullable=False, default=False)
	quantity = Column(Integer, nullable=False, default=1)
	properties = Column(JSONB)

	sold = Column(Integer, nullable=False, default=0)
	views = Column(Integer, nullable=False, default=0)

	photos = Column(String)

	seller = relationship('Profile', lazy=False)
	category = relationship('Category', lazy=False)


class Category(Model):
	"""Listings category model."""

	name = Column(String, nullable=False, unique=True)
	parent_id = foreign_key('Category')
	assignable = Column(Boolean, nullable=False, default=False)

	parent = relationship('Category', uselist=False)

	cached_tree = None

	@staticmethod
	def populate_table(categories: dict, parent_id: int = None):
		for name, subcategories in categories.items():
			category = Category.insert(
				name=name, parent_id=parent_id, assignable=(not subcategories)
			)
			Category.populate_table(subcategories, category.id)

	@staticmethod
	def setup_events():
		def clear_cache():
			Category.cached_tree = None
		event.listen(Category, 'after_insert', clear_cache)
		event.listen(Category, 'after_update', clear_cache)
		event.listen(Category, 'after_delete', clear_cache)
