"""api/offers/"""

from fastapi import Body, Depends, Response
from starlette.status import HTTP_201_CREATED, HTTP_204_NO_CONTENT

from quicksell.exceptions import BadRequest, Conflict, Forbidden
from quicksell.models import Listing, Offer, User
from quicksell.router import Router
from quicksell.schemas import OfferCreate, OfferRetrieve, OfferUpdate

from .base import current_user, fetch, fetch_allowed

router = Router(prefix='/offers', tags=['Offers'])


@router.get('/', response_model=list[OfferRetrieve])
async def get_offers_list(user: User = Depends(current_user)):
	if user.company:
		where = [Offer.company == user.company]
	else:
		where = [Offer.listing_id == Listing.id, Listing.seller == user.profile]
	return Offer.paginate(*where, Offer.active)


@router.post('/', response_model=OfferRetrieve, status_code=HTTP_201_CREATED)
async def create_offer(
	body: OfferCreate,
	user: User = Depends(current_user)
):
	if not user.company:
		raise BadRequest("You must register a company first")
	params = body.dict()
	listing = await fetch(Listing)(params.pop('listing_uuid'))
	if listing.seller is user.profile:
		raise BadRequest("You can't make offers for your own listing")
	if Offer.scalar(
		Offer.listing_id == listing.id,
		Offer.company_id == user.company.id,
		Offer.active
	):
		raise Conflict("You've already made an offer for the listing")
	return Offer.insert(**params, listing=listing, company=user.company)


@router.patch('/{uuid}/', response_model=OfferRetrieve)
async def update_offer(
	body: OfferUpdate,
	offer: Offer = Depends(fetch_allowed(Offer, Offer.active))
):
	if offer.accepted:
		raise BadRequest("Offer has already been accepted")
	return offer.update(**body.dict())


@router.put('/{uuid}/', response_class=Response)
async def accept_offer(
	accept: bool = Body(..., embed=True),
	offer: Offer = Depends(fetch(Offer, Offer.active, Offer.accepted.is_(None))),
	user: User = Depends(current_user)
):
	if user.profile is not offer.listing.seller:
		raise Forbidden("Offer is not for you")
	if accept:
		offer.update(accepted=True)
	else:
		offer.update(accepted=False, active=False)


@router.delete('/{uuid}/', response_class=Response, status_code=HTTP_204_NO_CONTENT)  # noqa
async def delete_offer(
	offer: Offer = Depends(fetch_allowed(Offer, Offer.active))
):
	offer.update(active=False)
