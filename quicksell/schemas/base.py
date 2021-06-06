"""Base and common classes for API schemas."""

from uuid import UUID

from pydantic import BaseModel


class ResponseSchema(BaseModel):
	"""Base response schema."""

	class Config:
		orm_mode = True
		json_encoders = {
			UUID: lambda uuid: uuid.hex
		}


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


class HexUUID(UUID):
	"""Hexadecimal UUID representation."""

	def __str__(self):
		return self.hex

	@classmethod
	def __modify_schema__(cls, field_schema):
		field_schema.update(
			pattern=r'^[0-9a-fA-F]{32}$',
			format='uuid.hex'
		)
