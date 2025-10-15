import asyncio
from fastapi.testclient import TestClient
from krishirakshak_backend.main import app
from krishirakshak_backend.db import engine
from sqlmodel import SQLModel
from krishirakshak_backend.config import settings


async def _create_db():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


def test_telegram_text_webhook():
    settings.WEBHOOK_RATE_PER_MIN = 0
    client = TestClient(app)
    asyncio.get_event_loop().run_until_complete(_create_db())
    payload = {"message": {"text": "Hello", "chat": {"id": "123"}}}
    r = client.post("/api/v1/webhooks/telegram", json=payload)
    assert r.status_code == 200
    assert r.json()["ok"] is True


def test_telegram_voice_webhook_enqueues():
    settings.WEBHOOK_RATE_PER_MIN = 0
    client = TestClient(app)
    asyncio.get_event_loop().run_until_complete(_create_db())
    payload = {"message": {"voice": {"file_id": "VOICE_FILE_ID"}, "chat": {"id": "123"}}}
    r = client.post("/api/v1/webhooks/telegram", json=payload)
    assert r.status_code == 200
    assert r.json()["ok"] is True


def test_whatsapp_text_webhook():
    settings.WEBHOOK_RATE_PER_MIN = 0
    client = TestClient(app)
    asyncio.get_event_loop().run_until_complete(_create_db())
    payload = {"From": "+10000000000", "Body": "Hi"}
    r = client.post("/api/v1/webhooks/whatsapp", json=payload)
    assert r.status_code == 200
    assert r.json()["ok"] is True


def test_whatsapp_voice_webhook_enqueues():
    settings.WEBHOOK_RATE_PER_MIN = 0
    client = TestClient(app)
    asyncio.get_event_loop().run_until_complete(_create_db())
    payload = {"From": "+10000000000", "Body": "", "MediaUrl0": "http://example.com/audio.ogg"}
    r = client.post("/api/v1/webhooks/whatsapp", json=payload)
    assert r.status_code == 200
    assert r.json()["ok"] is True
