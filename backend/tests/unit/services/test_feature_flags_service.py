import json
import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.schemas.feature_flags import DEFAULT_FLAGS, FeatureFlagsDict
from app.services.feature_flags import get_feature_flags


@pytest.fixture
def tenant_id() -> uuid.UUID:
    return uuid.UUID("12345678-1234-5678-1234-567812345678")


@pytest.fixture
def sample_flags() -> FeatureFlagsDict:
    return FeatureFlagsDict(
        waiter_mode=True,
        suggestion_engine=False,
        telegram_alerts=True,
        gst_module=False,
        payroll_rewards=False,
        discount_complimentary=False,
        waiter_transfer=False,
    )


@pytest.mark.asyncio
async def test_cache_hit_returns_flags_without_db(
    tenant_id: uuid.UUID, sample_flags: FeatureFlagsDict
) -> None:
    """On Valkey cache hit, DB must NOT be queried."""
    mock_valkey = AsyncMock()
    mock_valkey.get.return_value = json.dumps(sample_flags)
    mock_db = AsyncMock()

    with patch(
        "app.services.feature_flags.get_feature_flags_from_db"
    ) as mock_repo:
        result = await get_feature_flags(tenant_id, mock_db, mock_valkey)

    mock_repo.assert_not_called()
    assert result["waiter_mode"] is True
    assert result["telegram_alerts"] is True


@pytest.mark.asyncio
async def test_cache_miss_reads_db_and_sets_cache(
    tenant_id: uuid.UUID, sample_flags: FeatureFlagsDict
) -> None:
    """On Valkey cache miss, DB is queried and result is cached."""
    mock_valkey = AsyncMock()
    mock_valkey.get.return_value = None  # cache miss
    mock_db = AsyncMock()

    with patch(
        "app.services.feature_flags.get_feature_flags_from_db",
        return_value=sample_flags,
    ) as mock_repo:
        result = await get_feature_flags(tenant_id, mock_db, mock_valkey)

    mock_repo.assert_called_once_with(tenant_id, mock_db)
    mock_valkey.set.assert_called_once()
    set_call_args = mock_valkey.set.call_args
    assert set_call_args.kwargs["ex"] == 60
    assert result == sample_flags


@pytest.mark.asyncio
async def test_valkey_error_falls_back_to_db(
    tenant_id: uuid.UUID, sample_flags: FeatureFlagsDict
) -> None:
    """When Valkey raises an exception, service falls back to DB silently."""
    mock_valkey = AsyncMock()
    mock_valkey.get.side_effect = ConnectionError("Valkey unavailable")
    mock_db = AsyncMock()

    with patch(
        "app.services.feature_flags.get_feature_flags_from_db",
        return_value=sample_flags,
    ) as mock_repo:
        result = await get_feature_flags(tenant_id, mock_db, mock_valkey)

    mock_repo.assert_called_once_with(tenant_id, mock_db)
    assert result == sample_flags


@pytest.mark.asyncio
async def test_valkey_write_error_does_not_fail_request(
    tenant_id: uuid.UUID, sample_flags: FeatureFlagsDict
) -> None:
    """When Valkey set() raises, the service still returns flags successfully."""
    mock_valkey = AsyncMock()
    mock_valkey.get.return_value = None  # cache miss
    mock_valkey.set.side_effect = ConnectionError("Valkey write failed")
    mock_db = AsyncMock()

    with patch(
        "app.services.feature_flags.get_feature_flags_from_db",
        return_value=sample_flags,
    ):
        result = await get_feature_flags(tenant_id, mock_db, mock_valkey)

    assert result == sample_flags


@pytest.mark.asyncio
async def test_unknown_tenant_returns_default_flags(
    tenant_id: uuid.UUID,
) -> None:
    """When tenant has no DB row, service returns all-false DEFAULT_FLAGS."""
    mock_valkey = AsyncMock()
    mock_valkey.get.return_value = None  # cache miss
    mock_db = AsyncMock()

    with patch(
        "app.services.feature_flags.get_feature_flags_from_db",
        return_value=DEFAULT_FLAGS,
    ):
        result = await get_feature_flags(tenant_id, mock_db, mock_valkey)

    assert result == DEFAULT_FLAGS
    assert result["waiter_mode"] is False
