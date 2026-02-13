import requests
from flask import Flask, request
from config import *
from persona import SYSTEM_PROMPT
from memory import add_message, get_memory
from photos import get_random_photo
from scheduler import start_scheduler, update_activity

app = Flask(__name__)

TELEGRAM_SEND = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
TELEGRAM_PHOTO = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto"
TELEGRAM_ACTION = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendChatAction"


def send_typing(chat_id):
    requests.post(TELEGRAM_ACTION, json={
        "chat_id": chat_id,
        "action": "typing"
    })


def ask_openai(user_message):
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages += get_memory()
    messages.append({"role": "user", "content": user_message})

    payload = {
        "model": MODEL,
        "messages": messages,
        "temperature": TEMPERATURE,
        "top_p": TOP_P,
        "max_tokens": MAX_TOKENS
    }

    response = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers=headers,
        json=payload
    )

    result = response.json()

    if "choices" in result:
        reply = result["choices"][0]["message"]["content"]
        add_message("user", user_message)
        add_message("assistant", reply)
        return reply
    else:
        print("OpenAI error:", result)
        return "Сегодня я немного задумалась… но я рядом 💭"


@app.route("/", methods=["POST"])
def webhook():
    try:
        data = request.json
        message = data["message"]["text"]
        chat_id = data["message"]["chat"]["id"]

        if chat_id != OWNER_ID:
            return "ignored", 200

        update_activity()

        if message.lower() == "/photo":
            photo_url = get_random_photo()
            requests.post(TELEGRAM_PHOTO, json={
                "chat_id": chat_id,
                "photo": photo_url,
                "caption": "Это только для тебя… 💕"
            })
            return "ok", 200

        send_typing(chat_id)

        reply = ask_openai(message)

        requests.post(TELEGRAM_SEND, json={
            "chat_id": chat_id,
            "text": reply
        })

        return "ok", 200

    except Exception as e:
        print("Webhook error:", e)
        return "error", 200


@app.route("/", methods=["GET"])
def index():
    return "Dasha is alive"


if __name__ == "__main__":
    start_scheduler()
    app.run(host="0.0.0.0", port=3000)
