"""Listings related API schemas."""

from datetime import datetime
from typing import ForwardRef, Optional

from pydantic import conint, validator

from quicksell.models import Listing

from .base import HexUUID, LocationSchema, RequestSchema, ResponseSchema

ProfileRetrieve = ForwardRef('ProfileRetrieve')


class ListingRetrieve(ResponseSchema):
	"""Listing response schema."""

	uuid: HexUUID
	state: Listing.State
	ts_spawn: datetime
	ts_expires: datetime
	title: str
	description: str
	price: int
	is_new: bool
	category: str
	quantity: int
	properties: Optional[str]
	sold: int
	views: int
	photos: Optional[str]
	location: Optional[LocationSchema]
	seller: ProfileRetrieve

	@validator('category', pre=True)
	def category_name(cls, category):  # pylint: disable=no-self-argument
		return category.name


class ListingCreate(RequestSchema):
	"""Listing creation schema."""

	title: str
	description: str
	price: conint(ge=0)
	is_new: bool
	category: str
	quantity: Optional[int]
	location: Optional[LocationSchema]


class ListingUpdate(RequestSchema):
	"""Listing update schema."""

	title: Optional[str]
	description: Optional[str]
	price: Optional[conint(ge=0)]
	is_new: Optional[bool]
	category: Optional[str]
	quantity: Optional[int]
	location: Optional[LocationSchema]
