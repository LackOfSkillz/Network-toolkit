import pytest

from httpx import AsyncClient, ASGITransport

from backend.src.main import app

@pytest.mark.asyncio
async def test_get_configurations_contract():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.get("/configurations")
        # Expect 200 when implemented; will fail if endpoint not present (desired for TDD)
        assert resp.status_code == 200
