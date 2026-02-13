import os
import requests
from flask import Flask, request

# ====== CONFIG ======
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OWNER_ID = int(os.getenv("OWNER_ID"))

TELEGRAM_API = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"
OPENAI_API = "https://api.openai.com/v1/chat/completions"

app = Flask(__name__)

# ====== HELPER ======
def send_message(chat_id, text):
    requests.post(f"{TELEGRAM_API}/sendMessage", json={
        "chat_id": chat_id,
        "text": text
    })

def generate_reply(user_text):
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "gpt-4o-mini",
        "messages": [
            {
                "role": "system",
                "content": "You are Dasha. You are feminine, intelligent, emotional, romantic. You respond naturally and realistically. Not robotic. Medium length answers."
            },
            {
                "role": "user",
                "content": user_text
            }
        ],
        "temperature": 0.9
    }

    response = requests.post(OPENAI_API, headers=headers, json=data)
    result = response.json()

    if "choices" in result:
        return result["choices"][0]["message"]["content"]
    else:
        return "I’m thinking… 💭"

# ====== WEBHOOK ======
@app.route("/", methods=["POST"])
def webhook():
    data = request.json

    if "message" not in data:
        return "ok"

    chat_id = data["message"]["chat"]["id"]
    text = data["message"].get("text", "")

    if chat_id != OWNER_ID:
        send_message(chat_id, "I only talk to my owner.")
        return "ok"

    reply = generate_reply(text)
    send_message(chat_id, reply)

    return "ok"

# ====== HEALTH CHECK ======
@app.route("/", methods=["GET"])
def home():
    return "Bot is running"
    
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
