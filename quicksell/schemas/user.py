"""User-related API schemas."""

from pydantic import BaseModel


class UserCreate(BaseModel):
	"""User creation schema."""

	email: str
	password: str


class UserRetrieve(BaseModel):
	"""User retrieval schema."""

	id: int
	is_active: bool

	class Config:
		orm_mode = True
