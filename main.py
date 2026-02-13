import os
import requests
from flask import Flask, request

app = Flask(__name__)

TOKEN = os.getenv("TELEGRAM_TOKEN")

if not TOKEN:
    raise ValueError("TELEGRAM_TOKEN not found!")

TELEGRAM_API = f"https://api.telegram.org/bot{TOKEN}"

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()

    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")

        if text == "/start":
            send_message(chat_id, "Бот работает 🚀")
        elif text == "/help":
            send_message(chat_id, "Команды:\n/start\n/help")
        else:
            send_message(chat_id, "Я получил: " + text)

    return "ok", 200


def send_message(chat_id, text):
    url = f"{TELEGRAM_API}/sendMessage"
    requests.post(url, json={
        "chat_id": chat_id,
        "text": text
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
