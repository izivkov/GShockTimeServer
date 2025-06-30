from enum import Enum
from dataclasses import dataclass

class NotificationType(Enum):
    GENERIC = 0
    PHONE_CALL_URGENT = 1
    PHONE_CALL = 2
    EMAIL = 3
    MESSAGE = 4
    CALENDAR = 5
    EMAIL_SMS = 6

@dataclass
class AppNotification:
    
    type: NotificationType
    timestamp: str
    app: str
    title: str
    text: str
    short_text: str = ""

    def __post_init__(self):
        max_length_text = 193
        max_length_short_text = 40
        max_combined = 206  # Example combined max in bytes

        # Truncate individual fields by UTF-8 byte length
        text_bytes = self.text.encode("utf-8")
        if len(text_bytes) > max_length_text:
            self.text = text_bytes[:max_length_text].decode("utf-8", errors="ignore")

        short_text_bytes = self.short_text.encode("utf-8")
        if len(short_text_bytes) > max_length_short_text:
            self.short_text = short_text_bytes[:max_length_short_text].decode("utf-8", errors="ignore")

        # Now check combined UTF-8 byte length
        text_bytes = self.text.encode("utf-8")
        short_text_bytes = self.short_text.encode("utf-8")
        total_len = len(text_bytes) + len(short_text_bytes)
        if total_len > max_combined:
            # Only shorten text, not short_text
            allowed_text_bytes = max(0, max_combined - len(short_text_bytes))
            self.text = text_bytes[:allowed_text_bytes].decode("utf-8", errors="ignore")

    def to_dict(self) -> dict:
        return {
            "type": self.type,
            "timestamp": self.timestamp,
            "app": self.app,
            "title": self.title,
            "text": self.text,
            "short_text": self.short_text,
        }
    
