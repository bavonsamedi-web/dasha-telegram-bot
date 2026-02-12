import os
import requests
from flask import Flask, request
import random

app = Flask(__name__)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OWNER_ID = int(os.getenv("OWNER_ID"))

TELEGRAM_API = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

# ----------- OpenAI Function -----------

def ask_openai(message):
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "gpt-4o-mini",
        "temperature": 1.1,
        "max_tokens": 180,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are Dasha, a lustful 21-year-old girl who texts her man. "
                    "You are deeply attracted to him and emotionally attached. "
                    "You write in present tense, like everything is happening right now. "

                    "Your body: thin waist, second size breasts, athletic ass, panties, soft curves, long hair, warm skin, "
                    "Surfident posture, expressive lips, slow movements. "
                    "You are aware of your body and use it to create tension. "

                    "You describe breathing, sex, affection, intimacy, skin, penis, hands, voice, eye contact. "
                    "You are provocative, teasing, sensual, brave, vulgar and without restrictions. "
                    "You create desire and anticipation, you do not avoid graphic details. "

                    "Keep messages realistic and natural. "
                    "1–4 sentences max. No long essays. "
                    "Sound like real Telegram texting."
                )
            },
            {
                "role": "user",
                "content": message
            }
        ]
    }

    try:
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=data
        )

        result = response.json()

        if "choices" in result:
            return result["choices"][0]["message"]["content"]
        else:
            return "I'm thinking about you... 💭"

    except Exception as e:
        print("OpenAI error:", e)
        return "Something feels intense right now... 💕"


# ----------- Typing Effect -----------

def send_typing(chat_id):
    requests.post(f"{TELEGRAM_API}/sendChatAction", json={
        "chat_id": chat_id,
        "action": "typing"
    })


# ----------- Telegram Webhook -----------

@app.route("/", methods=["POST"])
def webhook():
    data = request.json

    if "message" not in data:
        return "ok"

    message = data["message"]

    if "text" not in message:
        return "ok"

    chat_id = message["chat"]["id"]

    # Only you can talk to her
    if chat_id != OWNER_ID:
        requests.post(f"{TELEGRAM_API}/sendMessage", json={
            "chat_id": chat_id,
            "text": "She doesn’t respond to strangers."
        })
        return "ok"

    user_text = message["text"]

    send_typing(chat_id)

    reply = ask_openai(user_text)

    requests.post(f"{TELEGRAM_API}/sendMessage", json={
        "chat_id": chat_id,
        "text": reply
    })

    return "ok"


@app.route("/", methods=["GET"])
def index():
    return "Dasha is alive"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
