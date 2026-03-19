from app.schemas.common import DataResponse, ErrorDetail, ErrorResponse


def test_data_response_serializes_to_envelope() -> None:
    """DataResponse must serialize with data field and null error."""
    response = DataResponse(data={"id": "abc", "status": "ok"})
    serialized = response.model_dump()
    assert serialized["data"] == {"id": "abc", "status": "ok"}
    assert serialized["error"] is None


def test_data_response_has_null_error_field() -> None:
    """DataResponse error field must be null (not missing)."""
    response = DataResponse(data="hello")
    serialized = response.model_dump()
    assert "error" in serialized
    assert serialized["error"] is None


def test_error_detail_default_details_is_empty_dict() -> None:
    """ErrorDetail.details must default to an empty dict."""
    detail = ErrorDetail(code="NOT_FOUND", message="Resource not found")
    assert detail.details == {}


def test_error_detail_with_custom_details() -> None:
    """ErrorDetail.details must accept arbitrary key-value pairs."""
    detail = ErrorDetail(
        code="VALIDATION_ERROR",
        message="Invalid input",
        details={"field": "email", "reason": "invalid format"},
    )
    assert detail.details["field"] == "email"


def test_error_response_serializes_to_envelope() -> None:
    """ErrorResponse must serialize with null data and populated error."""
    error_detail = ErrorDetail(code="NOT_FOUND", message="Resource not found")
    response = ErrorResponse(error=error_detail)
    serialized = response.model_dump()
    assert serialized["data"] is None
    assert serialized["error"]["code"] == "NOT_FOUND"
    assert serialized["error"]["message"] == "Resource not found"
    assert serialized["error"]["details"] == {}


def test_error_response_has_null_data_field() -> None:
    """ErrorResponse data field must be null (not missing)."""
    error_detail = ErrorDetail(code="SERVER_ERROR", message="Something went wrong")
    response = ErrorResponse(error=error_detail)
    serialized = response.model_dump()
    assert "data" in serialized
    assert serialized["data"] is None
