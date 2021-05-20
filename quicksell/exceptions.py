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


class Forbidden(HTTPException):
	"""403"""

	def __init__(self, detail: str = None, headers: dict = None):
		super().__init__(
			status.HTTP_403_FORBIDDEN,
			detail or "Access denied",
			headers
		)


class NotFound(HTTPException):
	"""404"""

	def __init__(self, detail: str = None, headers: dict = None):
		super().__init__(
			status.HTTP_404_NOT_FOUND,
			detail or "Object not found",
			headers
		)
