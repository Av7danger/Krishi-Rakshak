import os
from pathlib import Path
from typing import Tuple
import time
from typing import Dict, Tuple
from .config import settings

ALLOWED_IMAGE_EXTS = {".jpg", ".jpeg", ".png"}


def ensure_upload_dir() -> Path:
    path = Path(settings.LOCAL_UPLOAD_DIR)
    path.mkdir(parents=True, exist_ok=True)
    return path


def validate_image_filename(filename: str) -> Tuple[bool, str]:
    ext = os.path.splitext(filename)[1].lower()
    return (ext in ALLOWED_IMAGE_EXTS, ext)


def validate_upload_mime_and_size(content_type: str, size_bytes: int) -> bool:
    allowed = {m.strip() for m in settings.ALLOWED_IMAGE_MIME.split(",") if m.strip()}
    if content_type not in allowed:
        return False
    if size_bytes > settings.MAX_UPLOAD_MB * 1024 * 1024:
        return False
    return True


# Simple in-memory token bucket per key
_buckets: Dict[str, Tuple[float, float]] = {}


def token_bucket_allow(key: str, rate_per_min: int) -> bool:
    if rate_per_min <= 0:
        return True
    interval = 60.0 / float(rate_per_min)
    now = time.monotonic()
    last_ts, tokens = _buckets.get(key, (now, 1.0))
    # refill
    elapsed = now - last_ts
    tokens = min(tokens + elapsed / interval, float(rate_per_min))
    if tokens >= 1.0:
        tokens -= 1.0
        _buckets[key] = (now, tokens)
        return True
    _buckets[key] = (now, tokens)
    return False
