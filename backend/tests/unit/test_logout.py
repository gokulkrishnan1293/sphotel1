"""Unit tests for POST /api/v1/auth/logout endpoint (Story 2.5).

Uses a minimal FastAPI test app with mocked Valkey to avoid DB/Redis deps.
"""
import time
import uuid
from collections.abc import AsyncGenerator
from typing import Any
from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from app.core.security.jwt import create_access_token
from app.core.security.permissions import UserRole
from app.db.valkey import get_valkey
from app.main import app


def _mock_valkey_dep(set_return: Any = True) -> Any:
    mock = AsyncMock()
    mock.set = AsyncMock(return_value=set_return)
    mock.get = AsyncMock(return_value=None)
    mock.aclose = AsyncMock()

    async def _gen() -> AsyncGenerator[Any, None]:
        yield mock

    return _gen, mock


@pytest.mark.anyio
async def test_logout_with_valid_token_clears_cookie_and_sets_revoked() -> None:
    """Valid token → Valkey session_revoked set + cookie deleted."""
    user_id = uuid.uuid4()
    token = create_access_token(user_id, "sphotel", UserRole.BILLER)

    gen_fn, valkey_mock = _mock_valkey_dep()
    app.dependency_overrides[get_valkey] = gen_fn
    try:
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            resp = await client.post(
                "/api/v1/auth/logout",
                cookies={"access_token": token},
            )
        assert resp.status_code == 200
        body = resp.json()
        assert body["error"] is None
        assert body["data"]["message"] == "Logged out successfully"

        # Valkey.set should have been called with session_revoked key
        calls = [str(c) for c in valkey_mock.set.call_args_list]
        assert any(f"session_revoked:{user_id}" in c for c in calls)

        # Cookie should be cleared (Set-Cookie header with max-age=0 or empty)
        set_cookie = resp.headers.get("set-cookie", "")
        assert "access_token" in set_cookie
    finally:
        app.dependency_overrides.clear()


@pytest.mark.anyio
async def test_logout_with_no_token_still_returns_200() -> None:
    """No cookie present → still succeeds (idempotent)."""
    gen_fn, valkey_mock = _mock_valkey_dep()
    app.dependency_overrides[get_valkey] = gen_fn
    try:
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            resp = await client.post("/api/v1/auth/logout")
        assert resp.status_code == 200
        assert resp.json()["data"]["message"] == "Logged out successfully"
        # No Valkey call when no token
        valkey_mock.set.assert_not_called()
    finally:
        app.dependency_overrides.clear()


@pytest.mark.anyio
async def test_logout_with_invalid_token_still_returns_200() -> None:
    """Garbage token → decode fails silently, still returns 200."""
    gen_fn, valkey_mock = _mock_valkey_dep()
    app.dependency_overrides[get_valkey] = gen_fn
    try:
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            resp = await client.post(
                "/api/v1/auth/logout",
                cookies={"access_token": "garbage.token.value"},
            )
        assert resp.status_code == 200
        # Valkey.set should NOT be called for invalid token
        valkey_mock.set.assert_not_called()
    finally:
        app.dependency_overrides.clear()


@pytest.mark.anyio
async def test_logout_ttl_is_remaining_lifetime() -> None:
    """TTL passed to Valkey should be > 0 and <= JWT_EXPIRY_HOURS * 3600."""
    from app.core.config import settings

    user_id = uuid.uuid4()
    token = create_access_token(user_id, "sphotel", UserRole.ADMIN)

    gen_fn, valkey_mock = _mock_valkey_dep()
    app.dependency_overrides[get_valkey] = gen_fn
    try:
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            await client.post(
                "/api/v1/auth/logout",
                cookies={"access_token": token},
            )
        # Extract TTL from set() call kwargs
        call_kwargs = valkey_mock.set.call_args
        ttl = call_kwargs.kwargs.get("ex") or call_kwargs.args[2]  # type: ignore[index]
        assert isinstance(ttl, int)
        assert 0 < ttl <= settings.JWT_EXPIRY_HOURS * 3600
    finally:
        app.dependency_overrides.clear()
