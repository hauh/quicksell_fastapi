"""Chat and Message models."""

from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column
from sqlalchemy.sql import func
from sqlalchemy.types import BigInteger, String, Text

from .base import Model, UUIDColumn, association, foreign_key


class Chat(Model):
	"""User's chat."""

	uuid = UUIDColumn()
	listing_id = foreign_key('Listing', nullable=True, index=False)
	last_message_id = foreign_key('Message', nullable=True, index=False)
	subject = Column(String, nullable=False)
	ts_update = Column(BigInteger, server_default=func.now(), onupdate=func.now())

	members = association('Chat', 'Profile', back_populates='chats', lazy=False)
	listing = relationship('Listing', back_populates=None, lazy=False)
	last_message = relationship(
		'Message',
		lazy=False,
		post_update=True,
		foreign_keys=[last_message_id],
	)
	messages = relationship(
		'Message',
		back_populates='chat',
		lazy='dynamic',
		order_by='desc(Message.ts_spawn)',
		foreign_keys="[Message.chat_id]"
	)

	@classmethod
	def about_listing(cls, listing):
		return cls(listing=listing, subject=listing.title, members=[listing.seller])


class Message(Model):
	"""Message in Chat."""

	author_id = foreign_key('Profile')
	chat_id = foreign_key('Chat')
	text = Column(Text)

	chat = relationship('Chat', back_populates='messages', foreign_keys=[chat_id])
	author = relationship('Profile', back_populates=None, lazy=False)
