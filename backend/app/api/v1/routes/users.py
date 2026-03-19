from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import CurrentUser, get_current_user
from app.db.session import get_db
from app.models.user import TenantUser
from app.schemas.auth import MeResponse
from app.schemas.common import DataResponse
from app.schemas.users import PreferencesUpdateRequest

router = APIRouter(prefix="/users", tags=["users"])


@router.patch("/me/preferences", response_model=DataResponse[MeResponse])
async def update_my_preferences(
    body: PreferencesUpdateRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> DataResponse[MeResponse]:
    """Update authenticated user's display preference. All roles permitted."""
    result = await db.execute(
        select(TenantUser).where(TenantUser.id == current_user["user_id"])
    )
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(
            status_code=404,
            detail={"code": "NOT_FOUND", "message": "User not found"},
        )

    # Merge into existing preferences dict (preserves any future keys)
    current_prefs: dict[str, object] = dict(user.preferences or {})
    current_prefs["theme"] = body.theme

    await db.execute(
        update(TenantUser)
        .where(TenantUser.id == current_user["user_id"])
        .values(preferences=current_prefs)
    )
    await db.commit()

    result2 = await db.execute(
        select(TenantUser).where(TenantUser.id == current_user["user_id"])
    )
    user2 = result2.scalar_one()
    return DataResponse(data=MeResponse.model_validate(user2))
