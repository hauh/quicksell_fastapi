"""Routes helpers."""

from contextlib import contextmanager
from typing import Type

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

from quicksell.exceptions import Conflict, Forbidden, NotFound, Unauthorized
from quicksell.models import UniqueViolation, User
from quicksell.schemas import HexUUID

TOKEN_URL = '../users/auth/'


def current_user(required: bool = True):
	oauth = OAuth2PasswordBearer(tokenUrl=TOKEN_URL, auto_error=required)

	async def fetch_user(token: str = Depends(oauth)) -> User:
		if user := User.scalar(User.access_token == token):
			return user
		if not required:
			return None
		raise Unauthorized()
	return fetch_user


def fetch(cls: Type, *filters):
	async def fetch_object(uuid: HexUUID):
		obj = cls.scalar(cls.uuid == uuid, *filters)
		if not obj:
			raise NotFound(cls.__name__ + " not found")
		return obj
	return fetch_object


def fetch_allowed(cls: Type, *filters):
	async def fetch_object(uuid: HexUUID, user: User = Depends(current_user())):
		obj = await fetch(cls, *filters)(uuid)
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
