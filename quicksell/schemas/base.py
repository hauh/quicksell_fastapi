"""Base and common classes for API schemas."""

from pydantic import BaseModel


class ResponseSchema(BaseModel):
	"""Base response schema."""

	class Config:
		orm_mode = True


class RequestSchema(BaseModel):
	"""Base request schema."""

	class Config:
		anystr_strip_whitespace = True

	def dict(self, exclude_unset=True, exclude_none=True, **kwargs):
		return super().dict(
			exclude_unset=exclude_unset, exclude_none=exclude_none, **kwargs
		)


class LocationSchema(RequestSchema):
	"""Location schema."""

	latitude: float
	longitude: float
	address: str
