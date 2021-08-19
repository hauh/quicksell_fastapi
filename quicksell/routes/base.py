"""Routes helpers."""

from contextlib import contextmanager
from typing import Type

from fastapi import Depends

from quicksell.authorization import authorization
from quicksell.exceptions import Conflict, Forbidden, NotFound, Unauthorized
from quicksell.models import UniqueViolation, User
from quicksell.schemas import HexUUID


async def current_user(token: str = Depends(authorization)) -> User:
	user = User.scalar(User.access_token == token)
	if not user:
		raise Unauthorized()
	return user


def fetch(cls: Type):
	async def fetch_object(uuid: HexUUID):
		obj = cls.scalar(cls.uuid == uuid)
		if not obj:
			raise NotFound(cls.__name__ + " not found")
		return obj
	return fetch_object


def fetch_allowed(cls: Type):
	async def fetch_object(uuid: HexUUID, user: User = Depends(current_user)):
		obj = await fetch(cls)(uuid)
		if not obj.allowed(user):
			raise Forbidden()
		return obj
	return fetch_object


@contextmanager
def unique_violation_check():
	try:
		yield
	except UniqueViolation as e:
		raise Conflict(str(e)) from e
