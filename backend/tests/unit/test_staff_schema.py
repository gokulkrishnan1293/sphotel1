import uuid
from datetime import datetime, timezone

import pytest

from app.core.security.permissions import UserRole
from app.schemas.staff import CreateStaffRequest, ResetPinRequest, StaffResponse


def test_create_staff_request_valid() -> None:
    req = CreateStaffRequest(name="Alice", role=UserRole.BILLER, pin="1234")
    assert req.name == "Alice"
    assert req.role == UserRole.BILLER
    assert req.pin == "1234"


def test_create_staff_request_rejects_short_pin() -> None:
    with pytest.raises(Exception):
        CreateStaffRequest(name="Bob", role=UserRole.WAITER, pin="123")


def test_create_staff_request_rejects_long_pin() -> None:
    with pytest.raises(Exception):
        CreateStaffRequest(name="Bob", role=UserRole.WAITER, pin="123456789")


def test_create_staff_request_rejects_empty_name() -> None:
    with pytest.raises(Exception):
        CreateStaffRequest(name="", role=UserRole.BILLER, pin="1234")


def test_reset_pin_request_valid() -> None:
    req = ResetPinRequest(pin="5678")
    assert req.pin == "5678"


def test_reset_pin_request_rejects_short_pin() -> None:
    with pytest.raises(Exception):
        ResetPinRequest(pin="12")


def test_staff_response_from_orm() -> None:
    """StaffResponse can be built from an ORM-like object via model_validate."""

    class FakeUser:
        id = uuid.uuid4()
        tenant_id = "sphotel"
        name = "Charlie"
        role = UserRole.KITCHEN_STAFF
        is_active = True
        created_at = datetime(2026, 1, 1, tzinfo=timezone.utc)

    resp = StaffResponse.model_validate(FakeUser())
    assert resp.name == "Charlie"
    assert resp.role == UserRole.KITCHEN_STAFF
    assert resp.is_active is True
    assert resp.tenant_id == "sphotel"


def test_staff_response_does_not_expose_credentials() -> None:
    """StaffResponse schema must not contain pin_hash or password_hash fields."""
    fields = StaffResponse.model_fields
    assert "pin_hash" not in fields
    assert "password_hash" not in fields
    assert "totp_secret" not in fields
