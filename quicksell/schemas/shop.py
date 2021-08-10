"""Shops related API schemas."""

from typing import Optional

from pydantic import EmailStr

from quicksell.models import Company

from .base import HexUUID, LocationSchema, RequestSchema, ResponseSchema


class CompanyRetrieve(ResponseSchema):
	"""Company response schema."""

	uuid: HexUUID
	name: str
	form: Company.Form
	tin: str
	address: str
	phone: str
	email: EmailStr
	logo: Optional[str]


class ShopRetrieve(ResponseSchema):
	"""Shop response schema."""

	uuid: HexUUID
	name: str
	description: Optional[str]
	location: LocationSchema
	phone: str
	photo: Optional[str]
	company: CompanyRetrieve


class CompanyCreate(RequestSchema):
	"""Company creation schema."""

	name: str
	form: Company.Form
	tin: int
	address: str
	phone: str
	email: EmailStr
	logo: Optional[str]


class ShopCreate(RequestSchema):
	"""Shop creation schema."""

	name: str
	description: Optional[str]
	phone: str
	location: LocationSchema
	photo: Optional[str]
