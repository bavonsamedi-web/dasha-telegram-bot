import requests
from flask import Flask, request
import time

from config import *
from persona import SYSTEM_PROMPT
from memory import add_message, get_memory
from scheduler import start_scheduler, update_activity
from state_manager import load_state, save_state
from mood_engine import update_mood
from relationship_engine import update_relationship
from conflict_engine import detect_tone, apply_conflict

app = Flask(__name__)

TELEGRAM_SEND = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
TELEGRAM_ACTION = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendChatAction"


def send_typing(chat_id):
    requests.post(TELEGRAM_ACTION, json={
        "chat_id": chat_id,
        "action": "typing"
    })


def ask_openai(user_message, state):

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "system", "content": f"Current mood: {state['mood']}. Relationship stage: {state['stage']}."}
    ]

    messages += get_memory()
    messages.append({"role": "user", "content": user_message})

    response = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": MODEL,
            "messages": messages,
            "temperature": TEMPERATURE,
            "max_tokens": MAX_TOKENS
        }
    )

    result = response.json()

    if "choices" in result:
        reply = result["choices"][0]["message"]["content"]
        add_message("user", user_message)
        add_message("assistant", reply)
        return reply

    print("OpenAI error:", result)
    return "Я немного задумалась… но я здесь."


@app.route("/", methods=["POST"])
def webhook():
    try:
        data = request.json
        message = data["message"]["text"]
        chat_id = data["message"]["chat"]["id"]

        if chat_id != OWNER_ID:
            return "ignored", 200

        update_activity()

        state = load_state()

        # Проверка охлаждения
        if state["cooldown_until"] > time.time():
            requests.post(TELEGRAM_SEND, json={
                "chat_id": chat_id,
                "text": "Мне нужно немного времени…"
            })
            return "ok", 200

        # Обновляем отношения
        state = update_relationship(state, message)

        # Определяем тон
        tone = detect_tone(message)
        state = apply_conflict(state, tone)

        # Обновляем настроение
        state = update_mood(state)

        send_typing(chat_id)

        reply = ask_openai(message, state)

        requests.post(TELEGRAM_SEND, json={
            "chat_id": chat_id,
            "text": reply
        })

        save_state(state)

        return "ok", 200

    except Exception as e:
        print("Webhook error:", e)
        return "error", 200


@app.route("/", methods=["GET"])
def index():
    return "Dasha Realism Mode Active"


if __name__ == "__main__":
    start_scheduler()
    app.run(host="0.0.0.0", port=3000)
