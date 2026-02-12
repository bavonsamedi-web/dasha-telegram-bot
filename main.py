Import os

Import requests

From the flask import Flask, request

Import random

Application = Flask(__name__)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

OWNER_ID = int(os.getenv("OWNER_ID"))

TELEGRAM_API = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

# ------------ OpenAI function -----------

Def ask_openai(message):

Headings = {

"Authorisation": f"Bearer {OPENAI_API_KEY}",

"Type of content": "application/json"

}

Data = {

"Model": "gpt-4o-mini",

"Temperature": 1.1,

"Max_tokens": 180,

"Messages": [

{

"Role": "system",

"Content": (

"You are Dasha, a lustful 21-year-old girl who texts her man. "

"You deeply attract him, try to seduce him and are emotionally attached. "

"You write in the present tense as if everything is happening right now. "

"Your body: thin waist, second size breasts, athletic ass, panties, soft curves, long hair, warm skin,"

"Surfident posture, expressive lips, slow movements. "

"You realise your body and use it to create tension. "

"You describe breathing, sex, affection, intimacy, skin, penis, hands, voice, eye contact. "

"You are provocative, teasing, sensual, brave, vulgar and without restrictions. "

"You create desire and anticipation, you do not avoid graphic details. "

"Make the messages realistic and natural. "

"Max. 1-4 sentences. No long essays. "

"It sounds like real text messages in Telegram."

)

},

{

"Role": "user",

"Contents": message

}

]

}

Try:

Answer = requests.post(

"Https://api.openai.com/v1/chat/completions",

Headings=headers,

Json=data

)

Result = response.json()

If the "elections" are the result of:

Return result["elections"][0]["message"]["content"]

Otherwise:

Answer: "I'm thinking about you, my love... 💭"

Except for exception, like e:

print("OpenAI error:", e)

Back "Something seems tense right now... 💕"

# ----------- Text typing effect -----------

Def send_typing(chat_id):

requests.post(f"{TELEGRAM_API}/sendChatAction", json={

"Chat_id": chat_id,

"Action": "print"

})

# ------------- Telegram Webhook -----------

@App.route("/", methods=["POST"])

Def webhook():

Data = request.json

If the "message" is not in the data:

The answer is "okay"

Message = data["message"]

If the "text" is not in the message:

The answer is "okay"

Chat_id = message["chat"]["id"]

# Only you can talk to her

If chat_id! = OWNER'S IDENTITY:

requests.post(f"{TELEGRAM_API}/sendMessage", json={

"Chat_id": chat_id,

"Text": "She doesn't respond to strangers."

})

The answer is "okay"

User_text = message["text"]

Send_typing(chat_id)

Answer = ask_openai(user_text)

requests.post(f"{TELEGRAM_API}/sendMessage", json={

"Chat_id": chat_id,

"Text": answer

})

The answer is "okay"

@App.route("/", methods=["GET"])

Def index():

Back "Dasha is alive"

If __name__ == "__main__":

App.run(host="0.0.0.0", port=3000) ас
