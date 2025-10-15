import os
import asyncio
from datetime import datetime
from celery import Celery
from sqlalchemy.ext.asyncio import AsyncSession
from .config import settings
from .inference.runner import run_mock_inference
from .models import Report
from .db import AsyncSessionLocal
from .stt.manager import get_stt_client
from .llm.manager import get_llm_client
from .tts.manager import get_tts_client
from .storage import storage

celery_app = Celery(__name__, broker=settings.CELERY_BROKER_URL, backend=settings.CELERY_RESULT_BACKEND)


async def run_inference_and_update(session: AsyncSession, report_id: int) -> None:
    from typing import Optional
    report: Optional[Report] = await session.get(Report, report_id)
    if not report:
        return
    report.status = "processing"
    await session.commit()
    await session.refresh(report)

    result = run_mock_inference(report.image_path)
    report.disease = result.get("disease")
    report.confidence = float(result.get("confidence", 0.0))
    report.treatment = result.get("treatment")
    report.status = "processed"
    report.processed_at = datetime.utcnow()
    await session.commit()
    await session.refresh(report)

    # Best-effort websocket broadcast (works in same process / dev mode)
    try:
        from .api.websocket import manager  # lazy import to avoid circulars
        if settings.WS_ENABLED and report.farmer_id:
            payload = {
                "type": "report_update",
                "report_id": report.id,
                "status": report.status,
                "disease": report.disease,
                "confidence": report.confidence,
                "treatment": report.treatment,
                "processed_at": report.processed_at.isoformat() if report.processed_at else None,
            }
            await manager.send_json_to_farmer(report.farmer_id, payload)
    except Exception:
        # ignore broadcast errors in tasks
        pass


def should_run_sync() -> bool:
    # Fallback to synchronous execution when running in development or tests
    return settings.APP_ENV != "production"


# Production Celery task wrapper with retries/backoff
@celery_app.task(bind=True, autoretry_for=(Exception,), retry_backoff=5, retry_backoff_max=60, retry_jitter=True, max_retries=3)
def inference_task(self, report_id: int) -> None:
    async def _runner() -> None:
        async with AsyncSessionLocal() as session:
            await run_inference_and_update(session, report_id)

    asyncio.run(_runner())


from typing import Optional


async def transcribe_and_respond_inner(message_id: int, source: str, media_url: str, chat_id: Optional[str] = None, to_phone: Optional[str] = None) -> None:
    stt = get_stt_client()
    llm = get_llm_client()
    tts = get_tts_client()
    # Download media
    local_path = storage.download_to_local(media_url)
    transcript = stt.transcribe(local_path)
    prompt = f"Transcribed user message: {transcript}\nProvide a concise advisory."
    reply_text = llm.generate_reply(prompt)
    reply_audio: bytes | None = None
    if settings.TTS_ENABLED:
        audio = tts.synthesize(reply_text)
        if audio:
            reply_audio = audio
    # Send via integration client (mock)
    if source == "telegram":
        from .integrations.telegram_client import TelegramClient
        if chat_id:
            TelegramClient().send_message(chat_id, reply_text)
    elif source == "whatsapp":
        from .integrations.twilio_client import TwilioClient
        if to_phone:
            TwilioClient().send_whatsapp_message(to_phone, reply_text)
    # Log to MessageLog
    async with AsyncSessionLocal() as session:
        from .models import MessageLog
        ml = MessageLog(source=source, direction="out", reply_text=reply_text)
        session.add(ml)
        await session.commit()


@celery_app.task(bind=True, autoretry_for=(Exception,), retry_backoff=5, retry_backoff_max=60, retry_jitter=True, max_retries=3)
def transcribe_and_respond(self, message_id: int, source: str, media_url: str, chat_id: Optional[str] = None, to_phone: Optional[str] = None) -> None:  # type: ignore
    asyncio.run(transcribe_and_respond_inner(message_id, source, media_url, chat_id, to_phone))
