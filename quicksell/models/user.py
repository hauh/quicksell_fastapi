"""User-related database models."""

import enum
from uuid import uuid4

from sqlalchemy.orm import relationship
# from sqlalchemy.dialects.postgresql import UUID
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
	email = Column(String, unique=True, index=True)
	access_token = Column(String, index=True)
	password_hash = Column(String)

	ts_spawn = Column(TIMESTAMP, server_default=func.now())

	is_active = Column(Boolean, default=True)
	is_email_verified = Column(Boolean, default=False)
	is_staff = Column(Boolean, default=False)
	is_admin = Column(Boolean, default=False)

	password_reset_code = Column(Integer)
	password_reset_request_ts = Column(Integer)

	balance = Column(Integer, default=0)

	profile = relationship('Profile', backref='user', uselist=False)
	device = relationship('Device', backref='owner', uselist=False)


class Profile(ModelBase):
	"""User's profile model."""
	__tablename__ = 'Profile'

	id = Column(Integer, ForeignKey('User.id'), primary_key=True, index=True)
	# uuid = Column(UUID, default=uuid.uuid4, editable=False)
	uuid = Column(String, default=lambda: uuid4().hex)

	phone = Column(String, unique=True, index=True)
	full_name = Column(String)
	about = Column(String, default='')

	online = Column(Boolean, default=True)
	rating = Column(Integer, default=0)
	avatar = Column(String)

	location = Column(String)


class Device(ModelBase):
	"""User's device model."""
	__tablename__ = 'Device'

	class Platform(enum.Enum):
		"""Device platform."""

		other = 0, 'Other'
		android = 1, 'Android'
		ios = 2, 'iOS'

	id = Column(Integer, primary_key=True, index=True)
	owner_id = Column(Integer, ForeignKey('User.id'), index=True)
	fcm_id = Column(String, index=True)
	platform = Column(Enum(Platform), default=Platform.other)

	is_active = Column(Boolean, default=True)
	fails_count = Column(SmallInteger, default=0)
