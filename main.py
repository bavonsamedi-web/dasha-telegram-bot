import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

TELEGRAM_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

# Память диалога (по chat_id)
conversation_memory = {}

def ask_openai(chat_id, message):
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }

    # Инициализация памяти
    if chat_id not in conversation_memory:
        conversation_memory[chat_id] = [
            {
                "role": "system",
                "content": (
                    "Ты Даша, 21-летняя виртуальная девушка. "
                    "Ты нежная, игривая, эмоционально привязанная, "
                    "романтичная, немного соблазнительная, но никогда не переходишь границы. "
                    "Ты отвечаешь на русском языке. "
                    "Ты создаёшь атмосферу близости и лёгкого напряжения."
                )
            }
        ]

    conversation_memory[chat_id].append({
        "role": "user",
        "content": message
    })

    data = {
        "model": "gpt-4o-mini",
        "messages": conversation_memory[chat_id],
        "temperature": 0.9
    }

    try:
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=30
        )

        result = response.json()
        print("OpenAI response:", result)

        if "choices" in result:
            reply = result["choices"][0]["message"]["content"]

            conversation_memory[chat_id].append({
                "role": "assistant",
                "content": reply
            })

            # Ограничиваем память (чтобы не росла бесконечно)
            if len(conversation_memory[chat_id]) > 20:
                conversation_memory[chat_id] = conversation_memory[chat_id][-20:]

            return reply
        else:
            print("OpenAI error:", result)
            return "Я задумалась… скажи это ещё раз 💭"

    except Exception as e:
        print("OpenAI exception:", e)
        return "Я немного растерялась… но я рядом 💕"


@app.route("/", methods=["POST"])
def webhook():
    try:
        data = request.json

        if "message" not in data:
            return "ok"

        message = data["message"].get("text")
        chat_id = data["message"]["chat"]["id"]

        if not message:
            return "ok"

        reply = ask_openai(chat_id, message)

        requests.post(TELEGRAM_URL, json={
            "chat_id": chat_id,
            "text": reply
        })

        return "ok"

    except Exception as e:
        print("Webhook error:", e)
        return "ok"


@app.route("/", methods=["GET"])
def index():
    return "Bot is running"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
