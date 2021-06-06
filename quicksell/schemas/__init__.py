"""API schemas."""

from . import chat, listing, user
from .base import HexUUID
from .chat import ChatRetrieve, MessageRetrieve
from .listing import ListingCreate, ListingRetrieve, ListingUpdate
from .user import ProfileRetrieve, UserCreate, UserRetrieve

chat.ProfileRetrieve = ProfileRetrieve
listing.ProfileRetrieve = ProfileRetrieve
user.ChatRetrieve = ChatRetrieve


def update_forward_refs():
	for var_name, var in globals().items():
		if var_name.endswith('Retrieve'):
			var.update_forward_refs()


update_forward_refs()
