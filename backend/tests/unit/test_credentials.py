import pytest
from httpx import AsyncClient, ASGITransport
from backend.src.main import app


@pytest.mark.asyncio
async def test_create_and_get_credentials():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # login first
        login = await ac.post("/auth/login", json={"username": "admin", "password": "admin"})
        assert login.status_code == 200
        token = login.json().get("token")
        headers = {"Authorization": f"Bearer {token}"}

        payload = {"name": "cg1", "username": "u1", "password": "p1", "private_key": "key1"}
        resp = await ac.post("/credentials", json=payload, headers=headers)
        assert resp.status_code == 201
        data = resp.json()
        cg_id = data["id"]

        resp2 = await ac.get(f"/credentials/{cg_id}", headers=headers)
        assert resp2.status_code == 200
        got = resp2.json()
        assert got["name"] == "cg1"
        assert got["username"] == "u1"
        assert got["password"] == "p1"
        assert got["private_key"] == "key1"
