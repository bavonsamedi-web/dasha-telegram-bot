import threading
import time
import requests
from config import *
from state_manager import load_state, save_state
from mood_engine import update_mood

last_activity_time = time.time()


def update_activity():
    global last_activity_time
    last_activity_time = time.time()


def generate_autonomous_message(state):

    mood = state["mood"]
    stage = state["stage"]

    system_prompt = f"""
You are Dasha.

You are writing first.
Current mood: {mood}
Relationship stage: {stage}

Write a natural autonomous message.
Do not ask a question every time.
Sometimes share a thought.
Sometimes tease gently.
Sometimes be warm.
Be intelligent and emotionally nuanced.
"""

    response = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": MODEL,
            "messages": [{"role": "system", "content": system_prompt}],
            "temperature": 0.9,
            "max_tokens": 400
        }
    )

    result = response.json()

    if "choices" in result:
        return result["choices"][0]["message"]["content"]

    return "Иногда тишина заставляет думать…"


def proactive_loop():

    global last_activity_time

    while True:
        time.sleep(60)

        if time.time() - last_activity_time > PROACTIVE_INTERVAL:

            state = load_state()
            state = update_mood(state)

            message = generate_autonomous_message(state)

            requests.post(
                f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
                json={
                    "chat_id": OWNER_ID,
                    "text": message
                }
            )

            state["last_bot_message"] = time.time()
            save_state(state)

            last_activity_time = time.time()


def start_scheduler():
    thread = threading.Thread(target=proactive_loop)
    thread.daemon = True
    thread.start()
