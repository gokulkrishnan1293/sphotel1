from fastapi import APIRouter

from app.api.v1.routes.auth_admin import router as admin_router
from app.api.v1.routes.auth_credentials import router as credentials_router
from app.api.v1.routes.auth_pin import router as pin_router
from app.api.v1.routes.auth_reset import router as reset_router
from app.api.v1.routes.auth_session import router as session_router
from app.api.v1.routes.auth_tenant_public import router as tenant_router
from app.api.v1.routes.auth_totp import router as totp_router

router = APIRouter(prefix="/auth", tags=["auth"])
router.include_router(pin_router)
router.include_router(admin_router)
router.include_router(session_router)
router.include_router(totp_router)
router.include_router(credentials_router)
router.include_router(reset_router)
router.include_router(tenant_router)
