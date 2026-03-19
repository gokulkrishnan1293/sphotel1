"""Integration tests for /api/v1/super-admin/* endpoints (Story 3.1)."""
import datetime
import uuid
from collections.abc import AsyncGenerator
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException
from httpx import ASGITransport, AsyncClient

from app.core.dependencies import CurrentUser, get_current_user
from app.core.security.permissions import UserRole
from app.db.session import get_db
from app.db.valkey import get_valkey
from app.main import app
from app.models.tenant import Tenant
from app.schemas.tenant import TenantCreateRequest

TENANT_ID = "sphotel"
USER_ID = uuid.uuid4()
TENANT_UUID = uuid.uuid4()

_VALID_PROVISION_PAYLOAD = {
    "name": "Spice Garden",
    "subdomain": "spicegarden",
    "admin_email": "admin@spicegarden.com",
    "admin_password": "securepass123",
}


def _make_user(role: UserRole = UserRole.SUPER_ADMIN) -> CurrentUser:
    return {"user_id": USER_ID, "tenant_id": TENANT_ID, "role": role}


def _mock_valkey_dep() -> Any:
    mock = AsyncMock()
    mock.get = AsyncMock(return_value=None)
    mock.aclose = AsyncMock()

    async def _gen() -> AsyncGenerator[Any, None]:
        yield mock

    return _gen


def _mock_db_dep(db_mock: Any) -> Any:
    async def _gen() -> AsyncGenerator[Any, None]:
        yield db_mock

    return _gen


def _make_fake_tenant() -> MagicMock:
    fake = MagicMock(spec=Tenant)
    fake.id = TENANT_UUID
    fake.name = "Spice Garden"
    fake.slug = "spicegarden"
    fake.is_active = True
    fake.onboarding_completed = False
    fake.created_at = datetime.datetime(2026, 3, 18, tzinfo=datetime.timezone.utc)
    return fake


# ── POST /super-admin/tenants ─────────────────────────────────────────────────


@pytest.mark.anyio
async def test_create_tenant_requires_super_admin() -> None:
    """Admin role → 403."""
    app.dependency_overrides[get_current_user] = lambda: _make_user(UserRole.ADMIN)
    app.dependency_overrides[get_valkey] = _mock_valkey_dep()
    db_mock = AsyncMock()
    app.dependency_overrides[get_db] = _mock_db_dep(db_mock)
    try:
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            resp = await client.post(
                "/api/v1/super-admin/tenants", json=_VALID_PROVISION_PAYLOAD
            )
        assert resp.status_code == 403
    finally:
        app.dependency_overrides.clear()


@pytest.mark.anyio
async def test_create_tenant_no_auth_returns_401() -> None:
    """No auth cookie → 401."""
    app.dependency_overrides[get_valkey] = _mock_valkey_dep()
    try:
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            resp = await client.post(
                "/api/v1/super-admin/tenants", json=_VALID_PROVISION_PAYLOAD
            )
        assert resp.status_code == 401
    finally:
        app.dependency_overrides.clear()


@pytest.mark.anyio
async def test_create_tenant_invalid_subdomain_returns_422() -> None:
    """Reserved subdomain → 422."""
    app.dependency_overrides[get_current_user] = lambda: _make_user()
    app.dependency_overrides[get_valkey] = _mock_valkey_dep()
    db_mock = AsyncMock()
    app.dependency_overrides[get_db] = _mock_db_dep(db_mock)
    try:
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            resp = await client.post(
                "/api/v1/super-admin/tenants",
                json={**_VALID_PROVISION_PAYLOAD, "subdomain": "admin"},
            )
        assert resp.status_code == 422
    finally:
        app.dependency_overrides.clear()


@pytest.mark.anyio
async def test_create_tenant_short_password_returns_422() -> None:
    """Password < 8 chars → 422."""
    app.dependency_overrides[get_current_user] = lambda: _make_user()
    app.dependency_overrides[get_valkey] = _mock_valkey_dep()
    db_mock = AsyncMock()
    app.dependency_overrides[get_db] = _mock_db_dep(db_mock)
    try:
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            resp = await client.post(
                "/api/v1/super-admin/tenants",
                json={**_VALID_PROVISION_PAYLOAD, "admin_password": "short"},
            )
        assert resp.status_code == 422
    finally:
        app.dependency_overrides.clear()


