"""Push notifications handler."""

from os import environ

from pyfcm import FCMNotification
from pyfcm.errors import FCMError

from quicksell.models import Chat, Device
from quicksell.schemas import MessageRetrieve

push_service = FCMNotification(api_key=environ['FCM_KEY'])


async def push(device: Device, title=None, body=None, data=None):
	if device.is_active:
		try:
			response = push_service.notify_single_device(
				registration_id=device.fcm_id,
				message_title=title,
				message_body=body,
				data_message=data
			)
		except FCMError:
			return
		if response['success'] != 1:
			device.fails_count += 1
			if device.fails_count >= Device.MAX_FAILS:
				device.is_active = False
		elif device.fails_count:
			device.fails_count = 0


async def notify_chat_members(chat: Chat):
	message = chat.last_message
	title = f"{message.author.name} @ {chat.subject}"
	data = {
		'type': 'chat_message',
		'chat': chat.uuid.hex,
		'message': MessageRetrieve.from_orm(message).json()
	}
	for profile in chat.members:
		if profile is not message.author:
			await push(profile.user.device, title, message.text, data)
