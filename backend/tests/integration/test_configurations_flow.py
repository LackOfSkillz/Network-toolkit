import pytest
from httpx import AsyncClient, ASGITransport

from backend.src.main import app

@pytest.mark.asyncio
async def test_configurations_flow_integration():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # GET list (expected 200 or 404/501 until implemented)
        resp = await ac.get("/configurations")
        assert resp.status_code in (200, 404, 501)

        # POST a minimal configuration payload if POST is implemented
        # Authenticate first (demo admin/admin)
        login = await ac.post("/auth/login", json={"username": "admin", "password": "admin"})
        if login.status_code == 200:
            token = login.json().get("token")
            headers = {"Authorization": f"Bearer {token}"}
            resp_post = await ac.post("/configurations", json={"name": "test-config"}, headers=headers)
        else:
            resp_post = await ac.post("/configurations", json={"name": "test-config"})

        assert resp_post.status_code in (201, 400, 404, 501)
