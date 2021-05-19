"""User-related API schemas."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr


class ProfileRetrieve(BaseModel):
	"""Profile retrieval schema."""

	uuid: UUID
	full_name: str
	about: str
	online: bool
	rating: int
	avatar: Optional[str]
	location: Optional[str]

	class Config:
		orm_mode = True


class UserRetrieve(BaseModel):
	"""User retrieval schema."""

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


# class UserUpdate(BaseModel):
# 	"""User creation schema."""

# 	email: Optional[EmailStr]
# 	password: Optional[str]
# 	full_name: Optional[str]
# 	fcm_id: Optional[str]
# 	phone: Optional[str]
