"""Integration tests for /api/v1/auth/logout and /api/v1/auth/me (Story 2.5).

Uses ASGITransport with dependency_overrides to mock DB and Valkey.
"""
import uuid
from collections.abc import AsyncGenerator
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest
from httpx import ASGITransport, AsyncClient

from app.core.dependencies import CurrentUser, get_current_user
from app.core.security.jwt import create_access_token
from app.core.security.permissions import UserRole
from app.db.session import get_db
from app.db.valkey import get_valkey
from app.main import app

TENANT_ID = "sphotel"
USER_ID = uuid.uuid4()


def _make_user(role: UserRole = UserRole.ADMIN) -> CurrentUser:
    return {
        "user_id": USER_ID,
        "tenant_id": TENANT_ID,
        "role": role,
    }


def _mock_valkey_dep(get_return: str | None = None) -> Any:
    mock = AsyncMock()
    mock.get = AsyncMock(return_value=get_return)
    mock.set = AsyncMock(return_value=True)
    mock.delete = AsyncMock(return_value=1)
    mock.aclose = AsyncMock()

    async def _gen() -> AsyncGenerator[Any, None]:
        yield mock

    return _gen


def _mock_db_dep(db_mock: Any) -> Any:
    async def _gen() -> AsyncGenerator[Any, None]:
        yield db_mock

    return _gen


# ── POST /auth/logout ─────────────────────────────────────────────────────────

@pytest.mark.anyio
async def test_logout_no_cookie_returns_200() -> None:
    """No cookie → 200, idempotent."""
    app.dependency_overrides[get_valkey] = _mock_valkey_dep()
    try:
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            resp = await client.post("/api/v1/auth/logout")
        assert resp.status_code == 200
        assert resp.json()["data"]["message"] == "Logged out successfully"
    finally:
        app.dependency_overrides.clear()


@pytest.mark.anyio
async def test_logout_with_valid_token_returns_200() -> None:
    """Valid token → 200, session_revoked set in Valkey, cookie cleared."""
    valkey_mock = AsyncMock()
    valkey_mock.set = AsyncMock(return_value=True)
    valkey_mock.aclose = AsyncMock()

    async def _valkey_gen() -> AsyncGenerator[Any, None]:
        yield valkey_mock

    token = create_access_token(USER_ID, TENANT_ID, UserRole.BILLER)

    app.dependency_overrides[get_valkey] = _valkey_gen
    try:
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            resp = await client.post(
                "/api/v1/auth/logout",
                cookies={"access_token": token},
            )
        assert resp.status_code == 200
        calls = [str(c) for c in valkey_mock.set.call_args_list]
        assert any(f"session_revoked:{USER_ID}" in c for c in calls)
    finally:
        app.dependency_overrides.clear()


# ── GET /auth/me ──────────────────────────────────────────────────────────────

@pytest.mark.anyio
async def test_get_me_requires_auth() -> None:
    """No auth → 401."""
    app.dependency_overrides[get_valkey] = _mock_valkey_dep()
    try:
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            resp = await client.get("/api/v1/auth/me")
        assert resp.status_code == 401
    finally:
        app.dependency_overrides.clear()


@pytest.mark.anyio
async def test_get_me_returns_user_profile() -> None:
    """Authenticated user → 200 with MeResponse envelope."""
    fake_user = MagicMock()
    fake_user.user_id = USER_ID
    fake_user.tenant_id = TENANT_ID
    fake_user.name = "Alice Admin"
    fake_user.role = UserRole.ADMIN
    fake_user.email = "alice@sphotel.com"
    fake_user.is_active = True
    fake_user.preferences = {}

    fake_result = MagicMock()
    fake_result.scalar_one_or_none.return_value = fake_user
    db_mock = AsyncMock()
    db_mock.execute = AsyncMock(return_value=fake_result)

    app.dependency_overrides[get_current_user] = lambda: _make_user()
    app.dependency_overrides[get_db] = _mock_db_dep(db_mock)
    app.dependency_overrides[get_valkey] = _mock_valkey_dep()
    try:
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            resp = await client.get("/api/v1/auth/me")
        assert resp.status_code == 200
        body = resp.json()
        assert body["error"] is None
        assert body["data"]["name"] == "Alice Admin"
        assert body["data"]["role"] == "admin"
    finally:
        app.dependency_overrides.clear()


@pytest.mark.anyio
async def test_get_me_user_not_found_returns_404() -> None:
    """User deleted from DB after auth → 404."""
    fake_result = MagicMock()
    fake_result.scalar_one_or_none.return_value = None
    db_mock = AsyncMock()
    db_mock.execute = AsyncMock(return_value=fake_result)

    app.dependency_overrides[get_current_user] = lambda: _make_user()
    app.dependency_overrides[get_db] = _mock_db_dep(db_mock)
    app.dependency_overrides[get_valkey] = _mock_valkey_dep()
    try:
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            resp = await client.get("/api/v1/auth/me")
        assert resp.status_code == 404
        assert "NOT_FOUND" in resp.json()["error"]["message"]
    finally:
        app.dependency_overrides.clear()


@pytest.mark.anyio
async def test_get_me_allowed_for_all_roles() -> None:
    """Biller role → 200 (all roles permitted on /me)."""
    fake_user = MagicMock()
    fake_user.user_id = USER_ID
    fake_user.tenant_id = TENANT_ID
    fake_user.name = "Bob Biller"
    fake_user.role = UserRole.BILLER
    fake_user.email = None
    fake_user.is_active = True
    fake_user.preferences = {}

    fake_result = MagicMock()
    fake_result.scalar_one_or_none.return_value = fake_user
    db_mock = AsyncMock()
    db_mock.execute = AsyncMock(return_value=fake_result)

    app.dependency_overrides[get_current_user] = lambda: {
        "user_id": USER_ID,
        "tenant_id": TENANT_ID,
        "role": UserRole.BILLER,
    }
    app.dependency_overrides[get_db] = _mock_db_dep(db_mock)
    app.dependency_overrides[get_valkey] = _mock_valkey_dep()
    try:
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            resp = await client.get("/api/v1/auth/me")
        assert resp.status_code == 200
        assert resp.json()["data"]["role"] == "biller"
    finally:
        app.dependency_overrides.clear()


# ── PATCH /auth/credentials ───────────────────────────────────────────────────

@pytest.mark.anyio
async def test_update_credentials_requires_admin() -> None:
    """Biller cannot update credentials → 403."""
    app.dependency_overrides[get_current_user] = lambda: {
        "user_id": USER_ID,
        "tenant_id": TENANT_ID,
        "role": UserRole.BILLER,
    }
    app.dependency_overrides[get_valkey] = _mock_valkey_dep()
    try:
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            resp = await client.patch(
                "/api/v1/auth/credentials",
                json={"password": "newpass"},
            )
        assert resp.status_code == 403
    finally:
        app.dependency_overrides.clear()


@pytest.mark.anyio
async def test_update_credentials_both_none_returns_422() -> None:
    """Empty body (both fields None) → 422 validation error."""
    app.dependency_overrides[get_current_user] = lambda: _make_user()
    app.dependency_overrides[get_valkey] = _mock_valkey_dep()
    db_mock = AsyncMock()
    app.dependency_overrides[get_db] = _mock_db_dep(db_mock)
    try:
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            resp = await client.patch(
                "/api/v1/auth/credentials",
                json={},
            )
        assert resp.status_code == 422
    finally:
        app.dependency_overrides.clear()
