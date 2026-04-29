import pytest
from httpx import AsyncClient, ASGITransport
from main import app


@pytest.mark.asyncio
async def test_health_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] in ["ok", "healthy"]


@pytest.mark.asyncio
async def test_login_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/auth/login",
            json={"username": "admin", "password": "admin123"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "token" in data
        assert "user" in data


@pytest.mark.asyncio
async def test_login_invalid_credentials():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/auth/login",
            json={"username": "admin", "password": "wrong"}
        )
        assert response.status_code == 401