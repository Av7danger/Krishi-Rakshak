# KrishiRakshak Backend

FastAPI backend for Android, Web Dashboard, and Voice/Chat (WhatsApp + Telegram).

## Features
- Auth (JWT), image upload with async inference (mock), report CRUD, feedback
- CORS configurable; WebSocket stub for realtime
- Webhooks for Telegram/WhatsApp (mock clients), LLM/STT mock managers
- Celery + Redis scaffolding with local sync fallback
- Storage: local filesystem with MinIO placeholders
- Docker Compose and GitHub Actions CI

## Security & Auth
- Mobile uses Bearer JWT; web can rely on a cookie set at login (`krishi_token`).
- Rate limits configurable via `.env`: `UPLOAD_RATE_PER_MIN`, `WEBHOOK_RATE_PER_MIN`.
- Upload validation: `ALLOWED_IMAGE_MIME` and `MAX_UPLOAD_MB`.
- Webhook verification:
  - Telegram: set `TELEGRAM_WEBHOOK_SECRET` and send header `X-Telegram-Bot-Api-Secret-Token`.
  - Twilio: placeholder `X-Twilio-Signature` accepted; add real HMAC check if desired.

## Quickstart (Local Dev)
1. Create and activate a Python 3.11+ venv, then install deps:
   ```bash
   pip install -e .[dev]
   ```
2. Copy env:
   ```bash
   cp .env.example .env
   ```
3. Run API:
   ```bash
   uvicorn krishirakshak_backend.main:app --reload
   ```
4. Open API docs at `http://localhost:8000/docs`.

## Docker (DB/Redis/MinIO)
```bash
docker compose up --build
```
Backend on `http://localhost:8000`.

## Endpoints
- POST `POST /api/v1/auth/register`
- POST `POST /api/v1/auth/login`
- GET  `/api/v1/me`
- POST `/api/v1/upload` (multipart `file`; optional fields: `crop_type`, `lat`, `lon`, `farmer_id`, `consent_for_training`)
- GET  `/api/v1/reports?farmer_id=...`
- GET  `/api/v1/reports/{id}`
- POST `/api/v1/feedback`
- POST `/api/v1/webhooks/telegram`
- POST `/api/v1/webhooks/whatsapp`
- WS   `/ws/`
### Additional
- DELETE `/api/v1/auth/me` to delete the current account

## Mock vs Real
- `LLM_MODE=MOCK|OPENAI|LOCAL` (OPENAI requires `OPENAI_API_KEY`)
- `STT_MODE=MOCK` placeholder
- `TELEGRAM_ENABLED=false`, `WHATSAPP_ENABLED=false`
 - `USE_MINIO=true` to store uploads in MinIO/S3-compatible storage. Signed URLs available via storage helper.

## Android emulator
Use `http://10.0.2.2:8000/api/v1/upload`.

## Privacy & Consent
- `consent_for_training` stored with each `Report` and on `Farmer` profile.

## Tests
```bash
pytest -q
```

## Notes
- For production, wire real MinIO/S3 in `storage.py`, real Celery tasks in `tasks.py`, and real integrations in `integrations/*`.
