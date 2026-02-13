import requests
from flask import Flask, request
from openai import OpenAI
from config import *
from memory import add_message, get_memory
from state import get_state, update_last_user_time, increase_relationship, decrease_relationship
from personality import build_system_prompt
from image_engine import generate_image
from proactive import start_proactive

app = Flask(__name__)

client = OpenAI(api_key=OPENAI_API_KEY)

TELEGRAM_SEND = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
TELEGRAM_PHOTO = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto"
TELEGRAM_ACTION = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendChatAction"


# ======================
# TELEGRAM HELPERS
# ======================

def send_typing(chat_id):
    requests.post(TELEGRAM_ACTION, json={
        "chat_id": chat_id,
        "action": "typing"
    })


def send_message(chat_id, text):
    requests.post(TELEGRAM_SEND, json={
        "chat_id": chat_id,
        "text": text
    })


def send_photo(chat_id, photo_url):
    requests.post(TELEGRAM_PHOTO, json={
        "chat_id": chat_id,
        "photo": photo_url
    })


# ======================
# AI CHAT
# ======================

def generate_reply(user_text):

    state = get_state()

    system_prompt = build_system_prompt(state)

    messages = [
        {"role": "system", "content": system_prompt}
    ] + get_memory() + [
        {"role": "user", "content": user_text}
    ]

    response = client.chat.completions.create(
        model=MODEL_CHAT,
        messages=messages,
        temperature=TEMPERATURE,
        max_tokens=MAX_TOKENS
    )

    reply = response.choices[0].message.content

    add_message("user", user_text)
    add_message("assistant", reply)

    return reply


# ======================
# WEBHOOK
# ======================

@app.route("/", methods=["POST"])
def webhook():

    data = request.json

    if "message" not in data:
        return "ok"

    message = data["message"]
    chat_id = message["chat"]["id"]

    if chat_id != OWNER_ID:
        return "ok"

    if "text" not in message:
        return "ok"

    user_text = message["text"]

    update_last_user_time()

    # ======================
    # PHOTO DETECTION
    # ======================

    photo_triggers = ["фото", "селфи", "пришли", "покажи", "/photo"]

    if any(trigger in user_text.lower() for trigger in photo_triggers):

        if user_text.startswith("/photo"):
            scene = user_text.replace("/photo", "").strip()
        else:
            scene = user_text

        send_typing(chat_id)

        try:
            image_url = generate_image(scene)
            send_photo(chat_id, image_url)
            increase_relationship(1)
        except Exception as e:
            print("Image error:", e)
            send_message(chat_id, "Я не смогла сейчас сделать фото… попробуй ещё раз.")

        return "ok"

    # ======================
    # EMOTION ANALYSIS
    # ======================

    negative_words = ["игнор", "отстань", "надоела", "бесишь"]

    if any(word in user_text.lower() for word in negative_words):
        decrease_relationship(2)
    else:
        increase_relationship(1)

    # ======================
    # NORMAL CHAT
    # ======================

    send_typing(chat_id)

    reply = generate_reply(user_text)

    send_message(chat_id, reply)

    return "ok"


@app.route("/", methods=["GET"])
def index():
    return "Dasha System Online"


if __name__ == "__main__":
    start_proactive()
    app.run(host="0.0.0.0", port=3000)
