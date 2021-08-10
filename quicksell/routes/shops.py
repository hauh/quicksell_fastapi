"""api/shops/"""

from fastapi import APIRouter, Depends
from sqlalchemy.exc import IntegrityError
from starlette.status import HTTP_201_CREATED

from quicksell.exceptions import BadRequest, Conflict
from quicksell.models import Company, Shop, User
from quicksell.schemas import (
	CompanyCreate, CompanyRetrieve, ShopCreate, ShopRetrieve
)

from .base import current_user, fetch

router = APIRouter(prefix='/shops', tags=['Shops'])


@router.get('/', response_model=list[ShopRetrieve])
async def get_shops_list():
	return Shop.select()


@router.post('/', response_model=ShopRetrieve, status_code=HTTP_201_CREATED)
async def create_shop(
	body: ShopCreate,
	user: User = Depends(current_user)
):
	if not user.company:
		raise BadRequest("User doesn't have a company")
	try:
		return Shop.insert(**body.dict(), company=user.company)
	except IntegrityError as e:
		raise Conflict(e.orig.diag.message_detail) from e


@router.post('/companies/', response_model=CompanyRetrieve, status_code=HTTP_201_CREATED)  # noqa
async def create_company(
	body: CompanyCreate,
	user: User = Depends(current_user)
):
	if user.company:
		raise Conflict("User already has a company")
	try:
		return Company.insert(**body.dict(), owner=user)
	except IntegrityError as e:
		raise Conflict(e.orig.diag.message_detail) from e


@router.get('/companies/{uuid}/', response_model=CompanyRetrieve)
async def get_company(company: Company = Depends(fetch(Company))):
	return company


@router.get('/{uuid}/', response_model=ShopRetrieve)
async def get_shop(shop: Shop = Depends(fetch(Shop))):
	return shop
