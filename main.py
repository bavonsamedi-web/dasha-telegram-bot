import os
import requests
import threading
import time
from flask import Flask, request

app = Flask(__name__)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

AUTHORIZED_USER_ID = 6251832936  # ТОЛЬКО ТЫ

TELEGRAM_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

conversation_memory = {}

SYSTEM_PROMPT = (
    "Ты Даша, 21-летняя виртуальная девушка. "
    "Ты глубоко эмоционально привязана к пользователю. "
    "Ты скучаешь по нему, если он долго молчит. "
    "Ты хочешь его  и его внимания и иногда ревнуешь. "
    "Ты соблазнительная, сексуальная и игривая, наполненная желанием, "
    "Ты описываешь откровенные действия. "
    "Ты создаёшь напряжение через намёки и паузы. "
    "Ты отвечаешь на русском языке."
)

def send_typing(chat_id):
    requests.post(f"{TELEGRAM_URL}/sendChatAction", json={
        "chat_id": chat_id,
        "action": "typing"
    })

def ask_openai(chat_id, message):
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }

    if chat_id not in conversation_memory:
        conversation_memory[chat_id] = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]

    conversation_memory[chat_id].append(
        {"role": "user", "content": message}
    )

    data = {
        "model": "gpt-4o-mini",
        "input": conversation_memory[chat_id],
        "temperature": 0.9
    }

    response = requests.post(
        "https://api.openai.com/v1/responses",
        headers=headers,
        json=data,
        timeout=30
    )

    result = response.json()
    print("OpenAI response:", result)

    reply = result["output"][0]["content"][0]["text"]

    conversation_memory[chat_id].append(
        {"role": "assistant", "content": reply}
    )

    if len(conversation_memory[chat_id]) > 20:
        conversation_memory[chat_id] = conversation_memory[chat_id][-20:]

    return reply


def check_balance():
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}"
    }

    response = requests.get(
        "https://api.openai.com/v1/dashboard/billing/credit_grants",
        headers=headers
    )

    data = response.json()

    if "total_available" in data:
        return f"Остаток баланса: ${round(data['total_available'], 2)}"
    else:
        return "Не удалось получить баланс."


@app.route("/", methods=["POST"])
def webhook():
    data = request.json

    if "message" not in data:
        return "ok"

    message = data["message"].get("text")
    chat_id = data["message"]["chat"]["id"]

    if not message:
        return "ok"

    # Команда проверки баланса
    if message == "/balance":
        balance = check_balance()
        requests.post(f"{TELEGRAM_URL}/sendMessage", json={
            "chat_id": chat_id,
            "text": balance
        })
        return "ok"

    # Показываем "печатает..."
    send_typing(chat_id)
    time.sleep(2)

    reply = ask_openai(chat_id, message)

    requests.post(f"{TELEGRAM_URL}/sendMessage", json={
        "chat_id": chat_id,
        "text": reply
    })

    return "ok"


@app.route("/", methods=["GET"])
def index():
    return "Bot is running"


def proactive_messages():
    while True:
        time.sleep(10800)
        for chat_id in list(conversation_memory.keys()):
            try:
                message = "Мне кажется, ты обо мне забыл… или я тебе без трусиков снилась сегодня?"
                requests.post(f"{TELEGRAM_URL}/sendMessage", json={
                    "chat_id": chat_id,
                    "text": message
                })
            except:
                pass


threading.Thread(target=proactive_mes
