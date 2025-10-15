from krishirakshak_backend.llm.manager import get_llm_client
from krishirakshak_backend.stt.manager import get_stt_client
from krishirakshak_backend.config import settings


def test_mock_llm_and_stt():
    settings.LLM_MODE = "MOCK"
    settings.STT_MODE = "MOCK"
    llm = get_llm_client()
    stt = get_stt_client()
    assert "mock".lower() in llm.generate_reply("hi").lower()
    assert "leaf blight" in stt.transcribe("/tmp/audio.wav")
