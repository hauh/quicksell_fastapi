"""API exceptions."""

from fastapi import HTTPException, status


class BadRequest(HTTPException):
	"""400"""

	def __init__(self, detail: str = None, headers: dict = None):
		super().__init__(
			status.HTTP_400_BAD_REQUEST,
			detail or "Bad request",
			headers
		)


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
			detail or "Resource not found",
			headers
		)


class Conflict(HTTPException):
	"""409"""

	def __init__(self, detail: str = None, headers: dict = None):
		super().__init__(
			status.HTTP_409_CONFLICT,
			detail or "Resource already exists",
			headers
		)
