"""api/listings/"""

from fastapi import APIRouter, Depends, Response
from starlette.status import HTTP_201_CREATED, HTTP_204_NO_CONTENT

from quicksell.authorization import get_current_user
from quicksell.exceptions import BadRequest, Forbidden, NotFound
from quicksell.models import Category, Listing, Profile, User
from quicksell.schemas import (
	HexUUID, ListingCreate, ListingRetrieve, ListingUpdate
)

router = APIRouter(prefix='/listings', tags=['Listings'])


async def fetch_listing(uuid: HexUUID):
	listing = Listing.scalar(Listing.uuid == uuid)
	if not listing:
		raise NotFound("Listing not found")
	return listing


@router.get('/', response_model=list[ListingRetrieve])
async def get_listings_list(  # pylint: disable=too-many-arguments
	title: str = None,
	min_price: int = None,
	max_price: int = None,
	is_new: bool = None,
	category: str = None,
	seller: HexUUID = None,
	order_by: str = None,
	page: int = 0
):
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
		join = (Listing.category_id == Category.id, Category.name == category)
		filters.extend(join)
	if seller:
		join = (Listing.seller_id == Profile.id, Profile.uuid == seller)
		filters.extend(join)

	if order_by and (order := getattr(Listing, order_by.removeprefix('-'), None)):
		order = order.desc() if order_by.startswith('-') else order.asc()
	else:
		order = Listing.ts_spawn.desc()

	return Listing.paginate(*filters, order_by=order, page=page)


@router.post('/', response_model=ListingRetrieve, status_code=HTTP_201_CREATED)
async def create_listing(
	body: ListingCreate,
	user: User = Depends(get_current_user)
):
	params = body.dict()
	location = params.pop('location', user.profile.location)
	if not location:
		raise BadRequest("Location not provided and user didn't set a default one")
	category = Category.scalar(Category.name == params.pop('category'))
	if not category or not category.assignable:
		raise BadRequest("Invalid category")
	return Listing.insert(
		**params, location=location, category=category, seller=user.profile
	)


@router.get('/categories/')
async def categories_tree():
	if Category.cached_tree:
		return Category.cached_tree
	categories = {cat.id: cat for cat in Category.select()}
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
async def get_listing(listing: Listing = Depends(fetch_listing)):
	return listing


@router.patch('/{uuid}/', response_model=ListingRetrieve)
async def update_listing(
	body: ListingUpdate,
	listing: Listing = Depends(fetch_listing),
	user: User = Depends(get_current_user)
):
	if listing.seller is not user.profile:
		raise Forbidden()
	params = body.dict()
	if category_name := params.get('category'):
		category = Category.scalar(Category.name == category_name)
		if not category or not category.assignable:
			raise BadRequest("Invalid category")
		params['category'] = category
	listing.update(**params)
	return listing


@router.delete('/{uuid}/', response_class=Response, status_code=HTTP_204_NO_CONTENT)  # noqa
async def delete_listing(
	listing: Listing = Depends(fetch_listing),
	user: User = Depends(get_current_user)
):
	if listing.seller is not user.profile:
		raise Forbidden()
	listing.delete()
