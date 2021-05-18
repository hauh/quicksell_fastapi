"""App main."""

from fastapi import FastAPI

from quicksell.database import ModelBase, engine
from quicksell.routes import users_router

ModelBase.metadata.create_all(bind=engine)

app = FastAPI()
app.include_router(users_router)


@app.get('/')
def main():
	return "Quicksell API v0.1"
