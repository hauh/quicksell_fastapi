"""Users related API schemas."""

from datetime import datetime
from typing import ForwardRef, Optional

from pydantic import EmailStr

from .base import HexUUID, RequestSchema, ResponseSchema

CompanyRetrieve = ForwardRef('CompanyRetrieve')


class ProfileRetrieve(ResponseSchema):
	"""Profile response schema."""

	uuid: HexUUID
	name: str
	phone: str
	about: str
	ts_spawn: datetime
	online: bool
	rating: int
	avatar: Optional[str]


class ProfileUpdate(RequestSchema):
	"""Profile update schema."""

	name: Optional[str]
	phone: Optional[str]
	about: Optional[str]
	avatar: Optional[str]


class UserRetrieve(ResponseSchema):
	"""User response schema."""

	email: str
	is_email_verified: bool
	balance: int
	profile: ProfileRetrieve
	access_token: Optional[str]
	company: Optional[CompanyRetrieve]


class UserCreate(RequestSchema):
	"""User creation schema."""

	email: EmailStr
	password: str
	name: str
	fcm_id: str
	phone: str
