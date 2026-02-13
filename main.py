from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is alive"

@app.route("/webhook", methods=["POST"])
def webhook():
    return {"ok": True}
