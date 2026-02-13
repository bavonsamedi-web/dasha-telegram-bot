import os

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OWNER_ID = int(os.getenv("OWNER_ID", "0"))

MODEL = "gpt-4o-mini"

MAX_TOKENS = 1200
TEMPERATURE = 0.95
TOP_P = 0.9

PROACTIVE_INTERVAL = 2700  # 45 минут
