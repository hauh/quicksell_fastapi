"""Listings related database models."""

import enum
from datetime import timedelta

from sqlalchemy import UniqueConstraint, event
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column
from sqlalchemy.types import BigInteger, Boolean, Enum, Integer, String, Text

from .base import (
	ColumnArray, ColumnJSON, ColumnUUID, LocationMixin, Model, foreign_key,
	sql_ts_now
)

DEFAULT_LISTING_EXPIRY_TIME = timedelta(days=30).total_seconds()
sql_ts_expires = sql_ts_now + DEFAULT_LISTING_EXPIRY_TIME


class Listing(Model, LocationMixin):
	"""Listing model."""

	PAGE_SIZE = 30
	PUBLICATION_DELAY = timedelta(hours=5).total_seconds()

	class State(enum.Enum):
		"""Listing's poissble states."""

		draft = 0, 'Draft'
		active = 1, 'Active'
		sold = 2, 'Sold'
		closed = 3, 'Closed'
		deleted = 4, 'Deleted'

	uuid = ColumnUUID()
	seller_id = foreign_key('Profile', nullable=False)
	category_id = foreign_key('Category', nullable=False)

	state = Column(Enum(State), nullable=False, default=State.active)
	ts_expires = Column(BigInteger, nullable=False, server_default=sql_ts_expires)

	title = Column(String, nullable=False)
	description = Column(Text, nullable=False, default='')
	price = Column(Integer, nullable=False, default=0)
	is_new = Column(Boolean, nullable=False, default=False)
	quantity = Column(Integer, nullable=False, default=1)
	properties = ColumnJSON()

	sold = Column(Integer, nullable=False, default=0)
	views = Column(Integer, nullable=False, default=0)

	photos = ColumnArray()

	seller = relationship('Profile', lazy=False)
	category = relationship('Category', lazy=False)
	offers = relationship(
		'Offer',
		back_populates='listing',
		lazy=True,
		cascade='all, delete-orphan'
	)

	def allowed(self, user):
		return user.profile is self.seller


class Category(Model):
	"""Listings category model."""

	name = Column(String, nullable=False, unique=True)
	parent_id = foreign_key('Category')
	assignable = Column(Boolean, nullable=False, default=False)

	parent = relationship('Category', uselist=False)

	cached_tree = None

	@staticmethod
	def populate(categories: dict, parent_id: int = None):
		for name, subcategories in categories.items():
			category = Category.insert(
				name=name, parent_id=parent_id, assignable=(not subcategories)
			)
			Category.populate(subcategories, category.id)

	@staticmethod
	def setup_events():
		def clear_cache():
			Category.cached_tree = None
		event.listen(Category, 'after_insert', clear_cache)
		event.listen(Category, 'after_update', clear_cache)
		event.listen(Category, 'after_delete', clear_cache)


class View(Model):
	"""Listing view model."""

	__table_args__ = (UniqueConstraint('listing_id', 'ip'),)

	listing_id = foreign_key('Listing', nullable=False)
	ip = Column(String, nullable=False, index=True)
