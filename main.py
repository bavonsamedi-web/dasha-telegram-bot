import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# Переменные окружения
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

if not TELEGRAM_TOKEN:
    raise RuntimeError("TELEGRAM_TOKEN not set")

TELEGRAM_API = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"


@app.route("/", methods=["GET"])
def health():
    return "Bot is alive", 200


@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        data = request.get_json()

        if not data:
            return jsonify({"status": "no data"}), 200

        if "message" in data:
            chat_id = data["message"]["chat"]["id"]
            text = data["message"].get("text", "")

            send_message(chat_id, f"Ты написал: {text}")

        return jsonify({"status": "ok"}), 200

    except Exception as e:
        print("ERROR:", str(e))
        return jsonify({"error": str(e)}), 200


def send_message(chat_id, text):
    requests.post(
        f"{TELEGRAM_API}/sendMessage",
        json={
            "chat_id": chat_id,
            "text": text
        },
        timeout=10
    )
