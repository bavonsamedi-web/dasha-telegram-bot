import os
import requests
import random
import time
import threading
from flask import Flask, request
from datetime import datetime

app = Flask(__name__)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OWNER_ID = int(os.getenv("OWNER_ID", "0"))

TELEGRAM_API = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

SOFT_PHOTOS = [
    "https://i.postimg.cc/BXW8p1sv/IMG-4866.webp",
    "https://i.postimg.cc/tY01kVyJ/IMG-4867.webp"
]

HOT_PHOTOS = [
    "https://i.postimg.cc/V50rXWxh/IMG-4883.webp",
    "https://i.postimg.cc/JtHDj5fY/IMG-4884.webp"
]

state = {
    "heat": 0,
    "mood": "soft",
    "last_message": 0,
    "last_photo": 0
}

def is_night():
    h = datetime.now().hour
    return h >= 23 or h <= 5

def update_mood():
    if state["heat"] >= 4:
        state["mood"] = "playful"
    elif state["heat"] <= 0:
        state["mood"] = "cold"
    else:
        state["mood"] = "soft"

def send_message(chat_id, text):
    requests.post(f"{TELEGRAM_API}/sendMessage",
                  json={"chat_id": chat_id, "text": text})

def send_photo(chat_id):
    photo = random.choice(HOT_PHOTOS if state["heat"] >= 3 else SOFT_PHOTOS)
    requests.post(f"{TELEGRAM_API}/sendPhoto",
                  json={"chat_id": chat_id, "photo": photo})

def generate_voice(text):
    response = requests.post(
        "https://api.openai.com/v1/audio/speech",
        headers={"Authorization": f"Bearer {OPENAI_API_KEY}"},
        json={
            "model": "gpt-4o-mini-tts",
            "voice": "alloy",
            "input": text
        }
    )
    if response.status_code == 200:
        with open("voice.mp3", "wb") as f:
            f.write(response.content)
        return "voice.mp3"
    return None

def maybe_send_voice(chat_id, text):
    chance = 30

    if state["heat"] >= 3:
        chance = 60
    if state["mood"] == "cold":
        chance = 10

    roll = random.randint(1, 100)

    if roll <= chance:
        if state["mood"] == "playful":
            text = text + " …*тихий смешок*"

        voice_file = generate_voice(text)
        if voice_file:
            with open(voice_file, "rb") as audio:
                requests.post(
                    f"{TELEGRAM_API}/sendVoice",
                    files={"voice": audio},
                    data={"chat_id": chat_id}
                )

def ask_openai(user_text):
    system_prompt = (
        "You are Dasha. Write short Telegram-style messages. "
        "Be emotionally responsive and realistic. "
        "Avoid long essays."
    )

    response = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": "gpt-4o-mini",
            "temperature": 1.0,
            "max_tokens": 120,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_text}
            ]
        }
    )

    result = response.json()
    if "choices" in result:
        return result["choices"][0]["message"]["content"]
    return "..."

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

    user_text = message["text"].lower()
    state["last_message"] = time.time()

    if any(word in user_text for word in ["хочу", "ближе", "горячо"]):
        state["heat"] += 1
    elif len(user_text) < 4:
        state["heat"] -= 1

    update_mood()

    if "фото" in user_text:
        send_photo(chat_id)
        state["last_photo"] = time.time()
        return "ok"

    reply = ask_openai(user_text)
    send_message(chat_id, reply)
    maybe_send_voice(chat_id, reply)

    return "ok"

@app.route("/", methods=["GET"])
def index():
    return "Dasha 7.0 Random Voice Active"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
