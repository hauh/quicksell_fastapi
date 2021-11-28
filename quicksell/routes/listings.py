"""api/listings/"""

from time import time

from fastapi import Depends, Query, Request, Response
from starlette.status import HTTP_201_CREATED, HTTP_204_NO_CONTENT

from quicksell.exceptions import BadRequest
from quicksell.models import (
	Category, Listing, Profile, UniqueViolation, User, View
)
from quicksell.router import Router
from quicksell.schemas import (
	HexUUID, ListingCreate, ListingRetrieve, ListingUpdate
)

from .base import current_user, fetch, fetch_allowed

router = Router(prefix='/listings', tags=['Listings'])


@router.get('/', response_model=list[ListingRetrieve])
async def get_listings_list(
	# pylint: disable=too-many-arguments
	user: User = Depends(current_user(required=False)),
	title: str = None,
	min_price: int = None,
	max_price: int = None,
	is_new: bool = None,
	category: list[str] = Query(None),
	seller_uuid: HexUUID = None,
	distance: int = None,
	latitude: float = None,
	longitude: float = None,
	order_by: str = '-ts_spawn',
	page: int = 0
):
	filters = []
	if title and len(title) >= 3:
		filters.append(Listing.title.ilike(f'%{title}%'))
	if min_price is not None and min_price >= 0:
		filters.append(Listing.price >= min_price)
	if max_price is not None and max_price >= 0:
		filters.append(Listing.price <= max_price)
	if is_new is not None:
		filters.append(Listing.is_new == is_new)
	if category:
		filters.append(Listing.category_id == Category.id)
		filters.append(Category.name.in_(category))
	if seller_uuid:
		filters.append(Listing.seller_id == Profile.id)
		filters.append(Profile.uuid == seller_uuid)
	if distance and latitude and longitude:
		if order_by.removeprefix('-') == 'distance':
			return Listing.ordered_by_distance(
				latitude, longitude, distance,
				*filters, desc=order_by.startswith('-'), page=page
			)
		filters.append(Listing.in_range(latitude, longitude, distance)[0])
	if not user or not user.company:
		ts_filter = Listing.ts_spawn < int(time()) - Listing.PUBLICATION_DELAY
		if user and not seller_uuid:
			ts_filter |= Listing.seller_id == user.profile.id
		filters.append(ts_filter)
	return Listing.paginate(*filters, order_by=order_by, page=page)


@router.post('/', response_model=ListingRetrieve, status_code=HTTP_201_CREATED)
async def create_listing(
	body: ListingCreate,
	user: User = Depends(current_user())
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
async def get_listing(
	request: Request,
	listing: Listing = Depends(fetch(Listing))
):
	ip = request.client.host
	try:
		View.insert(listing_id=listing.id, ip=ip)
	except UniqueViolation:
		pass
	else:
		listing.views += 1
	return listing


@router.patch('/{uuid}/', response_model=ListingRetrieve)
async def update_listing(
	body: ListingUpdate,
	listing: Listing = Depends(fetch_allowed(Listing))
):
	params = body.dict()
	if category_name := params.get('category'):
		category = Category.scalar(Category.name == category_name)
		if not category or not category.assignable:
			raise BadRequest("Invalid category")
		params['category'] = category
	return listing.update(**params)


@router.delete('/{uuid}/', response_class=Response, status_code=HTTP_204_NO_CONTENT)  # noqa
async def delete_listing(listing: Listing = Depends(fetch_allowed(Listing))):
	listing.delete()
