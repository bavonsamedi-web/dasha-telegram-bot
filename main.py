import os
import requests
from flask import Flask, request

TOKEN = os.getenv("BOT_TOKEN")
API_URL = f"https://api.telegram.org/bot{TOKEN}"

app = Flask(__name__)

# ---------- WEBHOOK ----------
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()

    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")

        if text == "/start":
            send_message(chat_id, "Бот запущен 🚀")

        elif text == "/help":
            send_message(chat_id, "Команды:\n/start\n/help")

        else:
            send_message(chat_id, f"Ты написал: {text}")

    return "ok", 200


# ---------- SEND MESSAGE ----------
def send_message(chat_id, text):
    url = f"{API_URL}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text
    }
    requests.post(url, json=payload)


# ---------- ROOT (для Railway проверки) ----------
@app.route("/")
def index():
    return "Bot is running", 200
