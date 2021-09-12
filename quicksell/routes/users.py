"""api/users/"""

from fastapi import APIRouter, Body, Depends, Response
from fastapi.security import OAuth2PasswordRequestForm
from starlette.status import HTTP_201_CREATED, HTTP_204_NO_CONTENT

from quicksell.authorization import (
	check_password, generate_access_token, hash_password
)
from quicksell.exceptions import Unauthorized
from quicksell.models import Listing, Profile, User
from quicksell.schemas import (
	HexUUID, ListingRetrieve, ProfileRetrieve, ProfileUpdate, UserCreate,
	UserRetrieve
)

from .base import current_user, fetch, unique_violation_check

router = APIRouter(prefix='/users', tags=['Users'])


@router.get('/', response_model=UserRetrieve)
async def get_current_user(user: User = Depends(current_user)):
	return user


@router.post('/', response_model=UserRetrieve, status_code=HTTP_201_CREATED)
async def create_user(body: UserCreate):
	with unique_violation_check():
		return User.insert(
			email=body.email,
			password_hash=hash_password(body.password),
			access_token=generate_access_token(body.email),
			profile=Profile(phone=body.phone, name=body.name),
		)


@router.patch('/', response_model=ProfileRetrieve)
async def update_profile(
	body: ProfileUpdate,
	user: User = Depends(current_user)
):
	with unique_violation_check():
		return user.profile.update(**body.dict())


@router.post('/auth/')
async def login(auth: OAuth2PasswordRequestForm = Depends()):
	user = User.scalar(User.email == auth.username)
	if not user or not check_password(auth.password, user.password_hash):
		raise Unauthorized()
	user.access_token = generate_access_token(auth.username)
	return {'access_token': user.access_token}


@router.get('/favorites/', response_model=list[ListingRetrieve])
async def get_favorites(user: User = Depends(current_user)):
	return user.favorites


@router.put('/favorites/', response_class=Response)
async def add_to_favorites(
	listing_uuid: HexUUID = Body(...),
	user: User = Depends(current_user)
):
	listing = await fetch(Listing)(listing_uuid)
	user.favorites.append(listing)


@router.delete('/favorites/', response_class=Response, status_code=HTTP_204_NO_CONTENT)  # noqa
async def remove_from_favorites(
	listing_uuid: HexUUID = Body(...),
	user: User = Depends(current_user)
):
	listing = await fetch(Listing)(listing_uuid)
	try:
		user.favorites.remove(listing)
	except ValueError:
		pass


@router.get('/{uuid}/')
async def get_profile(profile: Profile = Depends(fetch(Profile))):
	return profile
