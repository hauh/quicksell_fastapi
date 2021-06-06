"""Chat and Message models."""

from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column
from sqlalchemy.types import BigInteger, String, Text

from .base import ColumnUUID, Model, association, foreign_key, sql_ts_now


class Chat(Model):
	"""User's chat."""

	PAGE_SIZE = 20

	uuid = ColumnUUID()
	listing_id = foreign_key('Listing', nullable=True, index=False)
	last_message_id = foreign_key('Message', nullable=True, index=False)
	subject = Column(String, nullable=False)
	ts_update = Column(BigInteger, server_default=sql_ts_now, onupdate=sql_ts_now)

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


class Message(Model):
	"""Message in Chat."""

	PAGE_SIZE = 40

	author_id = foreign_key('Profile')
	chat_id = foreign_key('Chat')
	text = Column(Text)

	chat = relationship('Chat', back_populates='messages', foreign_keys=[chat_id])
	author = relationship('Profile', back_populates=None, lazy=False)
