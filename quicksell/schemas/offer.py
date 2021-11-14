"""Offers related API schemas."""

from datetime import datetime
from typing import ForwardRef, Optional

from pydantic import conint

from .base import HexUUID, RequestSchema, ResponseSchema

ListingRetrieve = ForwardRef('ListingRetrieve')
CompanyRetrieve = ForwardRef('CompanyRetrieve')


class OfferRetrieve(ResponseSchema):
	"""Offer response schema."""

	uuid: HexUUID
	ts_spawn: datetime
	price: int
	comment: Optional[str]
	accepted: Optional[bool]
	listing: ListingRetrieve
	company: CompanyRetrieve


class OfferCreate(RequestSchema):
	"""Offer creation schema."""

	price: conint(gt=0)
	comment: Optional[str]
	listing_uuid: HexUUID


class OfferUpdate(RequestSchema):
	"""Offer update schema."""

	price: Optional[conint(gt=0)]
	comment: Optional[str]
