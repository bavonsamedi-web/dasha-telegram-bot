import os
import requests
from fastapi import FastAPI, Request

app = FastAPI()

BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}"


# -----------------------
# HEALTH CHECK (ОБЯЗАТЕЛЬНО ДЛЯ RAILWAY)
# -----------------------
@app.get("/")
async def root():
    return {"status": "alive"}


# -----------------------
# TELEGRAM WEBHOOK
# -----------------------
@app.post("/webhook")
async def telegram_webhook(request: Request):
    data = await request.json()

    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")

        if text == "/start":
            send_message(chat_id, "Бот запущен 🚀")
        else:
            send_message(chat_id, f"Ты написал: {text}")

    return {"ok": True}


# -----------------------
# SEND MESSAGE FUNCTION
# -----------------------
def send_message(chat_id, text):
    url = f"{TELEGRAM_API}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text
    }
    requests.post(url, json=payload)
