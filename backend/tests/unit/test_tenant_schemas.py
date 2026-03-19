"""Unit tests for tenant schemas added in Story 3.1."""
import pytest
from pydantic import ValidationError

from app.schemas.tenant import TenantCreateRequest


def test_valid_request() -> None:
    req = TenantCreateRequest(
        name="Spice Garden",
        subdomain="spicegarden",
        admin_email="admin@spicegarden.com",
        admin_password="securepass",
    )
    assert req.subdomain == "spicegarden"
    assert req.name == "Spice Garden"


def test_subdomain_uppercased_is_lowercased() -> None:
    req = TenantCreateRequest(
        name="Test",
        subdomain="SpiceGarden",
        admin_email="x@x.com",
        admin_password="12345678",
    )
    assert req.subdomain == "spicegarden"


def test_subdomain_with_hyphen_valid() -> None:
    req = TenantCreateRequest(
        name="Test",
        subdomain="spice-garden",
        admin_email="x@x.com",
        admin_password="12345678",
    )
    assert req.subdomain == "spice-garden"


def test_subdomain_starts_with_hyphen_raises() -> None:
    with pytest.raises(ValidationError):
        TenantCreateRequest(
            name="Test",
            subdomain="-bad",
            admin_email="x@x.com",
            admin_password="12345678",
        )


def test_subdomain_ends_with_hyphen_raises() -> None:
    with pytest.raises(ValidationError):
        TenantCreateRequest(
            name="Test",
            subdomain="bad-",
            admin_email="x@x.com",
            admin_password="12345678",
        )


def test_reserved_subdomain_raises() -> None:
    with pytest.raises(ValidationError):
        TenantCreateRequest(
            name="Test",
            subdomain="admin",
            admin_email="x@x.com",
            admin_password="12345678",
        )


def test_reserved_subdomain_api_raises() -> None:
    with pytest.raises(ValidationError):
        TenantCreateRequest(
            name="Test",
            subdomain="api",
            admin_email="x@x.com",
            admin_password="12345678",
        )


def test_password_too_short_raises() -> None:
    with pytest.raises(ValidationError):
        TenantCreateRequest(
            name="Test",
            subdomain="validslug",
            admin_email="x@x.com",
            admin_password="short",
        )


def test_invalid_email_raises() -> None:
    with pytest.raises(ValidationError):
        TenantCreateRequest(
            name="Test",
            subdomain="validslug",
            admin_email="not-an-email",
            admin_password="12345678",
        )


def test_name_empty_raises() -> None:
    with pytest.raises(ValidationError):
        TenantCreateRequest(
            name="",
            subdomain="validslug",
            admin_email="x@x.com",
            admin_password="12345678",
        )


def test_subdomain_too_short_raises() -> None:
    with pytest.raises(ValidationError):
        TenantCreateRequest(
            name="Test",
            subdomain="ab",
            admin_email="x@x.com",
            admin_password="12345678",
        )
