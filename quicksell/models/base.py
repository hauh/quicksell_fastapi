"""Base class of database models."""

from functools import partial
from uuid import uuid4

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base, declared_attr, relationship
from sqlalchemy.schema import Column, ForeignKey, Table
from sqlalchemy.sql import func, select
from sqlalchemy.types import BigInteger, Float, Integer, String

from quicksell.database import Database

sql_ts_now = func.extract('epoch', func.now())
ColumnUUID = partial(Column, UUID(as_uuid=True), nullable=False, default=uuid4)


class Base:
	"""Base model class."""
	# pylint: disable=no-self-argument, no-member

	@declared_attr
	def __tablename__(cls):
		return cls.__name__

	id = Column(Integer, primary_key=True, index=True)
	ts_spawn = Column(BigInteger, server_default=sql_ts_now)

	@classmethod
	def insert(cls, *args, **kwargs):
		obj = cls(*args, **kwargs)
		Database.session.add(obj)
		Database.session.flush()
		return obj

	@classmethod
	def select(cls, *filters):
		return Database.session.execute(select(cls).where(*filters)).scalars().all()

	@classmethod
	def scalar(cls, *filters):
		return Database.session.execute(select(cls).filter(*filters)).scalar()

	@classmethod
	def paginate(cls, *filters, order_by=None, page=0):
		return Database.session.execute(
			select(cls).where(*filters).order_by(order_by)
			.offset(page * cls.PAGE_SIZE).limit(cls.PAGE_SIZE)
		).scalars().unique().all()

	def update(self, **kwargs):
		for attribute, value in kwargs.items():
			setattr(self, attribute, value)

	def delete(self):
		Database.session.delete(self)


Model = declarative_base(cls=Base, metadata=Database.metadata)


class LocationMixin:
	"""Physical location of an object."""

	latitude = Column(Float, index=True)
	longitude = Column(Float, index=True)
	address = Column(String)

	@property
	def location(self):
		if not self.address:
			return None
		return {
			'latitude': self.latitude,
			'longitude': self.longitude,
			'address': self.address
		}

	@location.setter
	def location(self, location_dict):
		self.latitude = location_dict['latitude']
		self.longitude = location_dict['longitude']
		self.address = location_dict['address']


def association(table_from, table_to, **kwargs):
	table_name = 'Association{}{}'.format(*sorted((table_from, table_to)))
	table = Model.metadata.tables.get(table_name)
	if table is None:
		columns = [
			Column(
				associated_table_name.lower() + '_id', Integer,
				ForeignKey(associated_table_name + '.id'),
				primary_key=True, index=True
			)
			for associated_table_name in (table_from, table_to)
		]
		table = Table(table_name, Model.metadata, *columns)
	return relationship(table_to, secondary=table, **kwargs)


def foreign_key(table_name, nullable=True, index=True):
	return Column(
		Integer, ForeignKey(table_name + '.id'),
		nullable=nullable, index=index
	)
