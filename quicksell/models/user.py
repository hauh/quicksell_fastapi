"""Users related database models."""

import enum
from uuid import uuid4

from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Boolean, Enum, Integer, SmallInteger, String

from .base import Model


class User(Model):
	"""User model."""

	email = Column(String, unique=True, nullable=False, index=True)
	access_token = Column(String, index=True)
	password_hash = Column(String, nullable=False)

	is_active = Column(Boolean, nullable=False, default=True)
	is_email_verified = Column(Boolean, nullable=False, default=False)
	is_staff = Column(Boolean, nullable=False, default=False)
	is_admin = Column(Boolean, nullable=False, default=False)

	password_reset_code = Column(Integer)
	password_reset_request_ts = Column(Integer)

	balance = Column(Integer, nullable=False, default=0)

	profile = relationship('Profile', backref='user', uselist=False)
	device = relationship('Device', backref='owner', uselist=False)


class Profile(Model):
	"""User's profile model."""

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


class Device(Model):
	"""User's device model."""

	class Platform(enum.Enum):
		"""Device platform."""

		other = 0, 'Other'
		android = 1, 'Android'
		ios = 2, 'iOS'

	owner_id = Column(Integer, ForeignKey('User.id'), nullable=False, index=True)
	fcm_id = Column(String, nullable=False, index=True)
	platform = Column(Enum(Platform), nullable=False, default=Platform.other)

	is_active = Column(Boolean, nullable=False, default=True)
	fails_count = Column(SmallInteger, nullable=False, default=0)
