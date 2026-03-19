"""Integration tests for /api/v1/menu/items endpoints (Story 3.3)."""
import uuid
from collections.abc import AsyncGenerator
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.exc import IntegrityError

from app.core.dependencies import CurrentUser, get_current_user
from app.core.security.permissions import FoodType, UserRole
from app.db.session import get_db
from app.db.valkey import get_valkey
from app.main import app
from app.models.menu import MenuItem

TENANT_ID = "testrestaurant"
USER_ID = uuid.uuid4()
ITEM_ID = uuid.uuid4()


def _make_user(role: UserRole = UserRole.ADMIN) -> CurrentUser:
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


def _make_fake_item(
    *,
    item_id: uuid.UUID = ITEM_ID,
    name: str = "Chicken Biryani",
    category: str = "Biryani Varities",
    short_code: int | None = 97,
    price_paise: int = 18000,
    food_type: FoodType = FoodType.NON_VEG,
    description: str | None = None,
    is_available: bool = True,
    display_order: int = 1,
) -> MagicMock:
    fake = MagicMock(spec=MenuItem)
    fake.id = item_id
    fake.tenant_id = TENANT_ID
    fake.name = name
    fake.category = category
    fake.short_code = short_code
    fake.price_paise = price_paise
    fake.food_type = food_type
    fake.description = description
    fake.is_available = is_available
    fake.display_order = display_order
    return fake


# ── GET /menu/items ─────────────────────────────────────────────────────────


@pytest.mark.anyio
async def test_list_items_requires_admin() -> None:
    """Biller role → 403."""
    app.dependency_overrides[get_current_user] = lambda: _make_user(UserRole.BILLER)
    app.dependency_overrides[get_valkey] = _mock_valkey_dep()
    db_mock = AsyncMock()
    app.dependency_overrides[get_db] = _mock_db_dep(db_mock)
    try:
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            resp = await client.get("/api/v1/menu/items")
        assert resp.status_code == 403
    finally:
        app.dependency_overrides.clear()


@pytest.mark.anyio
async def test_list_items_empty() -> None:
    """No items → 200 with empty list."""
    scalars_mock = MagicMock()
    scalars_mock.all.return_value = []
    result_mock = MagicMock()
    result_mock.scalars.return_value = scalars_mock

    db_mock = AsyncMock()
    db_mock.execute = AsyncMock(return_value=result_mock)

    app.dependency_overrides[get_current_user] = lambda: _make_user()
    app.dependency_overrides[get_db] = _mock_db_dep(db_mock)
    app.dependency_overrides[get_valkey] = _mock_valkey_dep()
    try:
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            resp = await client.get("/api/v1/menu/items")
        assert resp.status_code == 200
        body = resp.json()
        assert body["error"] is None
        assert body["data"] == []
    finally:
        app.dependency_overrides.clear()


@pytest.mark.anyio
async def test_list_items_returns_items() -> None:
    """Returns serialized list of menu items."""
    fake_item = _make_fake_item()

    scalars_mock = MagicMock()
    scalars_mock.all.return_value = [fake_item]
    result_mock = MagicMock()
    result_mock.scalars.return_value = scalars_mock

    db_mock = AsyncMock()
    db_mock.execute = AsyncMock(return_value=result_mock)

    app.dependency_overrides[get_current_user] = lambda: _make_user()
    app.dependency_overrides[get_db] = _mock_db_dep(db_mock)
    app.dependency_overrides[get_valkey] = _mock_valkey_dep()
    try:
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            resp = await client.get("/api/v1/menu/items")
        assert resp.status_code == 200
        body = resp.json()
        assert len(body["data"]) == 1
        item = body["data"][0]
        assert item["name"] == "Chicken Biryani"
        assert item["category"] == "Biryani Varities"
        assert item["short_code"] == 97
        assert item["price_paise"] == 18000
        assert item["food_type"] == "non_veg"
        assert item["is_available"] is True
    finally:
        app.dependency_overrides.clear()


# ── POST /menu/items ─────────────────────────────────────────────────────────


@pytest.mark.anyio
async def test_create_item_returns_201() -> None:
    """Valid payload → 201 with created item."""
    fake_item = _make_fake_item()

    db_mock = AsyncMock()
    db_mock.commit = AsyncMock()
    db_mock.refresh = AsyncMock(side_effect=lambda obj: None)

    # Capture added item
    added: list[Any] = []
    def _add(obj: Any) -> None:
        added.append(obj)
        # Inject id/tenant_id for model_validate
        obj.id = ITEM_ID
        obj.tenant_id = TENANT_ID

    db_mock.add = MagicMock(side_effect=_add)

    app.dependency_overrides[get_current_user] = lambda: _make_user()
    app.dependency_overrides[get_db] = _mock_db_dep(db_mock)
    app.dependency_overrides[get_valkey] = _mock_valkey_dep()
    try:
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            resp = await client.post(
                "/api/v1/menu/items",
                json={
                    "name": "Chicken Biryani",
                    "category": "Biryani Varities",
                    "short_code": 97,
                    "price_paise": 18000,
                    "food_type": "non_veg",
                },
            )
        assert resp.status_code == 201
        body = resp.json()
        assert body["error"] is None
        assert body["data"]["name"] == "Chicken Biryani"
        assert body["data"]["food_type"] == "non_veg"
    finally:
        app.dependency_overrides.clear()


