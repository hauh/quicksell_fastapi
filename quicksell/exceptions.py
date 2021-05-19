"""API exceptions."""

from fastapi import HTTPException, status


class Unauthorized(HTTPException):
	"""401"""

	def __init__(self, detail: str = None, headers: dict = None):
		super().__init__(
			status.HTTP_401_UNAUTHORIZED,
			detail or "Invalid authentication credentials",
			headers or {"WWW-Authenticate": "Bearer"}
		)
