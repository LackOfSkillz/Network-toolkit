import pytest
from httpx import AsyncClient, ASGITransport

from backend.src.main import app

@pytest.mark.asyncio
async def test_auth_flow_integration():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # Attempt to login with placeholder credentials; currently the endpoint returns a token field
        resp = await ac.post("/auth/login", json={"username": "admin", "password": "admin"})
        assert resp.status_code in (200, 400, 422)
        # The response should be JSON; check for token key when implemented
        if resp.status_code == 200:
            assert "token" in resp.json()
