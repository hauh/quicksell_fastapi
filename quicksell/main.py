"""App main."""

import json

from fastapi import FastAPI

from quicksell.database import engine, session_maker
from quicksell.models import Category, Model
from quicksell.routes import chats_router, listings_router, users_router

app = FastAPI(title="Quickell API", version='0.2.6')
app.include_router(chats_router)
app.include_router(listings_router)
app.include_router(users_router)


@app.on_event('startup')
def create_tables():
	Model.metadata.create_all(bind=engine)


@app.on_event('startup')
def create_categories():
	with session_maker(autoflush=True) as session:
		session.query(Category).delete()
		with open('categories.json', encoding='utf-8') as categories_file:
			categories_json = json.load(categories_file)
			for category in Category.tree_generator(categories_json):
				session.add(category)
				session.flush()
		session.commit()
	Category.setup_events()


@app.get('/', tags=['Info'])
def main():
	return "Quicksell API v0.2"
