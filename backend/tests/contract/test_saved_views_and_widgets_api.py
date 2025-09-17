import pytest
from httpx import AsyncClient, ASGITransport
from backend.src.main import app


@pytest.mark.asyncio
async def test_saved_views_crud():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        login = await ac.post("/auth/login", json={"username": "admin", "password": "admin"})
        token = login.json().get("token")
        headers = {"Authorization": f"Bearer {token}"}

        # create
        payload = {"name": "v1", "view_blob": {"nodes": []}}
        resp = await ac.post("/saved-views", json=payload, headers=headers)
        assert resp.status_code == 201
        sid = resp.json().get("id")

        # get
        resp = await ac.get(f"/saved-views/{sid}", headers=headers)
        assert resp.status_code == 200

        # update
        upd = {"name": "v1-updated", "view_blob": {"nodes": [1]}}
        resp = await ac.put(f"/saved-views/{sid}", json=upd, headers=headers)
        assert resp.status_code == 200

        # list
        resp = await ac.get("/saved-views", headers=headers)
        assert resp.status_code == 200

        # delete
        resp = await ac.delete(f"/saved-views/{sid}", headers=headers)
        assert resp.status_code == 200


@pytest.mark.asyncio
async def test_widgets_crud():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        login = await ac.post("/auth/login", json={"username": "admin", "password": "admin"})
        token = login.json().get("token")
        headers = {"Authorization": f"Bearer {token}"}

        payload = {"name": "w1", "type": "chart", "config": {"kind": "pie"}}
        resp = await ac.post("/dashboard/widgets", json=payload, headers=headers)
        assert resp.status_code == 201
        wid = resp.json().get("id")

        resp = await ac.get(f"/dashboard/widgets/{wid}", headers=headers)
        assert resp.status_code == 200

        # update
        upd_w = {"name": "w1-up", "type": "chart", "config": {"kind": "bar"}}
        resp = await ac.put(f"/dashboard/widgets/{wid}", json=upd_w, headers=headers)
        assert resp.status_code == 200

        resp = await ac.get("/dashboard/widgets", headers=headers)
        assert resp.status_code == 200

        resp = await ac.delete(f"/dashboard/widgets/{wid}", headers=headers)
        assert resp.status_code == 200
