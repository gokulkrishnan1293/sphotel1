import logging
import uuid

from fastapi import HTTPException
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit_log import AuditLog
from app.models.tenant import Tenant
from app.schemas.tenant import TenantCreateRequest

logger = logging.getLogger(__name__)


async def provision_tenant(
    req: TenantCreateRequest,
    db: AsyncSession,
    actor_id: uuid.UUID,
) -> Tenant:
    """Create tenant and bill sequence atomically.

    Returns the tenant ORM object.
    Raises HTTP 409 if subdomain is already taken.
    """
    existing = await db.execute(select(Tenant).where(Tenant.slug == req.subdomain))
    if existing.scalar_one_or_none() is not None:
        raise HTTPException(
            status_code=409,
            detail={
                "code": "CONFLICT",
                "message": f"Subdomain '{req.subdomain}' is already taken",
            },
        )

    tenant = Tenant(name=req.name, slug=req.subdomain)
    db.add(tenant)
    await db.flush()

    seq_id = str(tenant.id).replace("-", "_")
    await db.execute(
        text(f"CREATE SEQUENCE IF NOT EXISTS tenant_{seq_id}_bill_seq START 1")
    )

    db.add(AuditLog(
        tenant_id=str(tenant.id),
        actor_id=actor_id,
        action="tenant_provisioned",
        target_id=tenant.id,
        payload={"tenant_name": req.name, "slug": req.subdomain},
    ))
    await db.commit()
    await db.refresh(tenant)

    logger.info("Tenant provisioned: id=%s slug=%s", tenant.id, req.subdomain)
    return tenant
