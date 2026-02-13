import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OWNER_ID = os.getenv("OWNER_ID")

if not TELEGRAM_TOKEN:
    raise Exception("TELEGRAM_TOKEN not set!")

def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text
    }
    requests.post(url, json=payload)

@app.route("/")
def home():
    return "Bot is alive", 200

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()

    if not data:
        return jsonify({"status": "no data"}), 200

    message = data.get("message")
    if not message:
        return jsonify({"status": "no message"}), 200

    chat_id = message["chat"]["id"]
    text = message.get("text", "")

    if text == "/start":
        send_message(chat_id, "Бот работает 🚀")
    else:
        send_message(chat_id, f"Ты написал: {text}")

    return jsonify({"status": "ok"}), 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
