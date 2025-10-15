from ..config import settings


class TwilioClient:
    def __init__(self) -> None:
        self.enabled = settings.WHATSAPP_ENABLED
        self.account_sid = settings.TWILIO_ACCOUNT_SID
        self.auth_token = settings.TWILIO_AUTH_TOKEN
        self.from_whatsapp = settings.TWILIO_WHATSAPP_FROM

    def send_whatsapp_message(self, to: str, text: str) -> None:
        # Mock: no-op
        return
