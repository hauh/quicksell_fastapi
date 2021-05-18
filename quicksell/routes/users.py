"""api/users/"""

import bcrypt
from fastapi import APIRouter, Depends
from sqlalchemy.orm.session import Session

from quicksell.database import session
from quicksell.models import User, Profile, Device
from quicksell.schemas import UserCreate, UserRetrieve

router = APIRouter(prefix='/users')


@router.get('/', response_model=list[UserRetrieve])
def users_list(db: Session = Depends(session)):
	return db.query(User).all()


@router.post('/', response_model=UserRetrieve)
def user_create(body: UserCreate, db: Session = Depends(session)):
	if profile := db.query(Profile).filter(Profile.phone == body.phone).first():
		return profile.user
	if device := db.query(Device).filter(Device.fcm_id == body.fcm_id).first():
		device.is_active = True
		device.fails_count = 0
		db.commit()
		return device.owner
	user = User(
		email=body.email,
		password_hash=password_hash(body.password),
		profile=Profile(phone=body.phone, full_name=body.full_name),
		device=Device(fcm_id=body.fcm_id)
	)
	db.add(user)
	db.commit()
	return user


def password_hash(password):
	return bcrypt.hashpw(password.strip().encode(), bcrypt.gensalt())
