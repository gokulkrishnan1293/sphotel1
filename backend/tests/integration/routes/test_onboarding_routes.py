"""Integration tests for /api/v1/tenants/me/onboarding endpoints (Story 3.2)."""
import datetime
import uuid
from collections.abc import AsyncGenerator
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest
from httpx import ASGITransport, AsyncClient

from app.core.dependencies import CurrentUser, get_current_user
from app.core.security.permissions import UserRole
from app.db.session import get_db
from app.db.valkey import get_valkey
from app.main import app
from app.models.tenant import Tenant

TENANT_UUID = uuid.uuid4()
USER_ID = uuid.uuid4()


def _make_user(role: UserRole = UserRole.ADMIN) -> CurrentUser:
    return {
        "user_id": USER_ID,
        "tenant_id": str(TENANT_UUID),
        "role": role,
    }


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


def _make_fake_tenant(completed: bool = False) -> MagicMock:
    fake = MagicMock(spec=Tenant)
    fake.id = TENANT_UUID
    fake.name = "Test Restaurant"
    fake.slug = "testrestaurant"
    fake.is_active = True
    fake.onboarding_completed = completed
    fake.created_at = datetime.datetime(2026, 3, 18, tzinfo=datetime.timezone.utc)
    return fake


# ── GET /tenants/me/onboarding ─────────────────────────────────────────────────


@pytest.mark.anyio
async def test_get_onboarding_requires_admin() -> None:
    """Biller role → 403."""
    app.dependency_overrides[get_current_user] = lambda: _make_user(UserRole.BILLER)
    app.dependency_overrides[get_valkey] = _mock_valkey_dep()
    db_mock = AsyncMock()
    app.dependency_overrides[get_db] = _mock_db_dep(db_mock)
    try:
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            resp = await client.get("/api/v1/tenants/me/onboarding")
        assert resp.status_code == 403
    finally:
        app.dependency_overrides.clear()


@pytest.mark.anyio
async def test_get_onboarding_no_auth_returns_401() -> None:
    """No auth → 401."""
    app.dependency_overrides[get_valkey] = _mock_valkey_dep()
    try:
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            resp = await client.get("/api/v1/tenants/me/onboarding")
        assert resp.status_code == 401
    finally:
        app.dependency_overrides.clear()


@pytest.mark.anyio
async def test_get_onboarding_returns_checklist() -> None:
    """Admin → 200 with checklist; staff_pins=True when count > 0, menu_items=True when > 0."""
    fake_tenant = _make_fake_tenant(completed=False)

    tenant_result = MagicMock()
    tenant_result.scalar_one_or_none.return_value = fake_tenant

    staff_count_result = MagicMock()
    staff_count_result.scalar_one.return_value = 2  # 2 staff with PINs

    menu_count_result = MagicMock()
    menu_count_result.scalar_one.return_value = 5  # 5 active menu items

    db_mock = AsyncMock()
    db_mock.execute = AsyncMock(
        side_effect=[tenant_result, staff_count_result, menu_count_result]
    )

    app.dependency_overrides[get_current_user] = lambda: _make_user()
    app.dependency_overrides[get_db] = _mock_db_dep(db_mock)
    app.dependency_overrides[get_valkey] = _mock_valkey_dep()
    try:
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            resp = await client.get("/api/v1/tenants/me/onboarding")
        assert resp.status_code == 200
        body = resp.json()
        assert body["error"] is None
        assert body["data"]["completed"] is False
        items = {i["key"]: i for i in body["data"]["items"]}
        assert "staff_pins" in items
        assert items["staff_pins"]["completed"] is True
        assert items["menu_items"]["completed"] is True
        assert len(body["data"]["items"]) == 7
    finally:
        app.dependency_overrides.clear()


