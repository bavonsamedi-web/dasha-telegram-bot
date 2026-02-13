import os
from fastapi import FastAPI, Request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from openai import OpenAI

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OWNER_ID = int(os.getenv("OWNER_ID"))

client = OpenAI(api_key=OPENAI_API_KEY)

app = FastAPI()
telegram_app = Application.builder().token(BOT_TOKEN).build()

memory = {}

async def start(update: Update, context):
    if update.effective_user.id != OWNER_ID:
        return
    await update.message.reply_text("Я готов, хозяин.")

async def reset(update: Update, context):
    if update.effective_user.id != OWNER_ID:
        return
    memory.clear()
    await update.message.reply_text("Память очищена.")

async def photo(update: Update, context):
    if update.effective_user.id != OWNER_ID:
        return
    
    prompt = update.message.text.replace("/photo", "").strip()
    if not prompt:
        await update.message.reply_text("Напиши описание после /photo")
        return

    result = client.images.generate(
        model="gpt-image-1",
        prompt=prompt,
        size="1024x1024"
    )

    image_base64 = result.data[0].b64_json

    import base64
    image_bytes = base64.b64decode(image_base64)

    await update.message.reply_photo(photo=image_bytes)

async def chat(update: Update, context):
    if update.effective_user.id != OWNER_ID:
        return

    user_id = update.effective_user.id
    text = update.message.text

    if user_id not in memory:
        memory[user_id] = []

    memory[user_id].append({"role": "user", "content": text})

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=memory[user_id]
    )

    answer = response.choices[0].message.content

    memory[user_id].append({"role": "assistant", "content": answer})

    await update.message.reply_text(answer)

telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(CommandHandler("reset", reset))
telegram_app.add_handler(CommandHandler("photo", photo))
telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))

@app.post("/")
async def webhook(request: Request):
    data = await request.json()
    update = Update.de_json(data, telegram_app.bot)
    await telegram_app.process_update(update)
    return {"ok": True}
