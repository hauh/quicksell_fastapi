"""API authorization."""

import os
from time import time

import bcrypt
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import jwt

from quicksell.database import Session, get_session
from quicksell.exceptions import Unauthorized
from quicksell.models import User

SECRET_KEY = os.environ['SECRET_KEY']

authorization = OAuth2PasswordBearer(tokenUrl='/users/auth/')


def hash_password(password: str) -> str:
	return bcrypt.hashpw(password.strip().encode(), bcrypt.gensalt()).decode()


def check_password(password: str, hashed: str) -> bool:
	return bcrypt.checkpw(password.encode(), hashed.encode())


def generate_access_token(email: str) -> str:
	return jwt.encode({'email': email, 'ts': int(time())}, SECRET_KEY)


def get_current_user(
	token: str = Depends(authorization),
	db: Session = Depends(get_session)
) -> User:
	user = db.query(User).filter(User.access_token == token).first()
	if not user:
		raise Unauthorized()
	return user
