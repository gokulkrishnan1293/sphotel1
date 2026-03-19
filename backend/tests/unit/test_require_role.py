import uuid

import pytest
from fastapi import Depends, FastAPI
from fastapi.responses import JSONResponse
from httpx import ASGITransport, AsyncClient

from app.core.dependencies import CurrentUser, get_current_user, require_role
from app.core.security.permissions import UserRole

# Minimal isolated test app — avoids mutating the production app instance
_test_app = FastAPI()


@_test_app.get("/admin-only")
async def _admin_route(
    user: CurrentUser = Depends(require_role(UserRole.ADMIN)),
) -> JSONResponse:
    return JSONResponse({"role": user["role"]})


@_test_app.get("/admin-or-manager")
async def _admin_or_manager_route(
    user: CurrentUser = Depends(require_role(UserRole.ADMIN, UserRole.MANAGER)),
) -> JSONResponse:
    return JSONResponse({"role": user["role"]})


def _make_user(role: UserRole) -> CurrentUser:
    return {
        "user_id": uuid.uuid4(),
        "tenant_id": str(uuid.uuid4()),
        "role": role,
    }


@pytest.mark.anyio
async def test_require_role_returns_401_without_auth() -> None:
    """No dependency override — get_current_user stub raises 401."""
    async with AsyncClient(
        transport=ASGITransport(app=_test_app), base_url="http://test"
    ) as client:
        response = await client.get("/admin-only")
    assert response.status_code == 401
    assert response.json()["detail"]["code"] == "UNAUTHORIZED"


@pytest.mark.anyio
async def test_require_role_returns_403_for_wrong_role() -> None:
    """BILLER role is rejected from an ADMIN-only endpoint."""
    _test_app.dependency_overrides[get_current_user] = lambda: _make_user(
        UserRole.BILLER
    )
    try:
        async with AsyncClient(
            transport=ASGITransport(app=_test_app), base_url="http://test"
        ) as client:
            response = await client.get("/admin-only")
        assert response.status_code == 403
        assert response.json()["detail"]["code"] == "FORBIDDEN"
    finally:
        _test_app.dependency_overrides.clear()


@pytest.mark.anyio
async def test_require_role_returns_200_for_correct_role() -> None:
    """ADMIN role is accepted on an ADMIN-only endpoint."""
    _test_app.dependency_overrides[get_current_user] = lambda: _make_user(
        UserRole.ADMIN
    )
    try:
        async with AsyncClient(
            transport=ASGITransport(app=_test_app), base_url="http://test"
        ) as client:
            response = await client.get("/admin-only")
        assert response.status_code == 200
        assert response.json()["role"] == "admin"
    finally:
        _test_app.dependency_overrides.clear()


@pytest.mark.anyio
async def test_require_role_multi_role_admin_accepted() -> None:
    """ADMIN accepted when multiple roles are allowed."""
    _test_app.dependency_overrides[get_current_user] = lambda: _make_user(
        UserRole.ADMIN
    )
    try:
        async with AsyncClient(
            transport=ASGITransport(app=_test_app), base_url="http://test"
        ) as client:
            response = await client.get("/admin-or-manager")
        assert response.status_code == 200
    finally:
        _test_app.dependency_overrides.clear()


@pytest.mark.anyio
async def test_require_role_multi_role_manager_accepted() -> None:
    """MANAGER accepted when multiple roles are allowed."""
    _test_app.dependency_overrides[get_current_user] = lambda: _make_user(
        UserRole.MANAGER
    )
    try:
        async with AsyncClient(
            transport=ASGITransport(app=_test_app), base_url="http://test"
        ) as client:
            response = await client.get("/admin-or-manager")
        assert response.status_code == 200
    finally:
        _test_app.dependency_overrides.clear()


@pytest.mark.anyio
async def test_require_role_multi_role_biller_rejected() -> None:
    """BILLER rejected from ADMIN-or-MANAGER endpoint."""
    _test_app.dependency_overrides[get_current_user] = lambda: _make_user(
        UserRole.BILLER
    )
    try:
        async with AsyncClient(
            transport=ASGITransport(app=_test_app), base_url="http://test"
        ) as client:
            response = await client.get("/admin-or-manager")
        assert response.status_code == 403
    finally:
        _test_app.dependency_overrides.clear()
