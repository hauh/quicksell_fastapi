"""API authorization."""

from os import environ
from time import time

import bcrypt
from jose import jwt

SECRET_KEY = environ['SECRET_KEY']


def hash_password(password: str) -> str:
	return bcrypt.hashpw(password.strip().encode(), bcrypt.gensalt()).decode()


def check_password(password: str, hashed: str) -> bool:
	return bcrypt.checkpw(password.encode(), hashed.encode())


def generate_access_token(email: str) -> str:
	return jwt.encode({'email': email, 'ts': int(time())}, SECRET_KEY)
