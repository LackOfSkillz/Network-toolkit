import pytest
from httpx import AsyncClient, ASGITransport
from backend.src.main import app


@pytest.mark.asyncio
async def test_what_if_contract():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # we expect auth to be required; use demo credentials
        login = await ac.post("/auth/login", json={"username": "admin", "password": "admin"})
        assert login.status_code == 200
        token = login.json().get("token")
        headers = {"Authorization": f"Bearer {token}"}

        resp = await ac.post("/what-if", json={"action": "deny", "proto": "tcp", "port": 22}, headers=headers)
        assert resp.status_code == 200
