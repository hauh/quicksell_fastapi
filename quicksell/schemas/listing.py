"""Listings related API schemas."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from quicksell.models import Listing

from .user import ProfileRetrieve


class ListingRetrieve(BaseModel):
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

	class Config:
		orm_mode = True


class ListingCreate(BaseModel):
	"""Listing creation schema."""

	title: str
	description: str
	price: int
	is_new: bool
	category: str
	quantity: Optional[int]

	class Config:
		anystr_strip_whitespace = True


class ListingUpdate(BaseModel):
	"""Listing update schema."""

	title: Optional[str]
	description: Optional[str]
	price: Optional[int]
	is_new: Optional[bool]
	category: Optional[str]
	quantity: Optional[int]

	class Config:
		anystr_strip_whitespace = True
