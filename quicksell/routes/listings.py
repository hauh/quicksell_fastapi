"""api/listings/"""

from fastapi import APIRouter, Depends, Response
from starlette.status import HTTP_201_CREATED, HTTP_204_NO_CONTENT

from quicksell.authorization import get_current_user
from quicksell.database import Session, get_session
from quicksell.exceptions import Forbidden, NotFound
from quicksell.models import Listing, Profile, User
from quicksell.schemas import ListingCreate, ListingRetrieve, ListingUpdate

router = APIRouter(prefix='/listings', tags=['Listings'])

PAGE_SIZE = 20


def fetch_listing(uuid: str, db: Session = Depends(get_session)):
	listing = db.query(Listing).filter(Listing.uuid == uuid).first()
	if not listing:
		raise NotFound("Listing not found")
	return listing


@router.get('/', response_model=list[ListingRetrieve])
def get_listings_list(  # pylint: disable=too-many-arguments
	title: str = None,
	min_price: int = None,
	max_price: int = None,
	is_new: bool = None,
	category: str = None,
	seller: str = None,
	order_by: str = None,
	page: int = 0,
	db: Session = Depends(get_session)
):
	query = db.query(Listing).join(Profile)

	filters = []
	if title and len(title) > 3:
		filters.append(Listing.title.like(f'%{title}%'))
	if min_price is not None and min_price >= 0:
		filters.append(Listing.price >= min_price)
	if max_price is not None and max_price >= 0:
		filters.append(Listing.price <= max_price)
	if is_new is not None:
		filters.append(Listing.is_new == is_new)
	if category:
		filters.append(Listing.category == category)
	if seller:
		filters.append(Profile.uuid == seller)
	query = query.filter(*filters)

	if order_by and (order := getattr(Listing, order_by.removeprefix('-'), None)):
		order = order.desc() if order_by.startswith('-') else order.asc()
	else:
		order = Listing.ts_spawn.desc()
	query = query.order_by(order)

	return query.offset(page * PAGE_SIZE).limit(PAGE_SIZE).all()


@router.post('/', response_model=ListingRetrieve, status_code=HTTP_201_CREATED)
def create_listing(
	body: ListingCreate,
	user: User = Depends(get_current_user),
	db: Session = Depends(get_session)
):
	params = body.dict(exclude_unset=True, exclude_none=True)
	listing = Listing(**params, seller=user.profile)
	db.add(listing)
	db.commit()
	return listing


@router.get('/{uuid}/', response_model=ListingRetrieve)
def get_listing(listing: Listing = Depends(fetch_listing)):
	return listing


@router.patch('/{uuid}/', response_model=ListingRetrieve)
def update_listing(
	body: ListingUpdate,
	listing: Listing = Depends(fetch_listing),
	user: User = Depends(get_current_user),
	db: Session = Depends(get_session)
):
	if listing.seller is not user.profile:
		raise Forbidden()
	params = body.dict(exclude_unset=True, exclude_none=True)
	for field, value in params.items():
		setattr(listing, field, value)
	db.commit()
	return listing


@router.delete('/{uuid}/', response_class=Response, status_code=HTTP_204_NO_CONTENT)  # noqa
def delete_listing(
	listing: Listing = Depends(fetch_listing),
	user: User = Depends(get_current_user),
	db: Session = Depends(get_session)
):
	if listing.seller is not user.profile:
		raise Forbidden()
	db.delete(listing)
	db.commit()
