"""api/shops/"""

from fastapi import Depends
from starlette.status import HTTP_201_CREATED

from quicksell.exceptions import BadRequest, Conflict
from quicksell.models import Company, Shop, User
from quicksell.router import Router
from quicksell.schemas import (
	CompanyCreate, CompanyRetrieve, ShopCreate, ShopRetrieve
)

from .base import current_user, fetch, unique_violation_check

router = Router(prefix='/shops', tags=['Shops'])


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
	with unique_violation_check():
		return Shop.insert(**body.dict(), company=user.company)


@router.post('/companies/', response_model=CompanyRetrieve, status_code=HTTP_201_CREATED)  # noqa
async def create_company(
	body: CompanyCreate,
	user: User = Depends(current_user)
):
	if user.company:
		raise Conflict("User already has a company")
	with unique_violation_check():
		return Company.insert(**body.dict(), owner=user)


@router.get('/companies/{uuid}/', response_model=CompanyRetrieve)
async def get_company(company: Company = Depends(fetch(Company))):
	return company


@router.get('/{uuid}/', response_model=ShopRetrieve)
async def get_shop(shop: Shop = Depends(fetch(Shop))):
	return shop
