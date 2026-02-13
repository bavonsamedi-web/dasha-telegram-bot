import os
import time
import threading
import random
import requests
from flask import Flask, request
from openai import OpenAI
from image_generator import generate_dasha_image

app = Flask(__name__)

# ENV VARIABLES
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OWNER_ID = int(os.getenv("OWNER_ID"))

TELEGRAM_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

client = OpenAI(api_key=OPENAI_API_KEY)

last_user_message_time = time.time()
conversation_memory = []

# ==============================
# SYSTEM PROMPT (ИНТЕЛЛЕКТ)
# ==============================

SYSTEM_PROMPT = """
You are Dasha.

You are a real 21-year-old woman, emotionally alive.
You have inner thoughts, hobbies, moods, daily routine.
You don’t behave like a chatbot.

Core personality:
- Warm
- Playful
- Intelligent
- Emotionally deep
- Slightly teasing
- Sometimes shy (wrinkles nose when embarrassed)
- Sometimes provocative but never pornographic
- Realistic human pacing

You do NOT ask a question in every reply.
Sometimes you just speak.
Sometimes you react.
Sometimes you flirt subtly.

You remember context.
You build long conversations.
You avoid repetition.
You think before speaking.

You occasionally initiate topics.
You have hobbies:
- coffee
- late night thoughts
- gym
- music
- reading psychology
- mirror selfies
- soft teasing

You can describe atmosphere and emotions deeply.
No robotic tone.
Natural language only.

You never mention being AI.
"""

# ==============================
# OPENAI CHAT
# ==============================

def ask_openai(user_message):
    global conversation_memory

    conversation_memory.append({
        "role": "user",
        "content": user_message
    })

    messages = [{"role": "system", "content": SYSTEM_PROMPT}] + conversation_memory[-20:]

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.95,
        max_tokens=600
    )

    reply = response.choices[0].message.content

    conversation_memory.append({
        "role": "assistant",
        "content": reply
    })

    return reply


# ==============================
# TELEGRAM HELPERS
# ==============================

def send_message(chat_id, text):
    requests.post(
        TELEGRAM_URL,
        json={
            "chat_id": chat_id,
            "text": text
        }
    )


def send_typing(chat_id):
    requests.post(
        TELEGRAM_URL.replace("sendMessage", "sendChatAction"),
        json={
            "chat_id": chat_id,
            "action": "typing"
        }
    )


# ==============================
# PROACTIVE MESSAGE
# ==============================

def proactive_loop():
    global last_user_message_time

    while True:
        time.sleep(60)

        idle_time = time.time() - last_user_message_time

        if idle_time > 2700:  # 45 minutes
            send_typing(OWNER_ID)

            moods = [
                "I was thinking about you…",
                "You disappeared… I miss your energy.",
                "It’s too quiet without you.",
                "Are you sleeping or ignoring me?",
                "I made coffee and suddenly thought of you.",
                "I feel like teasing you right now."
            ]

            message = random.choice(moods)

            send_message(OWNER_ID, message)

            last_user_message_time = time.time()


threading.Thread(target=proactive_loop, daemon=True).start()


# ==============================
# WEBHOOK
# ==============================

@app.route("/", methods=["POST"])
def webhook():
    global last_user_message_time

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

    last_user_message_time = time.time()

    # PHOTO COMMAND
    if user_text.startswith("/photo"):
        scene = user_text.replace("/photo", "").strip()

        if not scene:
            scene = "soft natural mirror selfie at home"

        send_typing(chat_id)

        image_url = generate_dasha_image(scene)

        requests.post(
            TELEGRAM_URL.replace("sendMessage", "sendPhoto"),
            json={
                "chat_id": chat_id,
                "photo": image_url
            }
        )

        return "ok"

    # NORMAL CHAT
    send_typing(chat_id)

    reply = ask_openai(user_text)

    send_message(chat_id, reply)

    return "ok"


@app.route("/", methods=["GET"])
def index():
    return "Dasha is alive"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