@pytest.mark.anyio
async def test_get_onboarding_staff_pins_false_when_no_staff() -> None:
    """No operational staff → staff_pins.completed = False; no menu → menu_items.completed = False."""
    fake_tenant = _make_fake_tenant()

    tenant_result = MagicMock()
    tenant_result.scalar_one_or_none.return_value = fake_tenant
    staff_count_result = MagicMock()
    staff_count_result.scalar_one.return_value = 0  # No staff
    menu_count_result = MagicMock()
    menu_count_result.scalar_one.return_value = 0  # No menu items

    db_mock = AsyncMock()
    db_mock.execute = AsyncMock(
        side_effect=[tenant_result, staff_count_result, menu_count_result]
    )

    app.dependency_overrides[get_current_user] = lambda: _make_user()
    app.dependency_overrides[get_db] = _mock_db_dep(db_mock)
    app.dependency_overrides[get_valkey] = _mock_valkey_dep()
    try:
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            resp = await client.get("/api/v1/tenants/me/onboarding")
        assert resp.status_code == 200
        items = {i["key"]: i for i in resp.json()["data"]["items"]}
        assert items["staff_pins"]["completed"] is False
        assert items["menu_items"]["completed"] is False
    finally:
        app.dependency_overrides.clear()


@pytest.mark.anyio
async def test_get_onboarding_tenant_not_found_returns_404() -> None:
    """Tenant not in DB → 404."""
    tenant_result = MagicMock()
    tenant_result.scalar_one_or_none.return_value = None
    db_mock = AsyncMock()
    db_mock.execute = AsyncMock(return_value=tenant_result)

    app.dependency_overrides[get_current_user] = lambda: _make_user()
    app.dependency_overrides[get_db] = _mock_db_dep(db_mock)
    app.dependency_overrides[get_valkey] = _mock_valkey_dep()
    try:
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            resp = await client.get("/api/v1/tenants/me/onboarding")
        assert resp.status_code == 404
        assert "NOT_FOUND" in resp.json()["error"]["message"]
    finally:
        app.dependency_overrides.clear()


# ── POST /tenants/me/onboarding/complete ──────────────────────────────────────


@pytest.mark.anyio
async def test_complete_onboarding_requires_admin() -> None:
    """Manager role → 403."""
    app.dependency_overrides[get_current_user] = lambda: _make_user(UserRole.MANAGER)
    app.dependency_overrides[get_valkey] = _mock_valkey_dep()
    db_mock = AsyncMock()
    app.dependency_overrides[get_db] = _mock_db_dep(db_mock)
    try:
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            resp = await client.post("/api/v1/tenants/me/onboarding/complete")
        assert resp.status_code == 403
    finally:
        app.dependency_overrides.clear()


@pytest.mark.anyio
async def test_complete_onboarding_returns_200() -> None:
    """Admin → 200; onboarding_completed set to True."""
    fake_tenant = _make_fake_tenant(completed=True)

    tenant_result = MagicMock()
    tenant_result.scalar_one_or_none.return_value = fake_tenant

    db_mock = AsyncMock()
    db_mock.execute = AsyncMock(return_value=tenant_result)
    db_mock.commit = AsyncMock()
    db_mock.refresh = AsyncMock()

    app.dependency_overrides[get_current_user] = lambda: _make_user()
    app.dependency_overrides[get_db] = _mock_db_dep(db_mock)
    app.dependency_overrides[get_valkey] = _mock_valkey_dep()
    try:
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            resp = await client.post("/api/v1/tenants/me/onboarding/complete")
        assert resp.status_code == 200
        body = resp.json()
        assert body["error"] is None
        assert body["data"]["onboarding_completed"] is True
    finally:
        app.dependency_overrides.clear()


@pytest.mark.anyio
async def test_complete_onboarding_tenant_not_found_returns_404() -> None:
    """Tenant not in DB → 404."""
    tenant_result = MagicMock()
    tenant_result.scalar_one_or_none.return_value = None

    db_mock = AsyncMock()
    db_mock.execute = AsyncMock(return_value=tenant_result)

    app.dependency_overrides[get_current_user] = lambda: _make_user()
    app.dependency_overrides[get_db] = _mock_db_dep(db_mock)
    app.dependency_overrides[get_valkey] = _mock_valkey_dep()
    try:
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            resp = await client.post("/api/v1/tenants/me/onboarding/complete")
        assert resp.status_code == 404
        assert "NOT_FOUND" in resp.json()["error"]["message"]
    finally:
        app.dependency_overrides.clear()
