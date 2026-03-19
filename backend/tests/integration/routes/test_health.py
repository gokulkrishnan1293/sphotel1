import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.mark.asyncio
async def test_health_returns_200() -> None:
    """GET /api/v1/health must respond with HTTP 200."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/api/v1/health")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_health_response_body() -> None:
    """GET /api/v1/health must return the correct envelope and payload."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/api/v1/health")
    body = response.json()
    assert body["error"] is None
    assert body["data"]["status"] == "ok"
    assert body["data"]["version"] == "0.1.0"


@pytest.mark.asyncio
async def test_health_content_type_is_json() -> None:
    """GET /api/v1/health must return Content-Type: application/json."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/api/v1/health")
    assert "application/json" in response.headers["content-type"]


@pytest.mark.asyncio
async def test_health_response_matches_envelope_schema() -> None:
    """GET /api/v1/health response must have exactly 'data' and 'error' keys."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/api/v1/health")
    body = response.json()
    assert set(body.keys()) == {"data", "error"}
    assert set(body["data"].keys()) == {"status", "version"}
