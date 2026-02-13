import os
import requests
from flask import Flask, request

app = Flask(__name__)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# -----------------------
# OpenAI запрос
# -----------------------

def ask_openai(text):

    url = "https://api.openai.com/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {
                "role": "system",
                "content": "Ты девушка по имени Даша. Отвечай живо, естественно, без формальностей."
            },
            {
                "role": "user",
                "content": text
            }
        ]
    }

    r = requests.post(url, headers=headers, json=payload)

    if r.status_code != 200:
        print("OpenAI error:", r.text)
        return "Я задумалась… Напиши еще раз ❤️"

    return r.json()["choices"][0]["message"]["content"]


# -----------------------
# WEBHOOK
# -----------------------

@app.route("/webhook", methods=["POST"])
def webhook():

    data = request.get_json(force=True)

    print("Incoming:", data)

    if "message" not in data:
        return "ok", 200

    chat_id = data["message"]["chat"]["id"]
    text = data["message"].get("text", "")

    if not text:
        return "ok", 200

    answer = ask_openai(text)

    send_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

    requests.post(send_url, json={
        "chat_id": chat_id,
        "text": answer
    })

    return "ok", 200


@app.route("/", methods=["GET"])
def home():
    return "Server is running", 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
