"""User-related database models."""

import time

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from quicksell.database import ModelBase


class User(ModelBase):
	"""User model."""
	__tablename__ = 'User'

	id = Column(Integer, primary_key=True, index=True)
	ts_spawn = Column(Integer, default=time.time)
	email = Column(String, unique=True, index=True)
	password = Column(String)
	is_active = Column(Boolean, default=True)

	profile = relationship('Profile', back_populates='user')


class Profile(ModelBase):
	"""User's profile model."""
	__tablename__ = 'Profile'

	id = Column(Integer, primary_key=True, index=True)
	user_id = Column(Integer, ForeignKey('User.id'))
	full_name = Column(String)
	phone = Column(String)

	user = relationship('User', back_populates='profile')
