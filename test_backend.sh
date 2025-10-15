#!/usr/bin/env bash
set -euo pipefail

# Simple end-to-end tester for the KrishiRakshak FastAPI backend.
# It exercises: health, register, login (JWT), upload, list reports, and feedback.
#
# Requirements:
# - Backend running locally (default: http://localhost:8000)
# - jq installed for pretty JSON

BASE_URL="http://localhost:8000"
API="/api/v1"
IMG_PATH="krishirakshak_backend/tests/data/leaf.jpg"  # change if needed

echo "1️⃣ Health check (GET /)"
curl -sS "${BASE_URL}/" | jq . || { echo "Health check failed" >&2; exit 1; }
echo

PHONE="+1999000111"
NAME="Tester"
PASSWORD="secret"

echo "2️⃣ Register a new user (POST ${API}/auth/register)"
REGISTER_RESP=$(curl -sS -X POST "${BASE_URL}${API}/auth/register" \
  -H 'Content-Type: application/json' \
  -d "{\"phone\": \"${PHONE}\", \"name\": \"${NAME}\", \"password\": \"${PASSWORD}\", \"consent_for_training\": true}")
echo "$REGISTER_RESP" | jq . || true
FARMER_ID=$(echo "$REGISTER_RESP" | jq -r '.id // empty')
echo "farmer_id=${FARMER_ID:-<empty>}"
echo

echo "3️⃣ Login and get JWT (POST ${API}/auth/login)"
LOGIN_RESP=$(curl -sS -X POST "${BASE_URL}${API}/auth/login" \
  -H 'Content-Type: application/json' \
  -d "{\"phone\": \"${PHONE}\", \"password\": \"${PASSWORD}\"}")
echo "$LOGIN_RESP" | jq . || true
TOKEN=$(echo "$LOGIN_RESP" | jq -r '.access_token // empty')
if [[ -z "$TOKEN" ]]; then
  echo "Failed to obtain JWT token" >&2
  exit 1
fi
echo "token_length=${#TOKEN}"
echo

if [[ ! -f "$IMG_PATH" ]]; then
  echo "Image not found at $IMG_PATH" >&2
  exit 1
fi

echo "4️⃣ Upload a test file (POST ${API}/upload)"
UPLOAD_HTTP=$(curl -sS -o /tmp/krishi_upload.json -w "%{http_code}" -X POST "${BASE_URL}${API}/upload" \
  -H "Authorization: Bearer ${TOKEN}" \
  -F file=@"${IMG_PATH}" \
  -F crop_type=wheat \
  -F lat=12.34 \
  -F lon=56.78 \
  -F farmer_id="${FARMER_ID:-1}" \
  -F consent_for_training=true)
echo "HTTP ${UPLOAD_HTTP}"
cat /tmp/krishi_upload.json | jq . || true
REPORT_ID=$(jq -r '.report_id // empty' /tmp/krishi_upload.json)
echo "report_id=${REPORT_ID:-<empty>}"
echo

echo "5️⃣ Fetch reports (GET ${API}/reports?farmer_id=...)"
curl -sS "${BASE_URL}${API}/reports?farmer_id=${FARMER_ID:-1}" | jq . || true
echo

if [[ -n "${REPORT_ID:-}" ]]; then
  echo "6️⃣ Send feedback (POST ${API}/feedback)"
  curl -sS -X POST "${BASE_URL}${API}/feedback" \
    -H 'Content-Type: application/json' \
    -d "{\"report_id\": ${REPORT_ID}, \"rating\": 5, \"comments\": \"Looks good\"}" | jq . || true
else
  echo "6️⃣ Send feedback skipped (no report_id)"
fi
echo

echo "7️⃣ Optional webhooks (Telegram + WhatsApp)"
curl -sS -o /dev/null -w "telegram_text_http=%{http_code}\n" -X POST "${BASE_URL}${API}/webhooks/telegram" \
  -H 'Content-Type: application/json' \
  -d '{"message":{"text":"hello","chat":{"id":"123"}}}'
curl -sS -o /dev/null -w "whatsapp_text_http=%{http_code}\n" -X POST "${BASE_URL}${API}/webhooks/whatsapp" \
  -H 'Content-Type: application/json' \
  -d '{"From":"+10000000000","Body":"hi"}'
echo

echo "8️⃣ Storage check (local uploads folder)"
if [[ -f uploads/leaf.jpg ]]; then
  echo "uploads/leaf.jpg present"
else
  echo "uploads/leaf.jpg missing (using MinIO or another storage?)"
fi
echo

echo "✅ All tests executed!"