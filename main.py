import os
import requests
from flask import Flask, request

app = Flask(__name__)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

TELEGRAM_API = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"


def send_message(chat_id, text):
    url = f"{TELEGRAM_API}/sendMessage"
    requests.post(url, json={
        "chat_id": chat_id,
        "text": text
    })


@app.route("/", methods=["POST"])
def webhook():
    try:
        data = request.get_json()

        if "message" not in data:
            return "OK", 200

        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")

        send_message(chat_id, f"Ты написал: {text}")

        return "OK", 200

    except Exception as e:
        print("ERROR:", e)
        return "OK", 200


@app.route("/", methods=["GET"])
def home():
    return "Bot is alive", 200


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
