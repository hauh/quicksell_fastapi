"""Custom FastAPI route class for managing DB session in routes."""

from typing import Callable

from fastapi import Request, Response
from fastapi.routing import APIRoute, APIRouter

from quicksell.database import Database


class DBSessionAPIRoute(APIRoute):
    """Starts session before entering route."""

    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()

        async def database_session_route_hander(request: Request) -> Response:
            with Database.start_session():
                return await original_route_handler(request)

        return database_session_route_hander


class Router(APIRouter):
    """API router with custom route class."""

    def __init__(self, *args, **kwargs):
        kwargs['route_class'] = DBSessionAPIRoute
        super().__init__(*args, **kwargs)
