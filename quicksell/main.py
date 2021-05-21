"""App main."""

from fastapi import FastAPI

from quicksell.database import engine
from quicksell.models import Model
from quicksell.routes import listings_router, users_router

app = FastAPI(title="Quickell API", version='0.2')
app.include_router(users_router)
app.include_router(listings_router)


@app.on_event('startup')
def create_tables():
	Model.metadata.create_all(bind=engine)


@app.get('/', tags=['Info'])
def main():
	return "Quicksell API v0.2"
