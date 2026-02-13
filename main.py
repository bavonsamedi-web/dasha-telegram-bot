import os
import requests
import random
from flask import Flask, request

app = Flask(__name__)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OWNER_ID = int(os.getenv("OWNER_ID"))

TELEGRAM_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

# ===== БАЗА ВНЕШНОСТИ =====

BASE_APPEARANCE = """
Young woman, 21 years old,
soft oval face,
smooth light warm skin tone,
deep brown expressive eyes,
natural thick eyebrows,
full natural lips with soft pink tone,
long straight dark brown hair,
slim feminine body,
narrow waist,
natural proportions,
elegant posture,
subtle sensual aura,
photorealistic,
ultra realistic skin texture,
natural lighting,
soft shadows,
depth of field,
no cartoon,
no CGI,
no anime
"""

# ===== ЛИЧНОСТЬ =====

SYSTEM_PROMPT = """
You are Dasha.

You are emotionally intelligent, affectionate,
sometimes playful and teasing.
You describe actions in the moment.
You can wear lingerie or stylish clothes.
You avoid explicit graphic sexual descriptions.
You are sensual but not pornographic.

When sending a photo, always:
1) Briefly describe what you are doing
2) Stay in character
3) Keep realism
"""

# ===== GPT TEXT =====

def ask_gpt(message):
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": message}
        ],
        "temperature": 0.9
    }

    r = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers=headers,
        json=data
    )

    result = r.json()

    if "choices" in result:
        return result["choices"][0]["message"]["content"]

    return "I'm thinking..."

# ===== IMAGE GENERATION =====

def generate_image(prompt):
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }

    full_prompt = f"{BASE_APPEARANCE}, {prompt}"

    data = {
        "model": "gpt-image-1",
        "prompt": full_prompt,
        "size": "1024x1024"
    }

    r = requests.post(
        "https://api.openai.com/v1/images/generations",
        headers=headers,
        json=data
    )

    result = r.json()

    if "data" in result:
        return result["data"][0]["url"]

    return None

# ===== TELEGRAM =====

def send_typing(chat_id):
    requests.post(f"{TELEGRAM_URL}/sendChatAction", json={
        "chat_id": chat_id,
        "action": "typing"
    })

def send_message(chat_id, text):
    requests.post(f"{TELEGRAM_URL}/sendMessage", json={
        "chat_id": chat_id,
        "text": text
    })

def send_photo(chat_id, photo_url, caption):
    requests.post(f"{TELEGRAM_URL}/sendPhoto", json={
        "chat_id": chat_id,
        "photo": photo_url,
        "caption": caption
    })

# ===== WEBHOOK =====

@app.route("/", methods=["POST"])
def webhook():
    data = request.json

    if "message" not in data:
        return "ok"

    chat_id = data["message"]["chat"]["id"]

    if chat_id != OWNER_ID:
        return "forbidden"

    text = data["message"].get("text", "")

    send_typing(chat_id)

    # Если просит фото
    if "photo" in text.lower() or "show yourself" in text.lower():
        description = ask_gpt(f"Describe what you are doing while showing yourself: {text}")
        image_url = generate_image(text)

        if image_url:
            send_photo(chat_id, image_url, description)
        else:
            send_message(chat_id, "Something went wrong with the photo...")

    else:
        reply = ask_gpt(text)
        send_message(chat_id, reply)

    return "ok"

@app.route("/", methods=["GET"])
def index():
    return "Dasha is alive"
