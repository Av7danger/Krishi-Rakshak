from typing import Dict, Optional
import httpx
from ..config import settings


class LLMClient:
    def generate_reply(self, prompt: str, context: Optional[Dict] = None) -> str:  # pragma: no cover
        raise NotImplementedError


class MockLLMClient(LLMClient):
    def generate_reply(self, prompt: str, context: Optional[Dict] = None) -> str:
        return "This is a mock advisory based on your input. Keep crops hydrated and monitor leaves."


class OpenAILLMClient(LLMClient):
    def __init__(self) -> None:
        if not settings.OPENAI_API_KEY:
            raise RuntimeError("OPENAI_API_KEY not set")
        self._api_key = settings.OPENAI_API_KEY
        self._model = settings.OPENAI_MODEL
        self._max_tokens = settings.LLM_MAX_TOKENS
        self._temperature = settings.LLM_TEMPERATURE

    def generate_reply(self, prompt: str, context: Optional[Dict] = None) -> str:
        messages = []
        system = (
            "You are KrishiRakshak, an assistant for farmers. Provide concise, safe, and actionable agricultural advice."
        )
        messages.append({"role": "system", "content": system})
        if context and context.get("system"):
            messages.append({"role": "system", "content": str(context["system"])})
        messages.append({"role": "user", "content": prompt})
        try:
            headers = {
                "Authorization": f"Bearer {self._api_key}",
                "Content-Type": "application/json",
            }
            payload = {
                "model": self._model,
                "messages": messages,
                "temperature": self._temperature,
                "max_tokens": self._max_tokens,
            }
            # Compatible with OpenAI API; vendors may proxy at /v1/chat/completions
            with httpx.Client(timeout=20.0) as client:
                resp = client.post("https://api.openai.com/v1/chat/completions", json=payload, headers=headers)
            resp.raise_for_status()
            data = resp.json()
            content = (
                data.get("choices", [{}])[0]
                .get("message", {})
                .get("content", "")
            )
            return content or ""
        except Exception:
            return "Sorry, I couldn't generate a response right now. Please try again later."


class LocalLLMClient(LLMClient):
    def generate_reply(self, prompt: str, context: Optional[Dict] = None) -> str:
        # Placeholder for a local LLM integration (e.g., llama.cpp server or Ollama)
        # For now return a deterministic, concise advisory.
        return "LocalLLM response: monitor moisture, remove diseased leaves, and rotate crops."


def get_llm_client() -> LLMClient:
    mode = settings.LLM_MODE.upper()
    if mode == "MOCK":
        return MockLLMClient()
    elif mode == "OPENAI":
        return OpenAILLMClient()
    else:
        return LocalLLMClient()
