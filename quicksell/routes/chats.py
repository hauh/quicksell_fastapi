"""api/chats/"""

from fastapi import Body, Depends, Response
from starlette.status import HTTP_201_CREATED, HTTP_204_NO_CONTENT

from quicksell.models import Chat, Listing, Message, Profile, User
from quicksell.notifications import notify_chat_members
from quicksell.router import Router
from quicksell.schemas import ChatRetrieve, HexUUID, MessageRetrieve

from .base import current_user, fetch, fetch_allowed

router = Router(prefix='/chats', tags=['Chats'])


@router.get('/', response_model=list[ChatRetrieve])
async def get_chats(
	page: int = 0,
	user: User = Depends(current_user)
):
	return Chat.paginate(
		Chat.members.any(Profile.id == user.profile.id),
		order_by=Chat.ts_update.desc(), page=page
	)


@router.post('/', response_model=ChatRetrieve, status_code=HTTP_201_CREATED)
async def create_chat(
	listing_uuid: HexUUID = Body(...),
	user: User = Depends(current_user)
):
	listing = await fetch(Listing)(listing_uuid)
	return (
		Chat.scalar(
			Chat.listing == listing,
			Chat.members.any(Profile.id == user.profile.id)
		)
		or Chat.insert(
			listing=listing, subject=listing.title,
			members=list({user.profile, listing.seller})
		)
	)


@router.get('/{uuid}/', response_model=list[MessageRetrieve])
async def get_chat_messages(
	page: int = 0,
	chat: Chat = Depends(fetch_allowed(Chat))
):
	return Message.paginate(
		Message.chat == chat, order_by=Message.ts_spawn.desc(), page=page
	)


@router.post('/{uuid}/', response_model=MessageRetrieve, status_code=HTTP_201_CREATED)  # noqa
async def create_message(
	text: str = Body(...),
	chat: Chat = Depends(fetch_allowed(Chat)),
	user: User = Depends(current_user)
):
	chat.last_message = Message.insert(text=text, chat=chat, author=user.profile)
	await notify_chat_members(chat)
	return chat.last_message


@router.delete('/{uuid}/', response_class=Response, status_code=HTTP_204_NO_CONTENT)  # noqa
async def delete_chat(chat: Chat = Depends(fetch_allowed(Chat))):
	chat.delete()
