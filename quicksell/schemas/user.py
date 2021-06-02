"""Users related API schemas."""

from datetime import datetime
from typing import Optional

from pydantic import EmailStr

from .base import RequestSchema, ResponseSchema


class ProfileRetrieve(ResponseSchema):
	"""Profile response schema."""

	uuid: str
	full_name: str
	about: str
	online: bool
	rating: int
	phone: str
	avatar: Optional[str]


class UserRetrieve(ResponseSchema):
	"""User response schema."""

	email: str
	is_email_verified: bool
	ts_spawn: datetime
	balance: int
	profile: ProfileRetrieve
	access_token: Optional[str]


class UserCreate(RequestSchema):
	"""User creation schema."""

	email: EmailStr
	password: str
	full_name: str
	fcm_id: str
	phone: str
