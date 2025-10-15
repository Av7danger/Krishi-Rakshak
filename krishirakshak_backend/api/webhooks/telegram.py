from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.ext.asyncio import AsyncSession
from ...db import get_session
from typing import Optional
from ...models import MessageLog
from ...llm.manager import get_llm_client
from ...integrations.telegram_client import TelegramClient
from ...tasks import transcribe_and_respond, should_run_sync
from ...utils import token_bucket_allow
from ...config import settings

router = APIRouter(prefix="/webhooks", tags=["webhooks"])


@router.post("/telegram")
async def telegram_webhook(update: dict, session: AsyncSession = Depends(get_session), x_telegram_bot_api_secret_token: Optional[str] = Header(default=None)):
    # Optional Telegram verification
    from ...config import settings as cfg
    if cfg.TELEGRAM_WEBHOOK_SECRET and x_telegram_bot_api_secret_token != cfg.TELEGRAM_WEBHOOK_SECRET:
        raise HTTPException(status_code=401, detail="Invalid Telegram secret")
    if not token_bucket_allow("webhook:telegram", settings.WEBHOOK_RATE_PER_MIN):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    # Log inbound message
    msg = MessageLog(source="telegram", direction="in", payload=update)
    session.add(msg)
    await session.commit()
    await session.refresh(msg)

    # Build a simple prompt
    msg_obj = (update.get("message", {}) or {})
    text = msg_obj.get("text") or ""
    llm = get_llm_client()
    reply = llm.generate_reply(f"User said: {text}")

    # Send reply (mock)
    chat_id = str(msg_obj.get("chat", {}).get("id", ""))
    TelegramClient().send_message(chat_id, reply)

    # Save reply
    msg_out = MessageLog(source="telegram", direction="out", reply_text=reply)
    session.add(msg_out)
    await session.commit()

    # If voice/audio, enqueue transcription task
    if (msg_obj.get("voice") or msg_obj.get("audio")) and chat_id:
        file_id = (msg_obj.get("voice") or msg_obj.get("audio") or {}).get("file_id")
        if file_id:
            # For now, pass file_id as media_url surrogate; integrations would download real file
            if should_run_sync():
                from ...tasks import transcribe_and_respond_inner
                await transcribe_and_respond_inner(msg.id, "telegram", file_id, chat_id=chat_id)
            else:
                transcribe_and_respond.delay(msg.id, "telegram", file_id, chat_id=chat_id)

    return {"ok": True}
