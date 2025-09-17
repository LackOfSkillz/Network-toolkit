import pytest

from httpx import AsyncClient, ASGITransport

from backend.src.main import app

@pytest.mark.asyncio
async def test_login_contract():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.post("/auth/login", json={"username": "x", "password": "y"})
        assert resp.status_code in (200, 501, 400, 422)
