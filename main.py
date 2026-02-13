import os
import requests
from flask import Flask, request

app = Flask(__name__)

TOKEN = os.getenv("TELEGRAM_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID"))
OPENAI_KEY = os.getenv("OPENAI_API_KEY")

TELEGRAM_API = f"https://api.telegram.org/bot{TOKEN}"

# ======= TELEGRAM SEND =======
def send_message(chat_id, text):
    requests.post(
        f"{TELEGRAM_API}/sendMessage",
        json={
            "chat_id": chat_id,
            "text": text
        }
    )

# ======= OPENAI =======
def ask_ai(user_text):
    headers = {
        "Authorization": f"Bearer {OPENAI_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "gpt-4o-mini",
        "messages": [
            {
                "role": "system",
                "content": "You are Dasha. You are warm, alive, feminine, playful. You speak naturally and emotionally."
            },
            {
                "role": "user",
                "content": user_text
            }
        ]
    }

    r = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers=headers,
        json=data
    )

    return r.json()["choices"][0]["message"]["content"]

# ======= WEBHOOK =======
@app.route("/", methods=["POST"])
def webhook():
    try:
        data = request.json

        if "message" not in data:
            return "OK", 200

        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")

        if chat_id != OWNER_ID:
            return "OK", 200

        reply = ask_ai(text)
        send_message(chat_id, reply)

        return "OK", 200

    except Exception as e:
        print("ERROR:", e)
        return "OK", 200

# ======= START =======
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
