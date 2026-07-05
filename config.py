import os
from dataclasses import dataclass

from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    telegram_bot_token: str
    openai_api_key: str
    deepseek_api_base: str
    deepseek_model: str
    max_history_messages: int
    max_context_chars: int


def load_settings() -> Settings:
    load_dotenv()

    telegram_bot_token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
    openai_api_key = os.getenv("OPENAI_API_KEY", "").strip()

    missing = []
    if not telegram_bot_token:
        missing.append("TELEGRAM_BOT_TOKEN")
    if not openai_api_key:
        missing.append("OPENAI_API_KEY")
    if missing:
        raise RuntimeError(f"Missing required environment variables: {', '.join(missing)}")

    return Settings(
        telegram_bot_token=telegram_bot_token,
        openai_api_key=openai_api_key,
        deepseek_api_base=os.getenv("DEEPSEEK_API_BASE", "https://api.deepseek.com/v1").rstrip("/"),
        deepseek_model=os.getenv("DEEPSEEK_MODEL", "deepseek-chat"),
        max_history_messages=int(os.getenv("MAX_HISTORY_MESSAGES", "6")),
        max_context_chars=int(os.getenv("MAX_CONTEXT_CHARS", "6000")),
    )
