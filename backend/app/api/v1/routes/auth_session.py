import time
from typing import Any

import jwt
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import CurrentUser, get_current_user
from app.core.security.jwt import decode_access_token
from app.db.session import get_db
from app.db.valkey import get_valkey
from app.models.user import TenantUser
from app.schemas.auth import MeResponse
from app.schemas.common import DataResponse, MessageResponse

router = APIRouter()


@router.post("/logout", response_model=DataResponse[MessageResponse])
async def logout(
    request: Request,
    response: Response,
    valkey: Any = Depends(get_valkey),
) -> DataResponse[MessageResponse]:
    """Invalidate session in Valkey and clear httpOnly cookie."""
    token = request.cookies.get("access_token")
    if token:
        try:
            payload = decode_access_token(token)
            user_id_str = str(payload["user_id"])
            exp = float(str(payload.get("exp", 0)))
            iat = float(str(payload.get("iat", 0)))
            remaining_ttl = max(1, int(exp - time.time()))
            await valkey.set(
                f"session_revoked:{user_id_str}", str(iat), ex=remaining_ttl
            )
        except jwt.InvalidTokenError:
            pass
    response.delete_cookie(key="access_token", path="/api")
    return DataResponse(data=MessageResponse(message="Logged out successfully"))


@router.get("/me", response_model=DataResponse[MeResponse])
async def get_me(
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> DataResponse[MeResponse]:
    """Return authenticated user's profile. All roles allowed."""
    result = await db.execute(
        select(TenantUser).where(TenantUser.id == current_user["user_id"])
    )
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(
            status_code=404,
            detail={"code": "NOT_FOUND", "message": "User not found"},
        )
    return DataResponse(data=MeResponse.model_validate(user))
