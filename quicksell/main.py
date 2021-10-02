"""App main."""

from fastapi import FastAPI

from quicksell.database import Database
from quicksell.routes import (
	chats_router, listings_router, shops_router, users_router
)

app = FastAPI(
	title="Quickell API",
	version='0.6.5',
	openapi_url='/doc/openapi.json',
	docs_url='/doc/swagger',
	redoc_url='/doc/redoc'
)

app.include_router(chats_router)
app.include_router(listings_router)
app.include_router(shops_router)
app.include_router(users_router)


@app.middleware('http')
async def db_session(request, call_next):
	with Database.start_session():
		return await call_next(request)


@app.get('/', tags=['Info'])
async def main():
	return f"{app.title} {app.version}"
