from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class ErrorDetail(BaseModel):
    """Error detail for API error responses."""

    code: str
    message: str
    details: dict[str, object] = {}


class DataResponse(BaseModel, Generic[T]):  # noqa: UP046
    """Envelope for successful API responses: {"data": ..., "error": null}."""

    data: T
    error: None = None


class ErrorResponse(BaseModel):
    """Envelope for error API responses: {"data": null, "error": {...}}."""

    data: None = None
    error: ErrorDetail


class MessageResponse(BaseModel):
    """Simple message payload for mutation confirmations."""

    message: str
