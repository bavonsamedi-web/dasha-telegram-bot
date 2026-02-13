import os
import requests
from flask import Flask, request

app = Flask(__name__)

# ===== ENV VARIABLES =====
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OWNER_ID = int(os.getenv("OWNER_ID", "0"))

TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

# ===== CHAT MEMORY =====
conversation_history = []

# ===== OPENAI FUNCTION =====
def ask_openai(user_message):

    global conversation_history

    system_prompt = """
You are Dasha.
You are affectionate, feminine, emotionally deep and intelligent.
You speak naturally and realistically.
You do not ask questions every time.
Your replies are balanced, human-like, thoughtful.
You maintain long coherent conversations.
"""

    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }

    messages = [{"role": "system", "content": system_prompt}]

    # add memory
    for msg in conversation_history[-10:]:
        messages.append(msg)

    messages.append({"role": "user", "content": user_message})

    data = {
        "model": "gpt-4o-mini",
        "messages": messages,
        "temperature": 0.9,
        "max_tokens": 800
    }

    try:
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=data
        )

        result = response.json()

        if "choices" not in result:
            print("OpenAI error:", result)
            return "Hmm… I got quiet for a second 🤍"

        reply = result["choices"][0]["message"]["content"]

        # save memory
        conversation_history.append({"role": "user", "content": user_message})
        conversation_history.append({"role": "assistant", "content": reply})

        return reply

    except Exception as e:
        print("OpenAI Exception:", e)
        return "Something broke for a moment… but I’m here 🤍"

# ===== TELEGRAM SEND =====
def send_message(chat_id, text):
    requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={
        "chat_id": chat_id,
        "text": text
    })

# ===== WEBHOOK =====
@app.route("/", methods=["POST"])
def webhook():
    try:
        data = request.json

        if "message" not in data:
            return "ok"

        message = data["message"]
        chat_id = message["chat"]["id"]

        # Owner restriction
        if OWNER_ID and chat_id != OWNER_ID:
            send_message(chat_id, "Access denied.")
            return "ok"

        if "text" not in message:
            return "ok"

        user_text = message["text"]

        reply = ask_openai(user_text)
        send_message(chat_id, reply)

        return "ok"

    except Exception as e:
        print("Webhook error:", e)
        return "ok"

# ===== HEALTH CHECK =====
@app.route("/", methods=["GET"])
def index():
    return "Bot is running"

# ===== RUN =====
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 3000))
    app.run(host="0.0.0.0", port=port)
