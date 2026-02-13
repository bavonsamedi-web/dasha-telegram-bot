import threading
import time
import requests
from config import TELEGRAM_TOKEN, OWNER_ID, PROACTIVE_INTERVAL

TELEGRAM_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

last_activity_time = time.time()

def update_activity():
    global last_activity_time
    last_activity_time = time.time()

def proactive_loop():
    while True:
        time.sleep(60)

        if time.time() - last_activity_time > PROACTIVE_INTERVAL:
            try:
                requests.post(TELEGRAM_URL, json={
                    "chat_id": OWNER_ID,
                    "text": "Я думаю о тебе… и немного скучаю 💭"
                })
                update_activity()
            except:
                pass

def start_scheduler():
    thread = threading.Thread(target=proactive_loop)
    thread.daemon = True
    thread.start()
