from typing import Optional


class TTSClient:
    def synthesize(self, text: str) -> Optional[bytes]:  # pragma: no cover
        raise NotImplementedError


class MockTTSClient(TTSClient):
    def synthesize(self, text: str) -> Optional[bytes]:
        # Return a tiny WAV header with no audio for tests/local flows
        # RIFF header for PCM with zero data
        return (
            b"RIFF" + (36).to_bytes(4, "little") + b"WAVEfmt " + (16).to_bytes(4, "little") + (1).to_bytes(2, "little")
            + (1).to_bytes(2, "little") + (8000).to_bytes(4, "little") + (8000 * 2).to_bytes(4, "little")
            + (2).to_bytes(2, "little") + (16).to_bytes(2, "little") + b"data" + (0).to_bytes(4, "little")
        )


def get_tts_client() -> TTSClient:
    # For now, always return Mock; can be extended to LOCAL/CLOUD later
    return MockTTSClient()


