import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.feature_flags import TenantFeatureFlags
from app.schemas.feature_flags import DEFAULT_FLAGS, FeatureFlagsDict


async def get_feature_flags_from_db(
    tenant_id: uuid.UUID, db: AsyncSession
) -> FeatureFlagsDict:
    """Read feature flags for a tenant from PostgreSQL.

    Returns DEFAULT_FLAGS (all False) when the tenant has no row yet —
    this is the expected state for new tenants before any flags are toggled.
    """
    result = await db.execute(
        select(TenantFeatureFlags).where(
            TenantFeatureFlags.tenant_id == tenant_id
        )
    )
    row = result.scalar_one_or_none()

    if row is None:
        return DEFAULT_FLAGS

    return FeatureFlagsDict(
        waiter_mode=row.waiter_mode,
        suggestion_engine=row.suggestion_engine,
        telegram_alerts=row.telegram_alerts,
        gst_module=row.gst_module,
        payroll_rewards=row.payroll_rewards,
        discount_complimentary=row.discount_complimentary,
        waiter_transfer=row.waiter_transfer,
        bill_close_ux=row.bill_close_ux,
    )
