"""Offers related database models."""

from sqlalchemy.schema import Column
from sqlalchemy.types import Boolean, Integer, Text

from .base import ColumnUUID, Model, foreign_key, relationship


class Offer(Model):
	"""Listing model."""

	PAGE_SIZE = 30

	uuid = ColumnUUID()
	listing_id = foreign_key('Listing', nullable=False)
	company_id = foreign_key('Company', nullable=False)

	price = Column(Integer, nullable=False)
	comment = Column(Text)
	accepted = Column(Boolean)
	active = Column(Boolean, default=True)

	listing = relationship('Listing', lazy='joined')
	company = relationship('Company', lazy='joined')

	def allowed(self, user):
		return user.company is self.company
