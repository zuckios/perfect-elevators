import os

from dotenv import load_dotenv
from telegram.ext import ApplicationBuilder
from handlers.start import start_handler
from handlers.conversation import conversation_handler

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

def main():
    if not BOT_TOKEN:
        raise SystemExit("Установите BOT_TOKEN в переменные окружения или в файл .env")
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(start_handler)
    app.add_handler(conversation_handler)

    print("🤖 Bot started...")
    app.run_polling()


if __name__ == "__main__":
    main()

