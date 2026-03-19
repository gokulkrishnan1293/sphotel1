from fastapi import APIRouter
from pydantic import BaseModel

from app.core.config import settings
from app.schemas.common import DataResponse

router = APIRouter(tags=["health"])


class HealthStatus(BaseModel):
    status: str
    version: str


@router.api_route("/health", methods=["GET", "HEAD"], response_model=DataResponse[HealthStatus])
async def health_check() -> DataResponse[HealthStatus]:
    """Health check endpoint. Returns status and version."""
    return DataResponse(data=HealthStatus(status="ok", version=settings.VERSION))
