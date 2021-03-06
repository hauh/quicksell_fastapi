"""Base class of database models."""

import math
from functools import partial
from uuid import uuid4

from psycopg2.errorcodes import UNIQUE_VIOLATION
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.declarative import as_declarative
from sqlalchemy.ext.mutable import MutableDict, MutableList
from sqlalchemy.orm import declared_attr, relationship
from sqlalchemy.schema import Column, ForeignKey, Table
from sqlalchemy.sql import func, select
from sqlalchemy.types import BigInteger, Float, Integer, String

from quicksell.database import Database

sql_ts_now = func.extract('epoch', func.now())
ColumnUUID = partial(
	Column, UUID(as_uuid=True), nullable=False, default=uuid4, index=True
)
ColumnArray = partial(
	Column, MutableList.as_mutable(ARRAY(String)), server_default='{}'
)
ColumnJSON = partial(
	Column, MutableDict.as_mutable(JSONB), server_default='{}'
)


class UniqueViolation(Exception):
	"""PostgreSQL unique constraint violation error."""

	def __init__(self, pg_exception_details):
		super().__init__()
		key, value = pg_exception_details.message_detail.split(')=(')
		self.value = value[:value.find(')')]
		self.column = key[key.find('(') + 1:]
		self.table = pg_exception_details.table_name

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
	ts_spawn = Column(BigInteger, server_default=sql_ts_now, index=True)

	def save(self):
		try:
			Database.session.add(self)
			Database.session.flush()
		except IntegrityError as e:
			Database.session.rollback()
			if e.orig.pgcode == UNIQUE_VIOLATION:
				raise UniqueViolation(e.orig.diag) from e
			raise
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
		query = select(cls).where(*filters) \
			.offset(page * cls.PAGE_SIZE).limit(cls.PAGE_SIZE)
		if order_by is not None:
			if isinstance(order_by, str):
				order_col = cls.__table__.columns.get(order_by.removeprefix('-'))
				if order_col is not None:
					if order_by.startswith('-'):
						order_col = order_col.desc()
					query = query.order_by(order_col)
			else:
				query = query.order_by(order_by)
		return Database.session.execute(query).scalars().unique().all()

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

	# @classmethod
	# def in_range(cls, latitude, longitude, radius):
	# 	latitude = math.radians(latitude)
	# 	longitude = math.radians(longitude)
	# 	expression = (func.acos(
	# 		func.sin(func.radians(cls.latitude)) * math.sin(latitude)
	# 		+ func.cos(func.radians(cls.latitude)) * math.cos(latitude)
	# 		* func.cos(func.radians(cls.longitude) - longitude)
	# 	) * 6378137).label('distance')
	# 	delta_lng = (180 / math.pi) * (radius / 6378137)
	# 	delta_lat = delta_lng / math.cos(latitude)
	# 	filt = (
	# 		cls.longitude.between(cls.longitude - delta_lng, cls.longitude + delta_lng)
	# 		& cls.latitude.between(cls.latitude - delta_lat, cls.latitude + delta_lat)
	# 		& (expression <= radius)
	# 	)
	# 	return filt, expression

	# @classmethod
	# def ordered_by_distance(cls, lat, lng, radius, *filters, desc, page=1):
	# 	range_filter, distance_expression = cls.in_range(lat, lng, radius)
	# 	return Database.session.execute(
	# 		select(cls, distance_expression).where(range_filter, *filters)
	# 		.order_by(distance_expression.desc() if desc else distance_expression)
	# 		.offset(page * cls.PAGE_SIZE).limit(cls.PAGE_SIZE)
	# 	).scalars().unique().all()


def association(table_from, table_to, **kwargs):
	table_name = 'Association{}{}'.format(*sorted((table_from, table_to)))
	if order_by := kwargs.get('order_by'):
		kwargs['order_by'] = order_by.replace('self', table_name + '.c')
	table = Database.metadata.tables.get(table_name)
	if table is None:
		table = Table(
			table_name, Database.metadata,
			Column(
				table_from.lower() + '_id', Integer,
				ForeignKey(table_from + '.id'),
				primary_key=True, index=True
			),
			Column(
				table_to.lower() + '_id', Integer,
				ForeignKey(table_to + '.id'),
				primary_key=True, index=True
			),
			Column('ts_spawn', BigInteger, server_default=sql_ts_now, index=True)
		)
	return relationship(table_to, secondary=table, **kwargs)


def foreign_key(table_name, index=True, **kwargs):
	return Column(
		Integer,
		ForeignKey(table_name + '.id', use_alter=True),
		index=index, **kwargs
	)
