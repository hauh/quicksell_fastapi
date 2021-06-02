"""Base class of database models."""

from functools import partial
from uuid import uuid4

from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKey, Table
from sqlalchemy.sql import func
from sqlalchemy.types import BigInteger, Float, Integer, String


class Base:
	"""Base model class."""
	# pylint: disable=no-self-argument, no-member

	@declared_attr
	def __tablename__(cls):
		return cls.__name__

	id = Column(Integer, primary_key=True, index=True)
	ts_spawn = Column(BigInteger, server_default=func.now())


Model = declarative_base(cls=Base)


class LocationMixin:
	"""Physical location of object."""

	latitude = Column(Float, index=True)
	longitude = Column(Float, index=True)
	address = Column(String)

	location = property()

	@location.setter
	def location(self, location_dict):
		self.latitude = location_dict['latitude']
		self.longitude = location_dict['longitude']
		self.address = location_dict['address']

	@location.getter
	def location(self):
		if not self.address:
			return None
		return {
			'latitude': self.latitude,
			'longitude': self.longitude,
			'address': self.address
		}


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


UUIDColumn = partial(
	Column, 'uuid', String,
	nullable=False,
	default=lambda: uuid4().hex,
	index=True,
)
