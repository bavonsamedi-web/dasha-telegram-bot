import os
import requests
from flask import Flask, request

app = Flask(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = os.getenv("OWNER_ID")

TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}"

@app.route("/")
def index():
    return "Bot is running"

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()

    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")

        if text == "/start":
            send_message(chat_id, "Привет. Я работаю.")
        elif text == "/help":
            send_message(chat_id, "Доступные команды:\n/start\n/help")
        else:
            send_message(chat_id, "Я получил сообщение.")

    return "ok", 200

def send_message(chat_id, text):
    requests.post(
        f"{TELEGRAM_API}/sendMessage",
        json={
            "chat_id": chat_id,
            "text": text
        }
    )
