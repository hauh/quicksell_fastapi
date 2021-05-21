"""Base classes for API schemas."""

from pydantic import BaseModel


class ResponseSchema(BaseModel):
	"""Base response schema."""

	class Config:
		orm_mode = True


class RequestSchema(BaseModel):
	"""Base request schema."""

	class Config:
		anystr_strip_whitespace = True
