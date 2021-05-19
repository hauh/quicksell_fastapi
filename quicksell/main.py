"""App main."""

from fastapi import FastAPI

from quicksell.database import ModelBase, engine
from quicksell.routes import users_router

ModelBase.metadata.create_all(bind=engine)

app = FastAPI(title="Quickell API", version='0.2')
app.include_router(users_router)


@app.get('/', tags=['Info'])
def main():
	return "Quicksell API v0.2"
