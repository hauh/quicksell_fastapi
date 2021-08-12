"""api/users/"""

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from starlette.status import HTTP_201_CREATED

from quicksell.authorization import (
	check_password, generate_access_token, hash_password
)
from quicksell.exceptions import Conflict, Unauthorized
from quicksell.models import Device, Profile, User
from quicksell.schemas import UserCreate, UserRetrieve

from .base import current_user, fetch

router = APIRouter(prefix='/users', tags=['Users'])


@router.get('/', response_model=UserRetrieve)
async def get_current_user(user: User = Depends(current_user)):
	return user


@router.post('/', response_model=UserRetrieve, status_code=HTTP_201_CREATED)
async def create_user(body: UserCreate):
	if User.scalar(User.email == body.email):
		raise Conflict("User with this email already exists")
	if Profile.scalar(Profile.phone == body.phone):
		raise Conflict("User with this phone number already exists")
	if Device.scalar(Device.fcm_id == body.fcm_id):
		# raise Conflict("Registration from this device has already been done")
		pass
	return User.insert(
		email=body.email,
		password_hash=hash_password(body.password),
		access_token=generate_access_token(body.email),
		profile=Profile(phone=body.phone, name=body.name),
		# device=Device(fcm_id=body.fcm_id)
	)


@router.post('/auth/')
async def login(auth: OAuth2PasswordRequestForm = Depends()):
	user = User.scalar(User.email == auth.username)
	if not user or not check_password(auth.password, user.password_hash):
		raise Unauthorized()
	user.access_token = generate_access_token(auth.username)
	return {'access_token': user.access_token}


@router.get('/{uuid}/')
async def get_profile(profile: Profile = Depends(fetch(Profile))):
	return profile
