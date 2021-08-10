"""App main."""

import json

from fastapi import FastAPI

from quicksell.database import Database
from quicksell.models import Category
from quicksell.routes import (
	chats_router, listings_router, shops_router, users_router
)

app = FastAPI(
	title="Quickell API",
	version='0.5.0',
	openapi_url='/doc/openapi.json',
	docs_url='/doc/swagger',
	redoc_url='/doc/redoc'
)

app.include_router(chats_router)
app.include_router(listings_router)
app.include_router(shops_router)
app.include_router(users_router)


@app.on_event('startup')
def init_db():
	Database.connect()
	Database.create_tables()


@app.on_event('startup')
def create_categories():
	with Database.start_session():
		if not Category.scalar():
			with open('assets/categories.json', encoding='utf-8') as categories_file:
				categories_json = json.load(categories_file)
				Category.populate_table(categories_json)
	Category.setup_events()


@app.middleware('http')
async def db_session(request, call_next):
	with Database.start_session():
		return await call_next(request)


@app.get('/', tags=['Info'])
async def main():
	return f"{app.title} {app.version}"
