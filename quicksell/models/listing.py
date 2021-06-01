"""Listings related database models."""

import enum
from datetime import datetime, timedelta

from sqlalchemy import event
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
	category_id = foreign_key('Category', nullable=False)
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

	location = Column(String)
	photos = Column(String)

	seller = relationship('Profile', lazy=False)
	category = relationship('Category', lazy=False)


class Category(Model):
	"""Listings category model."""

	name = Column(String, nullable=False, unique=True)
	parent_id = foreign_key('Category')
	assignable = Column(Boolean, nullable=False, default=False)

	parent = relationship('Category')

	cached_tree = None

	@staticmethod
	def tree_generator(categories: dict, parent_id: int = None):
		for name, children in categories.items():
			subcategory = Category(
				name=name, parent_id=parent_id, assignable=(not children)
			)
			yield subcategory
			yield from Category.tree_generator(children, subcategory.id)

	@staticmethod
	def setup_events():
		def clear_cache():
			Category.cached_tree = None
		event.listen(Category, 'after_insert', clear_cache)
		event.listen(Category, 'after_update', clear_cache)
		event.listen(Category, 'after_delete', clear_cache)
