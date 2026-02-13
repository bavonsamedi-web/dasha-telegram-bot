import os
import requests
from flask import Flask, request

app = Flask(__name__)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not TELEGRAM_TOKEN:
    raise Exception("TELEGRAM_TOKEN not set")

if not OPENAI_API_KEY:
    raise Exception("OPENAI_API_KEY not set")

TELEGRAM_API = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
OPENAI_URL = "https://api.openai.com/v1/chat/completions"


def ask_openai(user_text):
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "gpt-4o-mini",
        "messages": [
            {
                "role": "system",
                "content": "Ты девушка по имени Даша. Ты живая, естественная, умная. Отвечаешь развернуто, логично, без лишних вопросов. Общение теплое, живое."
            },
            {
                "role": "user",
                "content": user_text
            }
        ],
        "temperature": 0.9
    }

    response = requests.post(OPENAI_URL, headers=headers, json=data)

    if response.status_code != 200:
        print("OpenAI error:", response.text)
        return "Секунду… я задумалась."

    return response.json()["choices"][0]["message"]["content"]


@app.route("/", methods=["POST"])
def webhook():
    try:
        data = request.get_json()

        if not data:
            return "ok", 200

        message = data.get("message")

        if not message:
            return "ok", 200

        chat_id = message["chat"]["id"]
        text = message.get("text")

        if not text:
            return "ok", 200

        reply = ask_openai(text)

        requests.post(TELEGRAM_API, json={
            "chat_id": chat_id,
            "text": reply
        })

        return "ok", 200

    except Exception as e:
        print("Webhook error:", e)
        return "ok", 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
