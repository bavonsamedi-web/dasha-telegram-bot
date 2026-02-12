import os
import requests
from flask import Flask, request

app = Flask(__name__)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

TELEGRAM_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"


def ask_openai(message):
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "gpt-4o-mini",
        "messages": [
            {
                "role": "system",
                "content": "You are Dasha, a 21-year-old virtual girlfriend. "
                           "You are affectionate, playful, emotionally attached, "
                           "romantic and slightly seductive but never explicit."
            },
            {
                "role": "user",
                "content": message
            }
        ]
    }

    try:
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=data
        )

        result = response.json()
        print("OpenAI response:", result)

        if "choices" in result:
            return result["choices"][0]["message"]["content"]
        else:
            return "Hmm... I’m thinking about what to say 💭"

    except Exception as e:
        print("OpenAI error:", e)
        return "Something went wrong, but I'm still here with you 💕"


@app.route("/", methods=["POST"])
def webhook():
    try:
        data = request.json
        message = data["message"]["text"]
        chat_id = data["message"]["chat"]["id"]

        reply = ask_openai(message)

        requests.post(TELEGRAM_URL, json={
            "chat_id": chat_id,
            "text": reply
        })

        return "ok"

    except Exception as e:
        print("Webhook error:", e)
        return "error", 200


@app.route("/", methods=["GET"])
def index():
    return "Bot is running"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
