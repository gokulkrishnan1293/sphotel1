import uuid
from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.schemas.feature_flags import DEFAULT_FLAGS, FeatureFlagsDict

_KNOWN_TENANT_ID = uuid.UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa")

_ALL_ENABLED_FLAGS = FeatureFlagsDict(
    waiter_mode=True,
    suggestion_engine=True,
    telegram_alerts=True,
    gst_module=True,
    payroll_rewards=True,
    discount_complimentary=True,
    waiter_transfer=True,
)


def _make_mock_valkey() -> AsyncMock:
    mock = AsyncMock()
    mock.get.return_value = None  # cache miss — go to DB
    mock.set.return_value = True
    mock.aclose.return_value = None
    return mock


@pytest.mark.asyncio
async def test_get_tenant_features_returns_200() -> None:
    """GET /tenants/{id}/features must return HTTP 200."""
    mock_valkey = _make_mock_valkey()

    with (
        patch("app.db.valkey.aioredis") as mock_aioredis,
        patch(
            "app.services.feature_flags.get_feature_flags_from_db",
            return_value=DEFAULT_FLAGS,
        ),
    ):
        mock_aioredis.Redis.from_url.return_value = mock_valkey
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.get(
                f"/api/v1/tenants/{_KNOWN_TENANT_ID}/features"
            )

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_tenant_features_envelope_structure() -> None:
    """Response must follow {data, error} envelope with error null."""
    mock_valkey = _make_mock_valkey()

    with (
        patch("app.db.valkey.aioredis") as mock_aioredis,
        patch(
            "app.services.feature_flags.get_feature_flags_from_db",
            return_value=DEFAULT_FLAGS,
        ),
    ):
        mock_aioredis.Redis.from_url.return_value = mock_valkey
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.get(
                f"/api/v1/tenants/{_KNOWN_TENANT_ID}/features"
            )

    body = response.json()
    assert set(body.keys()) == {"data", "error"}
    assert body["error"] is None


@pytest.mark.asyncio
async def test_get_tenant_features_camel_case_keys() -> None:
    """Feature flag keys in response must be camelCase."""
    mock_valkey = _make_mock_valkey()

    with (
        patch("app.db.valkey.aioredis") as mock_aioredis,
        patch(
            "app.services.feature_flags.get_feature_flags_from_db",
            return_value=DEFAULT_FLAGS,
        ),
    ):
        mock_aioredis.Redis.from_url.return_value = mock_valkey
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.get(
                f"/api/v1/tenants/{_KNOWN_TENANT_ID}/features"
            )

    data = response.json()["data"]
    expected_keys = {
        "waiterMode",
        "suggestionEngine",
        "telegramAlerts",
        "gstModule",
        "payrollRewards",
        "discountComplimentary",
        "waiterTransfer",
    }
    assert set(data.keys()) == expected_keys


@pytest.mark.asyncio
async def test_get_tenant_features_unknown_tenant_returns_all_false() -> None:
    """Unknown tenant ID must return all-false flags (no 404)."""
    unknown_id = uuid.uuid4()
    mock_valkey = _make_mock_valkey()

    with (
        patch("app.db.valkey.aioredis") as mock_aioredis,
        patch(
            "app.services.feature_flags.get_feature_flags_from_db",
            return_value=DEFAULT_FLAGS,
        ),
    ):
        mock_aioredis.Redis.from_url.return_value = mock_valkey
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.get(
                f"/api/v1/tenants/{unknown_id}/features"
            )

    assert response.status_code == 200
    data = response.json()["data"]
    assert all(v is False for v in data.values())


@pytest.mark.asyncio
async def test_get_tenant_features_returns_enabled_flags() -> None:
    """When tenant has flags enabled, response must reflect them correctly."""
    mock_valkey = _make_mock_valkey()

    with (
        patch("app.db.valkey.aioredis") as mock_aioredis,
        patch(
            "app.services.feature_flags.get_feature_flags_from_db",
            return_value=_ALL_ENABLED_FLAGS,
        ),
    ):
        mock_aioredis.Redis.from_url.return_value = mock_valkey
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.get(
                f"/api/v1/tenants/{_KNOWN_TENANT_ID}/features"
            )

    data = response.json()["data"]
    assert data["waiterMode"] is True
    assert data["suggestionEngine"] is True
    assert data["waiterTransfer"] is True


@pytest.mark.asyncio
async def test_get_tenant_features_invalid_uuid_returns_422() -> None:
    """Invalid tenant UUID path parameter must return HTTP 422."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/api/v1/tenants/not-a-uuid/features")

    assert response.status_code == 422
