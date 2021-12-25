"""App main."""

from os import environ

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from quicksell.routes import (
	chats_router, listings_router, offers_router, shops_router, users_router
)

app = FastAPI(
	title="Quickell API",
	version='0.7.3',
	openapi_url='/doc/openapi.json',
	docs_url='/doc/swagger',
	redoc_url='/doc/redoc',
	root_path=environ.get('ROOT_PATH', '')
)

app.include_router(chats_router)
app.include_router(listings_router)
app.include_router(offers_router)
app.include_router(shops_router)
app.include_router(users_router)

app.mount('/media', StaticFiles(directory='media'), name='media')


@app.get('/', tags=['Info'])
async def main():
	return f"{app.title} {app.version}"
