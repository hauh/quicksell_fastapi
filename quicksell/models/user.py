"""Users related database models."""

import enum

from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column
from sqlalchemy.types import Boolean, Enum, Integer, SmallInteger, String

from .base import ColumnUUID, LocationMixin, Model, association, foreign_key


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

	profile = relationship(
		'Profile', back_populates='user', lazy=False, uselist=False
	)
	device = relationship('Device', back_populates='owner', uselist=False)


class Profile(Model, LocationMixin):
	"""User's profile model."""

	uuid = ColumnUUID()
	user_id = foreign_key('User')

	phone = Column(String, unique=True, nullable=False, index=True)
	name = Column(String, nullable=False)
	about = Column(String, nullable=False, default='')

	online = Column(Boolean, nullable=False, default=True)
	rating = Column(Integer, nullable=False, default=0)
	avatar = Column(String)

	user = relationship('User', back_populates='profile', uselist=False)
	listings = relationship(
		'Listing',
		back_populates='seller',
		lazy='dynamic',
		order_by='desc(Listing.ts_spawn)'
	)
	chats = association(
		'Profile', 'Chat',
		back_populates='members',
		lazy='dynamic',
		order_by='desc(Chat.ts_update)'
	)


class Device(Model):
	"""User's device model."""

	class Platform(enum.Enum):
		"""Device platform."""

		other = 0, 'Other'
		android = 1, 'Android'
		ios = 2, 'iOS'

	owner_id = foreign_key('User')
	fcm_id = Column(String, nullable=False, index=True)
	platform = Column(Enum(Platform), nullable=False, default=Platform.other)

	is_active = Column(Boolean, nullable=False, default=True)
	fails_count = Column(SmallInteger, nullable=False, default=0)

	owner = relationship('User', back_populates='device', uselist=False)
