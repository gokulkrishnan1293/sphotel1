"""Integration tests for /api/v1/users/me/preferences endpoint (Story 2.6).

Uses ASGITransport with dependency_overrides to mock DB and Valkey.
"""
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

TENANT_ID = "sphotel"
USER_ID = uuid.uuid4()


def _make_user(role: UserRole = UserRole.BILLER) -> CurrentUser:
    return {
        "user_id": USER_ID,
        "tenant_id": TENANT_ID,
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


def _make_fake_user(preferences: dict[str, object] | None = None) -> MagicMock:
    fake = MagicMock()
    fake.id = USER_ID
    fake.user_id = USER_ID
    fake.tenant_id = TENANT_ID
    fake.name = "Test User"
    fake.role = UserRole.BILLER
    fake.email = None
    fake.is_active = True
    fake.preferences = preferences if preferences is not None else {}
    return fake


# ── PATCH /users/me/preferences ───────────────────────────────────────────────

@pytest.mark.anyio
async def test_update_preferences_requires_auth() -> None:
    """No auth cookie → 401."""
    app.dependency_overrides[get_valkey] = _mock_valkey_dep()
    try:
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            resp = await client.patch(
                "/api/v1/users/me/preferences",
                json={"theme": "dark"},
            )
        assert resp.status_code == 401
    finally:
        app.dependency_overrides.clear()


@pytest.mark.anyio
async def test_update_preferences_invalid_theme_returns_422() -> None:
    """Invalid theme value → 422 validation error."""
    app.dependency_overrides[get_current_user] = lambda: _make_user()
    app.dependency_overrides[get_valkey] = _mock_valkey_dep()
    db_mock = AsyncMock()
    app.dependency_overrides[get_db] = _mock_db_dep(db_mock)
    try:
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            resp = await client.patch(
                "/api/v1/users/me/preferences",
                json={"theme": "blue"},
            )
        assert resp.status_code == 422
    finally:
        app.dependency_overrides.clear()


@pytest.mark.anyio
async def test_update_preferences_dark_returns_200() -> None:
    """Valid dark theme → 200 with updated MeResponse."""
    fake_user = _make_fake_user(preferences={})
    updated_user = _make_fake_user(preferences={"theme": "dark"})

    # First execute (select by id) returns the existing user
    # Second execute (update) → None result
    # Third execute (re-select) returns updated user
    select_result_1 = MagicMock()
    select_result_1.scalar_one_or_none.return_value = fake_user
    update_result = MagicMock()
    select_result_2 = MagicMock()
    select_result_2.scalar_one.return_value = updated_user

    db_mock = AsyncMock()
    db_mock.execute = AsyncMock(
        side_effect=[select_result_1, update_result, select_result_2]
    )
    db_mock.commit = AsyncMock()

    app.dependency_overrides[get_current_user] = lambda: _make_user()
    app.dependency_overrides[get_db] = _mock_db_dep(db_mock)
    app.dependency_overrides[get_valkey] = _mock_valkey_dep()
    try:
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            resp = await client.patch(
                "/api/v1/users/me/preferences",
                json={"theme": "dark"},
            )
        assert resp.status_code == 200
        body = resp.json()
        assert body["error"] is None
        assert body["data"]["preferences"]["theme"] == "dark"
    finally:
        app.dependency_overrides.clear()


@pytest.mark.anyio
async def test_update_preferences_light_returns_200() -> None:
    """Valid light theme → 200."""
    fake_user = _make_fake_user()
    updated_user = _make_fake_user(preferences={"theme": "light"})

    select_result_1 = MagicMock()
    select_result_1.scalar_one_or_none.return_value = fake_user
    update_result = MagicMock()
    select_result_2 = MagicMock()
    select_result_2.scalar_one.return_value = updated_user

    db_mock = AsyncMock()
    db_mock.execute = AsyncMock(
        side_effect=[select_result_1, update_result, select_result_2]
    )
    db_mock.commit = AsyncMock()

    app.dependency_overrides[get_current_user] = lambda: _make_user()
    app.dependency_overrides[get_db] = _mock_db_dep(db_mock)
    app.dependency_overrides[get_valkey] = _mock_valkey_dep()
    try:
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            resp = await client.patch(
                "/api/v1/users/me/preferences",
                json={"theme": "light"},
            )
        assert resp.status_code == 200
        assert resp.json()["data"]["preferences"]["theme"] == "light"
    finally:
        app.dependency_overrides.clear()


@pytest.mark.anyio
async def test_update_preferences_high_contrast_returns_200() -> None:
    """Valid high_contrast theme → 200."""
    fake_user = _make_fake_user()
    updated_user = _make_fake_user(preferences={"theme": "high_contrast"})

    select_result_1 = MagicMock()
    select_result_1.scalar_one_or_none.return_value = fake_user
    update_result = MagicMock()
    select_result_2 = MagicMock()
    select_result_2.scalar_one.return_value = updated_user

    db_mock = AsyncMock()
    db_mock.execute = AsyncMock(
        side_effect=[select_result_1, update_result, select_result_2]
    )
    db_mock.commit = AsyncMock()

    app.dependency_overrides[get_current_user] = lambda: _make_user()
    app.dependency_overrides[get_db] = _mock_db_dep(db_mock)
    app.dependency_overrides[get_valkey] = _mock_valkey_dep()
    try:
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            resp = await client.patch(
                "/api/v1/users/me/preferences",
                json={"theme": "high_contrast"},
            )
        assert resp.status_code == 200
        assert resp.json()["data"]["preferences"]["theme"] == "high_contrast"
    finally:
        app.dependency_overrides.clear()


@pytest.mark.anyio
async def test_update_preferences_user_not_found_returns_404() -> None:
    """User not in DB → 404."""
    select_result = MagicMock()
    select_result.scalar_one_or_none.return_value = None
    db_mock = AsyncMock()
    db_mock.execute = AsyncMock(return_value=select_result)

    app.dependency_overrides[get_current_user] = lambda: _make_user()
    app.dependency_overrides[get_db] = _mock_db_dep(db_mock)
    app.dependency_overrides[get_valkey] = _mock_valkey_dep()
    try:
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            resp = await client.patch(
                "/api/v1/users/me/preferences",
                json={"theme": "dark"},
            )
        assert resp.status_code == 404
        assert "NOT_FOUND" in resp.json()["error"]["message"]
    finally:
        app.dependency_overrides.clear()


@pytest.mark.anyio
async def test_update_preferences_allowed_for_all_roles() -> None:
    """Admin role → 200 (all roles permitted, no require_role guard)."""
    fake_user = _make_fake_user()
    updated_user = _make_fake_user(preferences={"theme": "dark"})
    updated_user.role = UserRole.ADMIN

    select_result_1 = MagicMock()
    select_result_1.scalar_one_or_none.return_value = fake_user
    update_result = MagicMock()
    select_result_2 = MagicMock()
    select_result_2.scalar_one.return_value = updated_user

    db_mock = AsyncMock()
    db_mock.execute = AsyncMock(
        side_effect=[select_result_1, update_result, select_result_2]
    )
    db_mock.commit = AsyncMock()

    app.dependency_overrides[get_current_user] = lambda: _make_user(UserRole.ADMIN)
    app.dependency_overrides[get_db] = _mock_db_dep(db_mock)
    app.dependency_overrides[get_valkey] = _mock_valkey_dep()
    try:
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            resp = await client.patch(
                "/api/v1/users/me/preferences",
                json={"theme": "dark"},
            )
        assert resp.status_code == 200
    finally:
        app.dependency_overrides.clear()
