import logging
import os
from typing import Final

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

# Configure basic logging to stdout for visibility
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# Environment variable name for the bot token
BOT_TOKEN_ENV: Final[str] = "TELEGRAM_BOT_TOKEN"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a greeting message when the /start command is issued."""
    user_first_name = update.effective_user.first_name if update.effective_user else "there"
    await update.message.reply_text(f"Hello, {user_first_name}! 👋\nSend me any message and I will echo it back.")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a help message when the /help command is issued."""
    help_text = (
        "I am a simple echo bot.\n\n"
        "Commands:\n"
        "/start - Greet and describe the bot\n"
        "/help - Show this help message\n\n"
        "Just send any text and I will echo it back."
    )
    await update.message.reply_text(help_text)


async def echo_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Echo back any non-command text message."""
    if update.message and update.message.text:
        await update.message.reply_text(update.message.text)


def main() -> None:
    token = os.getenv(BOT_TOKEN_ENV)
    if not token:
        logger.error(
            "Bot token not found. Please set the %s environment variable.", BOT_TOKEN_ENV,
        )
        raise SystemExit(1)

    application = Application.builder().token(token).build()

    # Register command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))

    # Register a message handler for all text messages that are not commands
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo_text))

    logger.info("Starting bot...")
    application.run_polling(close_loop=False)


if __name__ == "__main__":
    main()
