import os

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OWNER_ID = int(os.getenv("OWNER_ID", "0"))

MODEL_CHAT = "gpt-4o-mini"
MODEL_IMAGE = "gpt-image-1"

TEMPERATURE = 0.9
MAX_TOKENS = 800

PROACTIVE_INTERVAL = 2700  # 45 минут
