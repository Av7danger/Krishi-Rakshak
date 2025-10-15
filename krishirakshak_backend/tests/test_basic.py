import asyncio
import io
import os
from fastapi.testclient import TestClient
from sqlmodel import SQLModel
from krishirakshak_backend.main import app
from krishirakshak_backend.db import engine


async def _create_db():
    # ensure fresh sqlite db per run
    try:
        os.remove("krishi.db")
    except FileNotFoundError:
        pass
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


def test_root():
    client = TestClient(app)
    r = client.get("/")
    assert r.status_code == 200
    assert r.json()["ok"] is True


def test_auth_register_login_and_upload(tmp_path):
    client = TestClient(app)
    asyncio.get_event_loop().run_until_complete(_create_db())

    # register
    r = client.post("/api/v1/auth/register", json={
        "phone": "+1234567890",
        "name": "Farmer",
        "password": "secret",
        "consent_for_training": True
    })
    assert r.status_code == 200
    farmer = r.json()

    # login
    r = client.post("/api/v1/auth/login", json={"phone": "+1234567890", "password": "secret"})
    assert r.status_code == 200
    token = r.json()["access_token"]
    assert token

    # upload
    img = open("krishirakshak_backend/tests/data/leaf.jpg", "rb").read()
    files = {"file": ("leaf.jpg", img, "image/jpeg")}
    data = {"crop_type": "wheat", "farmer_id": farmer["id"], "consent_for_training": True}
    r = client.post("/api/v1/upload", files=files, data=data)
    assert r.status_code == 200
    payload = r.json()
    assert payload["report_id"] > 0
    assert payload["status"] in ("queued", "processed")

    # list reports
    r = client.get(f"/api/v1/reports?farmer_id={farmer['id']}")
    assert r.status_code == 200
    items = r.json()
    assert len(items) >= 1
