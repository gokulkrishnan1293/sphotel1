import json

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException


async def http_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Format HTTP exceptions into the standard error envelope."""
    status_code = 500
    detail = "Internal server error"
    if isinstance(exc, StarletteHTTPException):
        status_code = exc.status_code
        detail = str(exc.detail)
    return JSONResponse(
        status_code=status_code,
        content={
            "data": None,
            "error": {"code": str(status_code), "message": detail, "details": {}},
        },
    )


async def validation_exception_handler(
    request: Request, exc: Exception
) -> JSONResponse:
    """Format Pydantic validation errors into the standard error envelope."""
    errors: list[object] = []
    if isinstance(exc, RequestValidationError):
        # Pydantic v2 model_validator errors include non-serializable objects in
        # ctx (e.g., the raw ValueError). Convert to a JSON-safe representation.
        errors = json.loads(json.dumps(exc.errors(), default=str))
    return JSONResponse(
        status_code=422,
        content={
            "data": None,
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Request validation failed",
                "details": {"errors": errors},
            },
        },
    )


async def internal_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Format unhandled exceptions into the standard error envelope."""
    return JSONResponse(
        status_code=500,
        content={
            "data": None,
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred",
                "details": {},
            },
        },
    )
