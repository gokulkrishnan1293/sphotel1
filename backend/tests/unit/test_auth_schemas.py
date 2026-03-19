"""Unit tests for auth schemas added in Story 2.5."""
import uuid

import pytest
from pydantic import ValidationError

from app.core.security.permissions import UserRole
from app.schemas.auth import AdminResetRequest, MeResponse, UpdateCredentialsRequest


# ── UpdateCredentialsRequest ──────────────────────────────────────────────────

def test_update_credentials_email_only_valid() -> None:
    req = UpdateCredentialsRequest(email="admin@example.com")
    assert req.email == "admin@example.com"
    assert req.password is None


def test_update_credentials_password_only_valid() -> None:
    req = UpdateCredentialsRequest(password="securePass123")
    assert req.password == "securePass123"
    assert req.email is None


def test_update_credentials_both_fields_valid() -> None:
    req = UpdateCredentialsRequest(email="new@test.com", password="newpass")
    assert req.email == "new@test.com"
    assert req.password == "newpass"


def test_update_credentials_both_none_raises() -> None:
    with pytest.raises(ValidationError) as exc_info:
        UpdateCredentialsRequest()
    errors = exc_info.value.errors()
    assert any(
        "At least one of email or password" in str(e["msg"]) for e in errors
    )


def test_update_credentials_invalid_email_raises() -> None:
    with pytest.raises(ValidationError):
        UpdateCredentialsRequest(email="not-an-email")


# ── AdminResetRequest ─────────────────────────────────────────────────────────

def test_admin_reset_email_only_valid() -> None:
    req = AdminResetRequest(email="admin@example.com")
    assert req.email == "admin@example.com"


def test_admin_reset_both_none_raises() -> None:
    with pytest.raises(ValidationError) as exc_info:
        AdminResetRequest()
    errors = exc_info.value.errors()
    assert any(
        "At least one of email or password" in str(e["msg"]) for e in errors
    )


# ── MeResponse ────────────────────────────────────────────────────────────────

class _FakeUser:
    user_id = uuid.uuid4()
    tenant_id = "sphotel"
    name = "Alice Admin"
    role = UserRole.ADMIN
    email = "alice@sphotel.com"
    is_active = True
    preferences: dict[str, object] = {}


def test_me_response_orm_mode() -> None:
    me = MeResponse.model_validate(_FakeUser())
    assert me.name == "Alice Admin"
    assert me.role == UserRole.ADMIN
    assert me.email == "alice@sphotel.com"
    assert me.is_active is True


def test_me_response_email_can_be_none() -> None:
    class _NoEmail(_FakeUser):
        email = None

    me = MeResponse.model_validate(_NoEmail())
    assert me.email is None


def test_me_response_no_password_field() -> None:
    me = MeResponse.model_validate(_FakeUser())
    assert not hasattr(me, "password_hash")
    assert not hasattr(me, "pin_hash")