@pytest.mark.anyio
async def test_create_tenant_success_returns_201() -> None:
    """Valid request → 201 with TenantProvisionResponse."""
    fake_tenant = _make_fake_tenant()
    _totp_uri = "otpauth://totp/sphotel:admin%40spicegarden.com?secret=ABCDEF"

    async def _mock_provision(
        req: TenantCreateRequest, db: Any, actor_id: uuid.UUID
    ) -> tuple[MagicMock, str]:
        return fake_tenant, _totp_uri

    app.dependency_overrides[get_current_user] = lambda: _make_user()
    app.dependency_overrides[get_valkey] = _mock_valkey_dep()
    db_mock = AsyncMock()
    app.dependency_overrides[get_db] = _mock_db_dep(db_mock)
    try:
        with patch(
            "app.api.v1.routes.super_admin.provision_tenant",
            new=_mock_provision,
        ):
            async with AsyncClient(
                transport=ASGITransport(app=app), base_url="http://test"
            ) as client:
                resp = await client.post(
                    "/api/v1/super-admin/tenants", json=_VALID_PROVISION_PAYLOAD
                )
        assert resp.status_code == 201
        body = resp.json()
        assert body["error"] is None
        assert body["data"]["slug"] == "spicegarden"
        assert body["data"]["name"] == "Spice Garden"
        assert body["data"]["onboarding_completed"] is False
        assert body["data"]["is_active"] is True
        assert "totp_setup_uri" in body["data"]
        assert body["data"]["totp_setup_uri"] == _totp_uri
    finally:
        app.dependency_overrides.clear()


@pytest.mark.anyio
async def test_create_tenant_duplicate_subdomain_returns_409() -> None:
    """Duplicate subdomain → 409 CONFLICT."""

    async def _mock_conflict(
        req: TenantCreateRequest, db: Any, actor_id: uuid.UUID
    ) -> tuple[Any, str]:
        raise HTTPException(
            status_code=409,
            detail={
                "code": "CONFLICT",
                "message": "Subdomain 'spicegarden' is already taken",
            },
        )

    app.dependency_overrides[get_current_user] = lambda: _make_user()
    app.dependency_overrides[get_valkey] = _mock_valkey_dep()
    db_mock = AsyncMock()
    app.dependency_overrides[get_db] = _mock_db_dep(db_mock)
    try:
        with patch(
            "app.api.v1.routes.super_admin.provision_tenant",
            new=_mock_conflict,
        ):
            async with AsyncClient(
                transport=ASGITransport(app=app), base_url="http://test"
            ) as client:
                resp = await client.post(
                    "/api/v1/super-admin/tenants", json=_VALID_PROVISION_PAYLOAD
                )
        assert resp.status_code == 409
    finally:
        app.dependency_overrides.clear()


# ── GET /super-admin/stats ────────────────────────────────────────────────────


@pytest.mark.anyio
async def test_get_stats_requires_super_admin() -> None:
    """Admin role → 403."""
    app.dependency_overrides[get_current_user] = lambda: _make_user(UserRole.ADMIN)
    app.dependency_overrides[get_valkey] = _mock_valkey_dep()
    db_mock = AsyncMock()
    app.dependency_overrides[get_db] = _mock_db_dep(db_mock)
    try:
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            resp = await client.get("/api/v1/super-admin/stats")
        assert resp.status_code == 403
    finally:
        app.dependency_overrides.clear()


@pytest.mark.anyio
async def test_get_stats_no_auth_returns_401() -> None:
    """No auth → 401."""
    app.dependency_overrides[get_valkey] = _mock_valkey_dep()
    try:
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            resp = await client.get("/api/v1/super-admin/stats")
        assert resp.status_code == 401
    finally:
        app.dependency_overrides.clear()


@pytest.mark.anyio
async def test_get_stats_returns_tenant_count() -> None:
    """Super-Admin → 200 with total_tenants and total_bills_processed=0."""
    count_result = MagicMock()
    count_result.scalar_one.return_value = 3

    db_mock = AsyncMock()
    db_mock.execute = AsyncMock(return_value=count_result)

    app.dependency_overrides[get_current_user] = lambda: _make_user()
    app.dependency_overrides[get_db] = _mock_db_dep(db_mock)
    app.dependency_overrides[get_valkey] = _mock_valkey_dep()
    try:
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            resp = await client.get("/api/v1/super-admin/stats")
        assert resp.status_code == 200
        body = resp.json()
        assert body["error"] is None
        assert body["data"]["total_tenants"] == 3
        assert body["data"]["total_bills_processed"] == 0
    finally:
        app.dependency_overrides.clear()


@pytest.mark.anyio
async def test_get_stats_zero_tenants() -> None:
    """Zero tenants → 200 with total_tenants=0."""
    count_result = MagicMock()
    count_result.scalar_one.return_value = 0

    db_mock = AsyncMock()
    db_mock.execute = AsyncMock(return_value=count_result)

    app.dependency_overrides[get_current_user] = lambda: _make_user()
    app.dependency_overrides[get_db] = _mock_db_dep(db_mock)
    app.dependency_overrides[get_valkey] = _mock_valkey_dep()
    try:
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            resp = await client.get("/api/v1/super-admin/stats")
        assert resp.status_code == 200
        assert resp.json()["data"]["total_tenants"] == 0
    finally:
        app.dependency_overrides.clear()
