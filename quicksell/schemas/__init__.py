"""API schemas."""

from . import chat, listing, offer, user
from .base import HexUUID
from .chat import ChatRetrieve, MessageRetrieve
from .listing import ListingCreate, ListingRetrieve, ListingUpdate
from .offer import OfferCreate, OfferRetrieve, OfferUpdate
from .shop import CompanyCreate, CompanyRetrieve, ShopCreate, ShopRetrieve
from .user import ProfileRetrieve, ProfileUpdate, UserCreate, UserRetrieve

chat.ProfileRetrieve = ProfileRetrieve
listing.ProfileRetrieve = ProfileRetrieve
offer.CompanyRetrieve = CompanyRetrieve
offer.ListingRetrieve = ListingRetrieve
user.ChatRetrieve = ChatRetrieve
user.CompanyRetrieve = CompanyRetrieve
user.ShopRetrieve = ShopRetrieve


def update_forward_refs():
	for var_name, var in globals().items():
		if var_name.endswith('Retrieve'):
			var.update_forward_refs()


update_forward_refs()
