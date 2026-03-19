from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import CurrentUser, require_role
from app.core.security.permissions import UserRole
from app.core.security.pin import hash_pin
from app.db.session import get_db
from app.models.audit_log import AuditLog
from app.models.user import TenantUser
from app.schemas.auth import MeResponse, UpdateCredentialsRequest
from app.schemas.common import DataResponse

router = APIRouter()


@router.patch("/credentials", response_model=DataResponse[MeResponse])
async def update_credentials(
    body: UpdateCredentialsRequest,
    current_user: CurrentUser = Depends(
        require_role(UserRole.ADMIN, UserRole.SUPER_ADMIN)
    ),
    db: AsyncSession = Depends(get_db),
) -> DataResponse[MeResponse]:
    """Admin/Super-Admin self-service credential update."""
    updates: dict[str, object] = {}

    if body.email is not None:
        dupe = await db.execute(
            select(TenantUser).where(
                func.lower(TenantUser.email) == body.email.lower(),
                TenantUser.id != current_user["user_id"],
            )
        )
        if dupe.scalar_one_or_none() is not None:
            raise HTTPException(
                status_code=409,
                detail={"code": "EMAIL_TAKEN", "message": "Email already in use"},
            )
        updates["email"] = body.email.lower()

    if body.password is not None:
        updates["password_hash"] = hash_pin(body.password)

    await db.execute(
        update(TenantUser)
        .where(TenantUser.id == current_user["user_id"])
        .values(**updates)
    )
    db.add(AuditLog(
        tenant_id=current_user["tenant_id"],
        actor_id=current_user["user_id"],
        action="credentials_update",
        payload={"changed": list(updates.keys())},
    ))
    await db.commit()

    result = await db.execute(
        select(TenantUser).where(TenantUser.id == current_user["user_id"])
    )
    user = result.scalar_one()
    return DataResponse(data=MeResponse.model_validate(user))
