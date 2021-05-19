"""api/users/"""

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from quicksell.authorization import (
	check_password, generate_access_token, get_current_user, hash_password
)
from quicksell.database import Session, get_session
from quicksell.exceptions import Unauthorized
from quicksell.models import Device, Profile, User
from quicksell.schemas import UserCreate, UserRetrieve

router = APIRouter(prefix='/users', tags=['Users'])


@router.get('/', response_model=UserRetrieve)
def current_user(user: User = Depends(get_current_user)):
	return user


@router.post('/', response_model=UserRetrieve)
def create_user(body: UserCreate, db: Session = Depends(get_session)):
	if profile := db.query(Profile).filter(Profile.phone == body.phone).first():
		return profile.user
	if device := db.query(Device).filter(Device.fcm_id == body.fcm_id).first():
		device.is_active = True
		device.fails_count = 0
		db.commit()
		return device.owner
	user = User(
		email=body.email,
		password_hash=hash_password(body.password),
		access_token=generate_access_token(body.email),
		profile=Profile(phone=body.phone, full_name=body.full_name),
		device=Device(fcm_id=body.fcm_id)
	)
	db.add(user)
	db.commit()
	return user


@router.post('/auth/')
def login(
	auth: OAuth2PasswordRequestForm = Depends(),
	db: Session = Depends(get_session)
):
	user = db.query(User).filter(User.email == auth.username).first()
	if not user or not check_password(auth.password, user.password_hash):
		raise Unauthorized()
	user.access_token = generate_access_token(auth.username)
	db.commit()
	return {'access_token': user.access_token}
