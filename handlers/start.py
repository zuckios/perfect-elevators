from telegram import Update
from telegram.ext import CommandHandler, ContextTypes


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! 👋\n"
        "Я помогу сформировать коммерческое предложение.\n\n"
        "Нажми /calculate чтобы начать расчёт."
    )

start_handler = CommandHandler("start", start)
