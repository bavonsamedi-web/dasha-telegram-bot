import time
import threading
import random
import requests
from config import TELEGRAM_TOKEN, OWNER_ID, PROACTIVE_INTERVAL
from state import get_state

TELEGRAM_API = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

def start_proactive():

    def loop():
        while True:
            time.sleep(60)
            state = get_state()
            idle = time.time() - state["last_user_message_time"]

            if idle > PROACTIVE_INTERVAL:
                messages = [
                    "Я подумала о тебе…",
                    "Тут тихо без тебя.",
                    "Мне захотелось написать тебе первой.",
                    "Иногда я скучаю немного…"
                ]

                requests.post(
                    TELEGRAM_API,
                    json={
                        "chat_id": OWNER_ID,
                        "text": random.choice(messages)
                    }
                )

                state["last_bot_message_time"] = time.time()
                state["last_user_message_time"] = time.time()

    thread = threading.Thread(target=loop)
    thread.daemon = True
    thread.start()
