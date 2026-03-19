"""Integration tests for /api/v1/staff endpoints (Story 2.4).

Uses ASGITransport with dependency_overrides to mock DB and Valkey.
All tests are tenant-scoped and role-guarded.
"""
import uuid
from collections.abc import AsyncGenerator
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from app.core.dependencies import CurrentUser, get_current_user
from app.core.security.permissions import UserRole
from app.db.session import get_db
from app.db.valkey import get_valkey
from app.main import app

TENANT_ID = "sphotel"
ADMIN_ID = uuid.uuid4()


def _admin_user(role: UserRole = UserRole.ADMIN) -> CurrentUser:
    return {
        "user_id": ADMIN_ID,
        "tenant_id": TENANT_ID,
        "role": role,
    }


def _biller_user() -> CurrentUser:
    return {
        "user_id": uuid.uuid4(),
        "tenant_id": TENANT_ID,
        "role": UserRole.BILLER,
    }


def _mock_valkey_dep(get_return: str | None = None) -> Any:
    mock = AsyncMock()
    mock.get = AsyncMock(return_value=get_return)
    mock.set = AsyncMock(return_value=True)
    mock.aclose = AsyncMock()

    async def _gen() -> AsyncGenerator[Any, None]:
        yield mock

    return _gen


def _mock_db_dep(db_mock: Any) -> Any:
    async def _gen() -> AsyncGenerator[Any, None]:
        yield db_mock

    return _gen


# ── GET /staff — list ────────────────────────────────────────────────────────
@pytest.mark.anyio
async def test_list_staff_requires_auth() -> None:
    """No auth cookie → 401."""
    app.dependency_overrides[get_valkey] = _mock_valkey_dep()
    try:
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            resp = await client.get("/api/v1/staff")
        assert resp.status_code == 401
    finally:
        app.dependency_overrides.clear()


@pytest.mark.anyio
async def test_list_staff_forbidden_for_biller() -> None:
    """BILLER role → 403."""
    app.dependency_overrides[get_current_user] = lambda: _biller_user()
    app.dependency_overrides[get_valkey] = _mock_valkey_dep()
    try:
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            resp = await client.get("/api/v1/staff")
        assert resp.status_code == 403
    finally:
        app.dependency_overrides.clear()


@pytest.mark.anyio
async def test_list_staff_returns_200_for_admin() -> None:
    """ADMIN with mocked DB → 200 with envelope."""
    # Build a fake DB session that returns an empty list
    fake_scalars = MagicMock()
    fake_scalars.all.return_value = []
    fake_result = MagicMock()
    fake_result.scalars.return_value = fake_scalars
    db_mock = AsyncMock()
    db_mock.execute = AsyncMock(return_value=fake_result)

    app.dependency_overrides[get_current_user] = lambda: _admin_user()
    app.dependency_overrides[get_db] = _mock_db_dep(db_mock)
    app.dependency_overrides[get_valkey] = _mock_valkey_dep()
    try:
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            resp = await client.get("/api/v1/staff")
        assert resp.status_code == 200
        body = resp.json()
        assert body["error"] is None
        assert body["data"] == []
    finally:
        app.dependency_overrides.clear()


# ── POST /staff — create ─────────────────────────────────────────────────────
@pytest.mark.anyio
async def test_create_staff_rejects_role_hierarchy_violation() -> None:
    """Admin cannot create another Admin (same level) → 403 ROLE_HIERARCHY_VIOLATION."""
    app.dependency_overrides[get_current_user] = lambda: _admin_user(UserRole.ADMIN)
    app.dependency_overrides[get_valkey] = _mock_valkey_dep()
    db_mock = AsyncMock()
    app.dependency_overrides[get_db] = _mock_db_dep(db_mock)
    try:
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            resp = await client.post(
                "/api/v1/staff",
                json={"name": "Eve", "role": "admin", "pin": "1234"},
            )
        assert resp.status_code == 403
        # Custom exception handler wraps detail in error envelope
        assert "ROLE_HIERARCHY_VIOLATION" in resp.json()["error"]["message"]
    finally:
        app.dependency_overrides.clear()


