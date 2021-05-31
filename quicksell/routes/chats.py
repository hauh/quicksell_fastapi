"""api/chats/"""

from fastapi import APIRouter, Body, Depends, Response
from starlette.status import HTTP_201_CREATED, HTTP_204_NO_CONTENT

from quicksell.authorization import get_current_user
from quicksell.database import Session, get_session
from quicksell.exceptions import NotFound
from quicksell.models import Chat, Listing, Message, User
from quicksell.schemas import ChatRetrieve, MessageRetrieve

router = APIRouter(prefix='/chats', tags=['Chats'])

PAGE_SIZE = 30


def fetch_chat(
	uuid: str,
	user: User = Depends(get_current_user),
	db: Session = Depends(get_session)
):
	chat = db.query(Chat).filter(Chat.uuid == uuid).first()
	if not chat or user.profile not in chat.members:
		raise NotFound("Chat not found")
	return chat


@router.get('/', response_model=list[ChatRetrieve])
def get_chats(
	page: int = 0,
	user: User = Depends(get_current_user),
):
	return user.profile.chats.offset(page * PAGE_SIZE).limit(PAGE_SIZE).all()


@router.post('/', response_model=ChatRetrieve, status_code=HTTP_201_CREATED)
def create_chat(
	listing_uuid: str = Body(...),
	user: User = Depends(get_current_user),
	db: Session = Depends(get_session)
):
	listing = db.query(Listing).filter(Listing.uuid == listing_uuid).first()
	if not listing:
		raise NotFound("Listing not found")
	chat = user.profile.chats.filter(Chat.listing == listing).first()
	if not chat:
		chat = Chat.about_listing(listing)
		if user.profile is not listing.seller:
			chat.members.append(user.profile)
		db.add(chat, listing.seller)
		db.commit()
	return chat


@router.get('/{uuid}/', response_model=list[MessageRetrieve])
def get_chat_messages(
	page: int = 0,
	chat: Chat = Depends(fetch_chat)
):
	return chat.messages.offset(page * PAGE_SIZE).limit(PAGE_SIZE).all()


@router.post('/{uuid}/', response_model=MessageRetrieve, status_code=HTTP_201_CREATED)  # noqa
def create_message(
	text: str = Body(...),
	chat: Chat = Depends(fetch_chat),
	user: User = Depends(get_current_user),
	db: Session = Depends(get_session)
):
	message = Message(text=text, chat=chat, author=user.profile)
	chat.last_message = message
	db.add(message)
	db.commit()
	return message


@router.delete('/{uuid}/', response_class=Response, status_code=HTTP_204_NO_CONTENT)  # noqa
def delete_chat(
	chat: Chat = Depends(fetch_chat),
	db: Session = Depends(get_session)
):
	db.delete(chat)
	db.commit()
