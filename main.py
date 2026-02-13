import os
from flask import Flask, request
import requests

app = Flask(__name__)

TOKEN = os.environ.get("TELEGRAM_TOKEN")
OWNER_ID = int(os.environ.get("OWNER_ID"))

def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, json={
        "chat_id": chat_id,
        "text": text
    })

@app.route("/", methods=["GET"])
def home():
    return "Bot is alive", 200

@app.route("/", methods=["POST"])
def webhook():
    try:
        update = request.get_json()
        print("UPDATE:", update)

        if "message" in update:
            chat_id = update["message"]["chat"]["id"]
            text = update["message"].get("text", "")

            if chat_id == OWNER_ID:
                send_message(chat_id, f"Получила: {text}")

        return "ok", 200

    except Exception as e:
        print("ERROR:", e)
        return "ok", 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 3000))
    app.run(host="0.0.0.0", port=port)
