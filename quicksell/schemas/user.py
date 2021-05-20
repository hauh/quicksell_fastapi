"""Users related API schemas."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr


class ProfileRetrieve(BaseModel):
	"""Profile response schema."""

	uuid: str
	full_name: str
	about: str
	online: bool
	rating: int
	avatar: Optional[str]
	location: Optional[str]

	class Config:
		orm_mode = True


class UserRetrieve(BaseModel):
	"""User response schema."""

	email: str
	is_email_verified: bool
	ts_spawn: datetime
	balance: int
	profile: ProfileRetrieve
	access_token: Optional[str]

	class Config:
		orm_mode = True


class UserCreate(BaseModel):
	"""User creation schema."""

	email: EmailStr
	password: str
	full_name: str
	fcm_id: str
	phone: str

	class Config:
		anystr_strip_whitespace = True
