"""Base class of database models."""

from uuid import uuid4

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKey, Table
from sqlalchemy.sql import func
from sqlalchemy.types import BigInteger, Float, Integer, String

sql_ts_now = func.extract('epoch', func.now())


class Base:
	"""Base model class."""
	# pylint: disable=no-self-argument, no-member

	@declared_attr
	def __tablename__(cls):
		return cls.__name__

	id = Column(Integer, primary_key=True, index=True)
	ts_spawn = Column(BigInteger, server_default=sql_ts_now)


Model = declarative_base(cls=Base)


class UUIDMixin:
	"""Outside id of an object."""

	_uuid = Column('uuid', UUID(as_uuid=True), nullable=False, default=uuid4)

	@hybrid_property
	def uuid(self):
		return self._uuid.hex

	@uuid.expression
	def uuid(self):
		return self._uuid


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
