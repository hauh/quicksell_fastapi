"""Users related database models."""

import enum
from uuid import uuid4

from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.types import (
	TIMESTAMP, Boolean, Enum, Integer, SmallInteger, String
)

from quicksell.database import ModelBase


class User(ModelBase):
	"""User model."""
	__tablename__ = 'User'

	id = Column(Integer, primary_key=True, index=True)
	email = Column(String, unique=True, nullable=False, index=True)
	access_token = Column(String, index=True)
	password_hash = Column(String, nullable=False)

	ts_spawn = Column(TIMESTAMP, nullable=False, server_default=func.now())

	is_active = Column(Boolean, nullable=False, default=True)
	is_email_verified = Column(Boolean, nullable=False, default=False)
	is_staff = Column(Boolean, nullable=False, default=False)
	is_admin = Column(Boolean, nullable=False, default=False)

	password_reset_code = Column(Integer)
	password_reset_request_ts = Column(Integer)

	balance = Column(Integer, nullable=False, default=0)

	profile = relationship('Profile', backref='user', uselist=False)
	device = relationship('Device', backref='owner', uselist=False)


class Profile(ModelBase):
	"""User's profile model."""
	__tablename__ = 'Profile'

	id = Column(Integer, primary_key=True, index=True)
	user_id = Column(Integer, ForeignKey('User.id'), nullable=False, index=True)
	uuid = Column(String, nullable=False, default=lambda: uuid4().hex)

	phone = Column(String, unique=True, nullable=False, index=True)
	full_name = Column(String, nullable=False)
	about = Column(String, nullable=False, default='')

	online = Column(Boolean, nullable=False, default=True)
	rating = Column(Integer, nullable=False, default=0)
	avatar = Column(String)

	location = Column(String)
	listings = relationship('Listing', backref='seller')


class Device(ModelBase):
	"""User's device model."""
	__tablename__ = 'Device'

	class Platform(enum.Enum):
		"""Device platform."""

		other = 0, 'Other'
		android = 1, 'Android'
		ios = 2, 'iOS'

	id = Column(Integer, primary_key=True, index=True)
	owner_id = Column(Integer, ForeignKey('User.id'), nullable=False, index=True)
	fcm_id = Column(String, nullable=False, index=True)
	platform = Column(Enum(Platform), nullable=False, default=Platform.other)

	is_active = Column(Boolean, nullable=False, default=True)
	fails_count = Column(SmallInteger, nullable=False, default=0)
