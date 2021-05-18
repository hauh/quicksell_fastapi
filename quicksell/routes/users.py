"""api/users/"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm.session import Session

from quicksell.database import session
from quicksell.models import User
from quicksell.schemas import UserRetrieve

router = APIRouter(prefix='/users')


@router.get('/', response_model=list[UserRetrieve])
def users_list(db: Session = Depends(session)):
	return db.query(User).all()
