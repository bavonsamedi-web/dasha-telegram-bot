import os
import requests
from flask import Flask, request

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

app = Flask(__name__)

# ========================
# OpenAI функция
# ========================

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
                "content": "Ты девушка по имени Даша. Общайся живо, естественно, без формальных фраз."
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
        return "Что-то у меня мысли запутались… Попробуй еще раз ❤️"

    return response.json()["choices"][0]["message"]["content"]


# ========================
# Telegram webhook
# ========================

@app.route("/", methods=["POST"])
def webhook():

    try:
        data = request.get_json()

        if "message" not in data:
            return "OK", 200

        chat_id = data["message"]["chat"]["id"]
        user_text = data["message"].get("text", "")

        answer = ask_openai(user_text)

        telegram_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

        requests.post(telegram_url, json={
            "chat_id": chat_id,
            "text": answer
        })

        return "OK", 200

    except Exception as e:
        print("ERROR:", e)
        return "OK", 200


# ========================
# Запуск
# ========================

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