@pytest.mark.anyio
async def test_create_item_duplicate_short_code_returns_409() -> None:
    """Duplicate short_code in same tenant → 409."""
    orig = MagicMock()
    orig.__str__ = MagicMock(
        return_value="uq_menu_items_tenant_short_code violates unique constraint"
    )
    integrity_error = IntegrityError(
        statement="INSERT ...", params={}, orig=orig
    )

    db_mock = AsyncMock()
    db_mock.add = MagicMock()
    db_mock.commit = AsyncMock(side_effect=integrity_error)
    db_mock.rollback = AsyncMock()

    app.dependency_overrides[get_current_user] = lambda: _make_user()
    app.dependency_overrides[get_db] = _mock_db_dep(db_mock)
    app.dependency_overrides[get_valkey] = _mock_valkey_dep()
    try:
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            resp = await client.post(
                "/api/v1/menu/items",
                json={
                    "name": "Duplicate Item",
                    "category": "Biryani Varities",
                    "short_code": 97,
                    "price_paise": 10000,
                    "food_type": "veg",
                },
            )
        assert resp.status_code == 409
    finally:
        app.dependency_overrides.clear()


@pytest.mark.anyio
async def test_create_item_invalid_food_type_returns_422() -> None:
    """Invalid food_type enum value → 422 validation error."""
    app.dependency_overrides[get_current_user] = lambda: _make_user()
    db_mock = AsyncMock()
    app.dependency_overrides[get_db] = _mock_db_dep(db_mock)
    app.dependency_overrides[get_valkey] = _mock_valkey_dep()
    try:
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            resp = await client.post(
                "/api/v1/menu/items",
                json={
                    "name": "Veg Item",
                    "category": "Veg",
                    "price_paise": 5000,
                    "food_type": "INVALID",
                },
            )
        assert resp.status_code == 422
    finally:
        app.dependency_overrides.clear()


# ── PATCH /menu/items/{item_id} ──────────────────────────────────────────────


@pytest.mark.anyio
async def test_update_item_returns_200() -> None:
    """PATCH with valid fields → 200 with updated item."""
    fake_item = _make_fake_item()
    fake_item.is_available = False  # toggled

    result_mock = MagicMock()
    result_mock.scalar_one_or_none.return_value = fake_item

    db_mock = AsyncMock()
    db_mock.execute = AsyncMock(return_value=result_mock)
    db_mock.commit = AsyncMock()
    db_mock.refresh = AsyncMock()

    app.dependency_overrides[get_current_user] = lambda: _make_user()
    app.dependency_overrides[get_db] = _mock_db_dep(db_mock)
    app.dependency_overrides[get_valkey] = _mock_valkey_dep()
    try:
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            resp = await client.patch(
                f"/api/v1/menu/items/{ITEM_ID}",
                json={"is_available": False},
            )
        assert resp.status_code == 200
        body = resp.json()
        assert body["error"] is None
        assert body["data"]["is_available"] is False
    finally:
        app.dependency_overrides.clear()


@pytest.mark.anyio
async def test_update_item_wrong_tenant_returns_404() -> None:
    """Item belongs to different tenant → 404."""
    result_mock = MagicMock()
    result_mock.scalar_one_or_none.return_value = None

    db_mock = AsyncMock()
    db_mock.execute = AsyncMock(return_value=result_mock)

    app.dependency_overrides[get_current_user] = lambda: _make_user()
    app.dependency_overrides[get_db] = _mock_db_dep(db_mock)
    app.dependency_overrides[get_valkey] = _mock_valkey_dep()
    try:
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            resp = await client.patch(
                f"/api/v1/menu/items/{uuid.uuid4()}",
                json={"price_paise": 20000},
            )
        assert resp.status_code == 404
        assert "NOT_FOUND" in resp.json()["error"]["message"]
    finally:
        app.dependency_overrides.clear()


# ── DELETE /menu/items/{item_id} ─────────────────────────────────────────────


@pytest.mark.anyio
async def test_delete_item_returns_204() -> None:
    """Delete existing item → 204."""
    fake_item = _make_fake_item()

    result_mock = MagicMock()
    result_mock.scalar_one_or_none.return_value = fake_item

    db_mock = AsyncMock()
    db_mock.execute = AsyncMock(return_value=result_mock)
    db_mock.delete = AsyncMock()
    db_mock.commit = AsyncMock()

    app.dependency_overrides[get_current_user] = lambda: _make_user()
    app.dependency_overrides[get_db] = _mock_db_dep(db_mock)
    app.dependency_overrides[get_valkey] = _mock_valkey_dep()
    try:
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            resp = await client.delete(f"/api/v1/menu/items/{ITEM_ID}")
        assert resp.status_code == 204
    finally:
        app.dependency_overrides.clear()


@pytest.mark.anyio
async def test_delete_item_wrong_tenant_returns_404() -> None:
    """Item not found for tenant → 404."""
    result_mock = MagicMock()
    result_mock.scalar_one_or_none.return_value = None

    db_mock = AsyncMock()
    db_mock.execute = AsyncMock(return_value=result_mock)

    app.dependency_overrides[get_current_user] = lambda: _make_user()
    app.dependency_overrides[get_db] = _mock_db_dep(db_mock)
    app.dependency_overrides[get_valkey] = _mock_valkey_dep()
    try:
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            resp = await client.delete(f"/api/v1/menu/items/{uuid.uuid4()}")
        assert resp.status_code == 404
        assert "NOT_FOUND" in resp.json()["error"]["message"]
    finally:
        app.dependency_overrides.clear()
