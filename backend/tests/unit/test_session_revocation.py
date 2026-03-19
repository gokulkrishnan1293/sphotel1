"""Tests for session revocation check in get_current_user (Story 2.4).

Uses a minimal isolated FastAPI app to avoid polluting the production app.
Mocks Valkey via dependency_overrides so no real Valkey connection is needed.
"""
import time
import uuid
from collections.abc import AsyncGenerator
from typing import Any
from unittest.mock import AsyncMock

import pytest
from fastapi import Depends, FastAPI
from fastapi.responses import JSONResponse
from httpx import ASGITransport, AsyncClient

from app.core.dependencies import CurrentUser, require_role
from app.core.security.jwt import create_access_token
from app.core.security.permissions import UserRole
from app.db.valkey import get_valkey

# ── Minimal test app ─────────────────────────────────────────────────────────
_test_app = FastAPI()


@_test_app.get("/me")
async def _me_route(
    user: CurrentUser = Depends(require_role(UserRole.BILLER)),
) -> JSONResponse:
    return JSONResponse({"user_id": str(user["user_id"])})


# ── Helpers ──────────────────────────────────────────────────────────────────
def _make_token(user_id: uuid.UUID, role: UserRole = UserRole.BILLER) -> str:
    return create_access_token(user_id, "sphotel", role)


def _mock_valkey_dep(get_return: str | None = None) -> Any:
    """Return a mock Valkey dep generator whose .get() returns get_return."""
    mock = AsyncMock()
    mock.get = AsyncMock(return_value=get_return)
    mock.aclose = AsyncMock()

    async def _gen() -> AsyncGenerator[Any, None]:
        yield mock

    return _gen


# ── Tests ────────────────────────────────────────────────────────────────────
@pytest.mark.anyio
async def test_valid_token_with_no_revocation_passes() -> None:
    """Valid JWT + no revocation key in Valkey → 200."""
    user_id = uuid.uuid4()
    token = _make_token(user_id)
    _test_app.dependency_overrides[get_valkey] = _mock_valkey_dep(get_return=None)
    try:
        async with AsyncClient(
            transport=ASGITransport(app=_test_app), base_url="http://test"
        ) as client:
            resp = await client.get("/me", cookies={"access_token": token})
        assert resp.status_code == 200
    finally:
        _test_app.dependency_overrides.clear()


@pytest.mark.anyio
async def test_revoked_session_returns_401() -> None:
    """session_revoked timestamp >= token iat → 401 SESSION_REVOKED."""
    user_id = uuid.uuid4()
    token = _make_token(user_id)
    # Revocation timestamp in the future — definitely after token iat
    future_ts = str(time.time() + 9999)
    _test_app.dependency_overrides[get_valkey] = _mock_valkey_dep(
        get_return=future_ts
    )
    try:
        async with AsyncClient(
            transport=ASGITransport(app=_test_app), base_url="http://test"
        ) as client:
            resp = await client.get("/me", cookies={"access_token": token})
        assert resp.status_code == 401
        assert resp.json()["detail"]["code"] == "SESSION_REVOKED"
    finally:
        _test_app.dependency_overrides.clear()


@pytest.mark.anyio
async def test_token_issued_after_revocation_passes() -> None:
    """Token issued NOW when revocation timestamp is in the past → allowed."""
    user_id = uuid.uuid4()
    # Revocation timestamp set 9999 seconds ago
    past_ts = str(time.time() - 9999)
    token = _make_token(user_id)
    # token iat is ~now, which is > past revocation → should pass
    _test_app.dependency_overrides[get_valkey] = _mock_valkey_dep(get_return=past_ts)
    try:
        async with AsyncClient(
            transport=ASGITransport(app=_test_app), base_url="http://test"
        ) as client:
            resp = await client.get("/me", cookies={"access_token": token})
        assert resp.status_code == 200
    finally:
        _test_app.dependency_overrides.clear()


@pytest.mark.anyio
async def test_no_cookie_returns_401_unauthorized() -> None:
    """No access_token cookie → 401 UNAUTHORIZED (not SESSION_REVOKED)."""
    _test_app.dependency_overrides[get_valkey] = _mock_valkey_dep(get_return=None)
    try:
        async with AsyncClient(
            transport=ASGITransport(app=_test_app), base_url="http://test"
        ) as client:
            resp = await client.get("/me")
        assert resp.status_code == 401
        assert resp.json()["detail"]["code"] == "UNAUTHORIZED"
    finally:
        _test_app.dependency_overrides.clear()
