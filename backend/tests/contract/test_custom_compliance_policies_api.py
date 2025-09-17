import pytest
from httpx import AsyncClient, ASGITransport
from backend.src.main import app


@pytest.mark.asyncio
async def test_evaluate_policy_api():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        login = await ac.post("/auth/login", json={"username": "admin", "password": "admin"})
        assert login.status_code == 200
        token = login.json().get("token")
        headers = {"Authorization": f"Bearer {token}"}

        payload = {"policy": {"required_rules": [{"protocol": "tcp", "port": 22}]}, "config": {"rules": []}}
        resp = await ac.post("/custom-compliance-policies/evaluate", json=payload, headers=headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["compliant"] is False
