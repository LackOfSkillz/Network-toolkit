import pytest
from httpx import AsyncClient, ASGITransport
from backend.src.main import app


@pytest.mark.asyncio
async def test_drift_detection_api():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # login to get token
        login = await ac.post("/auth/login", json={"username": "admin", "password": "admin"})
        assert login.status_code == 200
        token = login.json().get("token")
        headers = {"Authorization": f"Bearer {token}"}

        desired = {"d1": {"rules": [{"id": "r1", "action": "allow", "protocol": "tcp", "port": 22}]}}
        observed = {"d1": {"rules": []}}
        payload = {"desired": desired, "observed": observed}

        resp = await ac.post("/drift-detection", json=payload, headers=headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "report" in data
        assert "d1" in data["report"]
        assert data["report"]["d1"]["missing"] == [{"id": "r1", "action": "allow", "protocol": "tcp", "port": 22}]
