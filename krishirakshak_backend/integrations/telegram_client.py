from ..config import settings


class TelegramClient:
    def __init__(self) -> None:
        self.enabled = settings.TELEGRAM_ENABLED
        self.bot_token = settings.TELEGRAM_BOT_TOKEN

    def send_message(self, chat_id: str, text: str) -> None:
        # Mock: no-op in tests/local
        return
