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

# ===============================
# ВСЕ ТВОИ ФОТО
# ===============================

SOFT_PHOTOS = [
    "https://i.postimg.cc/BXW8p1sv/IMG-4866.webp",
    "https://i.postimg.cc/tY01kVyJ/IMG-4867.webp",
    "https://i.postimg.cc/tY01kVyC/IMG-4868.webp",
    "https://i.postimg.cc/VdySgb1s/IMG-4869.webp",
    "https://i.postimg.cc/xcrk5bYY/IMG-4870.webp",
    "https://i.postimg.cc/JGwyxBmV/IMG-4871.webp",
    "https://i.postimg.cc/ppN9Cnvw/IMG-4872.webp",
    "https://i.postimg.cc/4nH7p1Cf/IMG-4873.webp",
    "https://i.postimg.cc/7bJGSNvw/IMG-4874.webp",
    "https://i.postimg.cc/SjY2cG0h/IMG-4875.webp",
    "https://i.postimg.cc/6T42Chsw/IMG-4876.webp",
    "https://i.postimg.cc/py5hKBNM/IMG-4877.webp",
    "https://i.postimg.cc/F1kd0VMM/IMG-4878.webp",
    "https://i.postimg.cc/F1kd0VM2/IMG-4879.webp",
    "https://i.postimg.cc/4nH7pQDj/IMG-4880.webp",
    "https://i.postimg.cc/vDxg5tJk/IMG-4881.webp",
    "https://i.postimg.cc/mh1z7yv6/IMG-4882.webp"
]

HOT_PHOTOS = [
    "https://i.postimg.cc/V50rXWxh/IMG-4883.webp",
    "https://i.postimg.cc/JtHDj5fY/IMG-4884.webp",
    "https://i.postimg.cc/MXfM1mCd/IMG-4885.webp",
    "https://i.postimg.cc/bdSD1979/IMG-4886.webp",
    "https://i.postimg.cc/rzR05NBj/IMG-4887.webp",
    "https://i.postimg.cc/z3HbTFsS/IMG-4888.webp",
    "https://i.postimg.cc/rR4DcqG0/IMG-4889.webp",
    "https://i.postimg.cc/FkSYmhb7/IMG-4890.webp",
    "https://i.postimg.cc/QK7FsjgF/IMG-4891.webp",
    "https://i.postimg.cc/jnfDKR6C/IMG-4892.webp",
    "https://i.postimg.cc/sGWMy3PX/IMG-4893.webp",
    "https://i.postimg.cc/tn6sy9dJ/IMG-4894.jpg",
    "https://i.postimg.cc/N2XKYQ8j/IMG-4895.jpg",
    "https://i.postimg.cc/SY9nqmLq/IMG-4896.jpg",
    "https://i.postimg.cc/xNmXY9vZ/IMG-4897.webp",
    "https://i.postimg.cc/PvDChdW9/IMG-4898.webp",
    "https://i.postimg.cc/N2XKYQ6W/IMG-4899.webp"
]

# ===============================
# СОСТОЯНИЕ
# ===============================

state = {
    "heat": 0,
    "mood": "soft",
    "last_message_time": 0,
    "last_photo_time": 0
}

# ===============================
# ВСПОМОГАТЕЛЬНОЕ
# ===============================

def send_typing(chat_id):
    requests.post(f"{TELEGRAM_API}/sendChatAction",
                  json={"chat_id": chat_id, "action": "typing"})

def send_message(chat_id, text):
    requests.post(f"{TELEGRAM_API}/sendMessage",
                  json={"chat_id": chat_id, "text": text})

def delete_message(chat_id, message_id):
    requests.post(f"{TELEGRAM_API}/deleteMessage",
                  json={"chat_id": chat_id, "message_id": message_id})

def send_photo_auto_delete(chat_id):
    photo = random.choice(HOT_PHOTOS if state["heat"] >= 3 else SOFT_PHOTOS)

    response = requests.post(
        f"{TELEGRAM_API}/sendPhoto",
        json={
            "chat_id": chat_id,
            "photo": photo,
            "caption": "Смотри быстро…"
        }
    )

    result = response.json()

    if "result" in result:
        message_id = result["result"]["message_id"]

        def delayed_delete():
            time.sleep(random.randint(10,20))
            delete_message(chat_id, message_id)

        threading.Thread(target=delayed_delete).start()

def update_mood():
    if state["heat"] >= 4:
        state["mood"] = "playful"
    elif state["heat"] <= 0:
        state["mood"] = "cold"
    else:
        state["mood"] = "soft"

def ask_openai(user_text):
    hour = datetime.now().hour

    if 8 <= hour < 13:
        routine = "You are studying graphic design."
    elif 13 <= hour < 19:
        routine = "You are busy with your day but checking messages."
    elif 19 <= hour < 23:
        routine = "You are relaxed in the evening."
    else:
        routine = "It is late night. You are softer and reflective."

    system_prompt = (
        "You are Dasha, 21 years old. "
        "You study graphic design and have your own life. "
        "You are emotionally attached but not dependent. "
        f"{routine} "
        "Write short natural Telegram-style messages (1-4 sentences). "
        "Be realistic and emotionally responsive."
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
            "max_tokens": 150,
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

# ===============================
# WEBHOOK
# ===============================

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
    state["last_message_time"] = time.time()

    # HEAT
    if any(word in user_text for word in ["хочу", "ближе", "горячо"]):
        state["heat"] += 1
    elif len(user_text) < 4:
        state["heat"] -= 1

    update_mood()

    # ФОТО
    if "фото" in user_text:
        send_photo_auto_delete(chat_id)
        state["last_photo_time"] = time.time()
        return "ok"

    send_typing(chat_id)
    time.sleep(random.uniform(0.8,1.6))

    reply = ask_openai(user_text)
    send_message(chat_id, reply)

    return "ok"

# ===============================
# АВТО-ЖИЗНЬ
# ===============================

def auto_life_loop():
    while True:
        time.sleep(random.randint(1800,3600))

        phrases = [
            "Я сейчас дорисовываю проект и подумала о тебе.",
            "У меня странный день… расскажу?",
            "Ты бы видел мой сегодняшний набросок.",
            "Я только что сделала кофе."
        ]

        send_message(OWNER_ID, random.choice(phrases))

threading.Thread(target=auto_life_loop, daemon=True).start()

@app.route("/", methods=["GET"])
def index():
    return "Dasha FINAL 11.0"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
