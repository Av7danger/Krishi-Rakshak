from typing import Optional
import base64
import httpx
from ..config import settings


class STTClient:
    def transcribe(self, audio_path: str) -> str:  # pragma: no cover
        raise NotImplementedError


class MockSTT(STTClient):
    def transcribe(self, audio_path: str) -> str:
        return "User asked about leaf blight"


def get_stt_client() -> STTClient:
    mode = settings.STT_MODE.upper()
    if mode == "MOCK":
        return MockSTT()
    if mode == "OPENAI":
        return OpenAIWhisperClient()
    if mode == "GOOGLE":
        return GoogleSTTClient()
    return MockSTT()


class OpenAIWhisperClient(STTClient):
    def __init__(self) -> None:
        if not settings.OPENAI_API_KEY:
            raise RuntimeError("OPENAI_API_KEY not set for STT")
        self._api_key = settings.OPENAI_API_KEY

    def transcribe(self, audio_path: str) -> str:
        try:
            headers = {"Authorization": f"Bearer {self._api_key}"}
            with open(audio_path, "rb") as f:
                files = {"file": (audio_path, f, "application/octet-stream")}
                data = {"model": "whisper-1"}
                with httpx.Client(timeout=60.0) as client:
                    resp = client.post("https://api.openai.com/v1/audio/transcriptions", headers=headers, data=data, files=files)
            resp.raise_for_status()
            j = resp.json()
            return j.get("text", "") or ""
        except Exception:
            return ""


class GoogleSTTClient(STTClient):
    def __init__(self) -> None:
        # Placeholder: expects GOOGLE_STT_API_KEY if implemented
        self._api_key: Optional[str] = None

    def transcribe(self, audio_path: str) -> str:
        # Placeholder implementation: return empty to signal not configured
        return ""
