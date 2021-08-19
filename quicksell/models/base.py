"""Base class of database models."""

from functools import partial
from uuid import uuid4

from psycopg2.errorcodes import UNIQUE_VIOLATION
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.declarative import as_declarative
from sqlalchemy.orm import declared_attr, relationship
from sqlalchemy.schema import Column, ForeignKey, Table
from sqlalchemy.sql import func, select
from sqlalchemy.types import BigInteger, Float, Integer, String

from quicksell.database import Database

sql_ts_now = func.extract('epoch', func.now())
ColumnUUID = partial(Column, UUID(as_uuid=True), nullable=False, default=uuid4)


class UniqueViolation(Exception):
	"""PostgreSQL unique constraint violation error."""

	def __init__(self, pg_exception_details):
		super().__init__()
		key, value = pg_exception_details.message_detail.split(')=(')
		self.value = value[:value.find(')')]
		key = key[key.find('(') + 1:]
		self.table = pg_exception_details.table_name
		column = Database.metadata.tables[self.table].columns[key]
		self.column = column.doc or column.name

	def __str__(self):
		return f"{self.table} with {self.column} '{self.value}' already exists"


@as_declarative(metadata=Database.metadata)
class Model:
	"""Base model class."""
	# pylint: disable=no-self-argument, no-member

	@declared_attr
	def __tablename__(cls):
		return cls.__name__

	id = Column(Integer, primary_key=True, index=True)
	ts_spawn = Column(BigInteger, server_default=sql_ts_now)

	def save(self):
		try:
			Database.session.add(self)
			Database.session.flush()
		except IntegrityError as e:
			if e.orig.pgcode != UNIQUE_VIOLATION:
				raise
			raise UniqueViolation(e.orig.diag) from e
		return self

	@classmethod
	def insert(cls, *args, **kwargs):
		return cls(*args, **kwargs).save()

	@classmethod
	def select(cls, *filters):
		return Database.session.execute(
			select(cls).where(*filters)
		).scalars().unique().all()

	@classmethod
	def scalar(cls, *filters):
		return Database.session.execute(select(cls).where(*filters)).scalar()

	@classmethod
	def paginate(cls, *filters, order_by=None, page=0):
		return Database.session.execute(
			select(cls).where(*filters).order_by(order_by)
			.offset(page * cls.PAGE_SIZE).limit(cls.PAGE_SIZE)
		).scalars().unique().all()

	def update(self, **kwargs):
		for attribute, value in kwargs.items():
			setattr(self, attribute, value)
		return self.save()

	def delete(self):
		Database.session.delete(self)


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
	table = Database.metadata.tables.get(table_name)
	if table is None:
		columns = [
			Column(
				associated_table_name.lower() + '_id', Integer,
				ForeignKey(associated_table_name + '.id'),
				primary_key=True, index=True
			)
			for associated_table_name in (table_from, table_to)
		]
		table = Table(table_name, Database.metadata, *columns)
	return relationship(table_to, secondary=table, **kwargs)


def foreign_key(table_name, nullable=True, index=True):
	return Column(
		Integer, ForeignKey(table_name + '.id'),
		nullable=nullable, index=index
	)
