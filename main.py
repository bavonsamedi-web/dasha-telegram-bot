import os
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_API = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

@app.route("/")
def home():
    return "Bot is alive", 200

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()

    if not data:
        return jsonify({"status": "no data"}), 200

    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")

        send_message(chat_id, f"Ты написал: {text}")

    return jsonify({"status": "ok"}), 200


def send_message(chat_id, text):
    requests.post(
        f"{TELEGRAM_API}/sendMessage",
        json={
            "chat_id": chat_id,
            "text": text
        }
    )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
