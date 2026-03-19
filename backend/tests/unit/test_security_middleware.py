import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.mark.anyio
async def test_x_frame_options_deny() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/api/v1/health")
    assert response.headers.get("x-frame-options") == "DENY"


@pytest.mark.anyio
async def test_x_content_type_options_nosniff() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/api/v1/health")
    assert response.headers.get("x-content-type-options") == "nosniff"


@pytest.mark.anyio
async def test_hsts_header_present() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/api/v1/health")
    hsts = response.headers.get("strict-transport-security", "")
    assert "max-age=31536000" in hsts
    assert "includeSubDomains" in hsts


@pytest.mark.anyio
async def test_csp_header_present() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/api/v1/health")
    csp = response.headers.get("content-security-policy")
    assert csp is not None
    assert len(csp) > 0


@pytest.mark.anyio
async def test_referrer_policy_header() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/api/v1/health")
    assert (
        response.headers.get("referrer-policy") == "strict-origin-when-cross-origin"
    )


@pytest.mark.anyio
async def test_no_wildcard_cors() -> None:
    from app.core.config import settings

    assert "*" not in settings.CORS_ORIGINS
