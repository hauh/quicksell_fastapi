"""Listings related API schemas."""

from datetime import datetime
from typing import ForwardRef, Optional

from quicksell.models import Listing

from .base import RequestSchema, ResponseSchema

ProfileRetrieve = ForwardRef('ProfileRetrieve')


class ListingRetrieve(ResponseSchema):
	"""Listing response schema."""

	uuid: str
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
	location: Optional[str]
	photos: Optional[str]
	seller: ProfileRetrieve


class ListingCreate(RequestSchema):
	"""Listing creation schema."""

	title: str
	description: str
	price: int
	is_new: bool
	category: str
	quantity: Optional[int]


class ListingUpdate(RequestSchema):
	"""Listing update schema."""

	title: Optional[str]
	description: Optional[str]
	price: Optional[int]
	is_new: Optional[bool]
	category: Optional[str]
	quantity: Optional[int]