@pytest.mark.anyio
async def test_create_staff_rejects_invalid_pin() -> None:
    """PIN shorter than 4 digits → 422 validation error."""
    app.dependency_overrides[get_current_user] = lambda: _admin_user()
    app.dependency_overrides[get_valkey] = _mock_valkey_dep()
    db_mock = AsyncMock()
    app.dependency_overrides[get_db] = _mock_db_dep(db_mock)
    try:
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            resp = await client.post(
                "/api/v1/staff",
                json={"name": "Bob", "role": "biller", "pin": "12"},
            )
        assert resp.status_code == 422
    finally:
        app.dependency_overrides.clear()


# ── PATCH /staff/{id}/pin — reset PIN ────────────────────────────────────────
@pytest.mark.anyio
async def test_reset_pin_not_found_returns_404() -> None:
    """Staff ID not found in tenant → 404."""
    fake_result = MagicMock()
    fake_result.scalar_one_or_none.return_value = None
    db_mock = AsyncMock()
    db_mock.execute = AsyncMock(return_value=fake_result)

    app.dependency_overrides[get_current_user] = lambda: _admin_user()
    app.dependency_overrides[get_db] = _mock_db_dep(db_mock)
    app.dependency_overrides[get_valkey] = _mock_valkey_dep()
    try:
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            resp = await client.patch(
                f"/api/v1/staff/{uuid.uuid4()}/pin",
                json={"pin": "9999"},
            )
        assert resp.status_code == 404
        assert "NOT_FOUND" in resp.json()["error"]["message"]
    finally:
        app.dependency_overrides.clear()


# ── PATCH /staff/{id}/deactivate ─────────────────────────────────────────────
@pytest.mark.anyio
async def test_deactivate_requires_admin() -> None:
    """BILLER cannot deactivate staff → 403."""
    app.dependency_overrides[get_current_user] = lambda: _biller_user()
    app.dependency_overrides[get_valkey] = _mock_valkey_dep()
    try:
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            resp = await client.patch(f"/api/v1/staff/{uuid.uuid4()}/deactivate")
        assert resp.status_code == 403
    finally:
        app.dependency_overrides.clear()


# ── DELETE /staff/{id}/sessions ───────────────────────────────────────────────
@pytest.mark.anyio
async def test_revoke_sessions_not_found_returns_404() -> None:
    """Staff ID not found in tenant → 404."""
    fake_result = MagicMock()
    fake_result.scalar_one_or_none.return_value = None
    db_mock = AsyncMock()
    db_mock.execute = AsyncMock(return_value=fake_result)

    app.dependency_overrides[get_current_user] = lambda: _admin_user()
    app.dependency_overrides[get_db] = _mock_db_dep(db_mock)
    app.dependency_overrides[get_valkey] = _mock_valkey_dep()
    try:
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            resp = await client.delete(
                f"/api/v1/staff/{uuid.uuid4()}/sessions"
            )
        assert resp.status_code == 404
    finally:
        app.dependency_overrides.clear()


@pytest.mark.anyio
async def test_revoke_sessions_sets_valkey_keys() -> None:
    """Successful revoke sets session_revoked and auth_locked in Valkey."""
    staff_id = uuid.uuid4()

    # Fake staff record in DB
    fake_staff = MagicMock()
    fake_staff.id = staff_id
    fake_staff.role = UserRole.BILLER
    fake_staff.tenant_id = TENANT_ID
    fake_result = MagicMock()
    fake_result.scalar_one_or_none.return_value = fake_staff
    db_mock = AsyncMock()
    db_mock.execute = AsyncMock(return_value=fake_result)
    db_mock.add = MagicMock()
    db_mock.commit = AsyncMock()

    valkey_mock = AsyncMock()
    valkey_mock.set = AsyncMock(return_value=True)
    valkey_mock.aclose = AsyncMock()

    async def _valkey_gen() -> AsyncGenerator[Any, None]:
        yield valkey_mock

    app.dependency_overrides[get_current_user] = lambda: _admin_user()
    app.dependency_overrides[get_db] = _mock_db_dep(db_mock)
    app.dependency_overrides[get_valkey] = _valkey_gen
    try:
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            resp = await client.delete(f"/api/v1/staff/{staff_id}/sessions")
        assert resp.status_code == 200
        body = resp.json()
        assert body["error"] is None
        assert body["data"]["message"] == "Sessions revoked"

        # Verify Valkey was called with both keys
        calls = [str(c) for c in valkey_mock.set.call_args_list]
        assert any(f"session_revoked:{staff_id}" in c for c in calls)
        assert any(f"auth_locked:{staff_id}" in c for c in calls)
    finally:
        app.dependency_overrides.clear()
