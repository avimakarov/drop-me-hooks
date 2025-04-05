import os
import asyncio

from flask import Flask, request
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

app = Flask(__name__)
PORT = os.getenv()
TOKEN = os.getenv("TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

# Инициализация Application
application = Application.builder().token(TOKEN).build()


# Обработчики
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"Вы сказали: {update.message.text}")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я бот, работающий через WebHook.")


# Регистрация обработчиков
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))


@app.route("/webhook", methods=["POST"])
def webhook():
    if request.method == "POST":
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        update = Update.de_json(request.get_json(force=True), application.bot)
        loop.run_until_complete(application.initialize())
        loop.run_until_complete(application.process_update(update))

    return "ok", 200


async def set_webhook():
    await application.initialize()
    await application.bot.set_webhook(WEBHOOK_URL + "/webhook")


if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(set_webhook())
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 8000)))