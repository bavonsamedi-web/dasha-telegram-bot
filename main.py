import os
import requests
from flask import Flask, request

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

app = Flask(__name__)

# ------------------------
# OpenAI
# ------------------------

def ask_openai(message):
    url = "https://api.openai.com/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "gpt-4o-mini",
        "messages": [
            {
                "role": "system",
                "content": "Ты девушка по имени Даша. Общайся живо, естественно."
            },
            {
                "role": "user",
                "content": message
            }
        ]
    }

    response = requests.post(url, headers=headers, json=data)

    if response.status_code != 200:
        print("OpenAI ERROR:", response.text)
        return "У меня что-то зависло в голове… Попробуй еще раз ❤️"

    return response.json()["choices"][0]["message"]["content"]


# ------------------------
# WEBHOOK
# ------------------------

@app.route("/webhook", methods=["POST"])
def webhook():

    data = request.get_json()

    if not data:
        return "OK", 200

    if "message" not in data:
        return "OK", 200

    chat_id = data["message"]["chat"]["id"]
    text = data["message"].get("text", "")

    answer = ask_openai(text)

    telegram_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

    requests.post(telegram_url, json={
        "chat_id": chat_id,
        "text": answer
    })

    return "OK", 200


@app.route("/", methods=["GET"])
def home():
    return "Bot is running", 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
