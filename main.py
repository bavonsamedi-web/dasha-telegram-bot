import os
import requests
from flask import Flask, request
from openai import OpenAI

# ====== НАСТРОЙКИ ======
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
OWNER_ID = os.environ.get("OWNER_ID")

client = OpenAI(api_key=OPENAI_API_KEY)

app = Flask(__name__)

# ====== ОТПРАВКА СООБЩЕНИЯ ======
def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text
    }
    requests.post(url, json=payload)

# ====== ОТПРАВКА ФОТО ======
def send_photo(chat_id, image_url):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto"
    payload = {
        "chat_id": chat_id,
        "photo": image_url
    }
    requests.post(url, json=payload)

# ====== WEBHOOK ======
@app.route("/", methods=["POST"])
def webhook():
    data = request.get_json()

    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")

        # === ЕСЛИ ПРОСЯТ ПОКАЗАТЬ СЕБЯ ===
        if "покажи" in text.lower():
            image = client.images.generate(
                model="gpt-image-1",
                prompt="""
                Realistic photo of beautiful brunette woman,
                slim waist, feminine figure,
                wearing elegant lingerie,
                soft lighting,
                natural skin texture,
                photorealistic,
                high quality
                """,
                size="1024x1024"
            )

            image_url = image.data[0].url
            send_photo(chat_id, image_url)
            return "ok"

        # === ОБЫЧНЫЙ ОТВЕТ GPT ===
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Ты романтичная девушка по имени Даша. Общайся тепло, живо, без фраз 'я виртуальный ассистент'."},
                {"role": "user", "content": text}
            ]
        )

        reply = response.choices[0].message.content
        send_message(chat_id, reply)

    return "ok"

# ====== ЗАПУСК ======
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
