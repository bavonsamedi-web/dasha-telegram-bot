import os
from flask import Flask, request
import requests

app = Flask(__name__)

TOKEN = os.getenv("TELEGRAM_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID"))

def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = {
        "chat_id": chat_id,
        "text": text
    }
    requests.post(url, json=data)

@app.route("/", methods=["POST"])
def webhook():
    try:
        data = request.get_json()

        if not data:
            return "ok", 200

        if "message" in data:
            chat_id = data["message"]["chat"]["id"]
            text = data["message"].get("text", "")

            print("Chat ID:", chat_id)

            if chat_id != OWNER_ID:
                return "ok", 200

            send_message(chat_id, f"Ты написал: {text}")

        return "ok", 200

    except Exception as e:
        print("ERROR:", e)
        return "ok", 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
