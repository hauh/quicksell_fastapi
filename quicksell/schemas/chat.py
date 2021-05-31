"""Chats related API schemas."""

from datetime import datetime
from typing import ForwardRef, Optional

from .base import ResponseSchema

ProfileRetrieve = ForwardRef('ProfileRetrieve')


class MessageRetrieve(ResponseSchema):
	"""Message in Chat response schema."""

	author: ProfileRetrieve
	text: str
	ts_spawn: datetime


class ChatRetrieve(ResponseSchema):
	"""Chat response schema."""

	uuid: str
	subject: str
	ts_update: datetime
	last_message: Optional[MessageRetrieve]
	members: list[ProfileRetrieve]
