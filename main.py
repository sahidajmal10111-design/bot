import os
import logging
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from database import init_db, clear_history
from handlers.text import handle_text
from handlers.voice import handle_voice
from handlers.image import handle_photo

load_dotenv()

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("Bot-key")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
PORT = int(os.getenv("PORT", 8443))

init_db()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command."""
    name = update.effective_user.first_name
    await update.message.reply_text(
        f"Hello {name}! 👋 How are you? What do you want to talk about?"
    )


async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /reset command — clear chat history."""
    clear_history(update.effective_user.id)
    await update.message.reply_text("Alright, let's start fresh! 🙂")


def main():
    app = Application.builder().token(TOKEN).build()

    # Register handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("reset", reset))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.add_handler(MessageHandler(filters.VOICE, handle_voice))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    if WEBHOOK_URL:
        # Webhook mode (VPS / paid hosting)
        logger.info(f"Starting webhook mode: {WEBHOOK_URL}")
        app.run_webhook(
            listen="0.0.0.0",
            port=PORT,
            url_path=TOKEN,
            webhook_url=f"{WEBHOOK_URL}/{TOKEN}"
        )
    else:
        # Polling mode (local / free tier)
        logger.info("Starting polling mode...")
        app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
