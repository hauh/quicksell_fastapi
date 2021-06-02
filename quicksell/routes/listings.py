"""api/listings/"""

from fastapi import APIRouter, Depends, Response
from starlette.status import HTTP_201_CREATED, HTTP_204_NO_CONTENT

from quicksell.authorization import get_current_user
from quicksell.database import Session, get_session
from quicksell.exceptions import BadRequest, Forbidden, NotFound
from quicksell.models import Category, Listing, Profile, User
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
	query = db.query(Listing)
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
		query = query.join(Category, Listing.category_id == Category.id)
		filters.append(Category.name == category)
	if seller:
		query = query.join(Profile, Listing.seller_id == Profile.id)
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
	params = body.dict()
	params['location'] = params.get('location') or user.profile.location
	if not params['location']:
		raise BadRequest("Location not provided and user didn't set a default one")
	category_name = params.pop('category')
	category = db.query(Category).filter(Category.name == category_name).first()
	if not category or not category.assignable:
		raise BadRequest("Invalid category")
	listing = Listing(**params, category=category, seller=user.profile)
	db.add(listing)
	db.commit()
	return listing


@router.get('/categories/')
def categories_tree(db: Session = Depends(get_session)):
	if Category.cached_tree:
		return Category.cached_tree
	categories = {cat.id: cat for cat in db.query(Category).all()}
	tree = {}
	for category in categories.values():
		category_branch = {}
		tree[category.name] = category_branch
		if category.parent_id:
			parent_name = categories[category.parent_id].name
			tree.setdefault(parent_name, {})[category.name] = category_branch
	for category in categories.values():
		if category.parent_id:
			tree.pop(category.name)
	Category.cached_tree = tree
	return tree


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
	params = body.dict()
	for field, value in params.items():  # TODO: validate category
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
