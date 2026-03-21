import os
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.tenant import Tenant

router = APIRouter(prefix="/public", tags=["public"])

@router.get("/manifest.json")
async def get_manifest(request: Request, db: AsyncSession = Depends(get_db)):
    """Generate a dynamic PWA manifest based on the Host header."""
    host = request.headers.get("host", "")
    
    # Default Nive Chain Manager (Admin) manifest
    if host.startswith("managehotels") or not host:
        return JSONResponse({
            "name": "Nive's Chain Manager",
            "short_name": "Chain Manager",
            "start_url": "/",
            "display": "standalone",
            "background_color": "#09090b",
            "theme_color": "#09090b",
            "icons": [
                {
                    "src": "/pwa-192x192.png",
                    "sizes": "192x192",
                    "type": "image/png"
                },
                {
                    "src": "/pwa-512x512.png",
                    "sizes": "512x512",
                    "type": "image/png"
                }
            ]
        })

    # Find tenant by slug (assuming slug is the first part of the subdomain)
    slug = host.split(".")[0]
    result = await db.execute(select(Tenant).where(Tenant.slug == slug))
    tenant = result.scalar_one_or_none()
    
    if not tenant:
        # Fallback to default if tenant not found
        return JSONResponse({
            "name": "SP Hotel",
            "short_name": "SP Hotel",
            "start_url": "/",
            "display": "standalone",
            "background_color": "#09090b",
            "theme_color": "#09090b",
            "icons": [
                {
                    "src": "/pwa-192x192.png",
                    "sizes": "192x192",
                    "type": "image/png"
                }
            ]
        })

    pwa = tenant.pwa_settings or {}
    app_name = pwa.get("app_name") or tenant.name
    app_short_name = pwa.get("app_short_name") or app_name[:12]
    
    logo_url = f"/api/v1/public/logo/{tenant.slug}.png" if tenant.logo_path else "/pwa-192x192.png"

    return JSONResponse({
        "name": app_name,
        "short_name": app_short_name,
        "start_url": "/",
        "display": "standalone",
        "background_color": "#09090b",
        "theme_color": "#09090b",
        "icons": [
            {
                "src": logo_url,
                "sizes": "512x512",
                "type": "image/png",
                "purpose": "any maskable"
            }
        ]
    })

@router.get("/logo/{tenant_slug}.png")
async def get_logo(tenant_slug: str, db: AsyncSession = Depends(get_db)):
    """Serve the custom logo for a tenant."""
    result = await db.execute(select(Tenant).where(Tenant.slug == tenant_slug))
    tenant = result.scalar_one_or_none()
    
    if not tenant or not tenant.logo_path:
        # Fallback to default logo in backend static folder
        default_logo = os.path.join("app", "static", "default-logo.png")
        if os.path.exists(default_logo):
            return FileResponse(default_logo)
        raise HTTPException(status_code=404, detail="Default logo not found")

    if not os.path.exists(tenant.logo_path):
        raise HTTPException(status_code=404, detail="Logo file not found on disk")

    return FileResponse(tenant.logo_path)
