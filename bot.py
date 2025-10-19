import logging
import os
from typing import Final, List, Sequence

from telegram import Update, Bot, ReactionTypeEmoji
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

# Configure basic logging to stdout for visibility
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# Environment variable name for the bot token
BOT_TOKEN_ENV: Final[str] = "TELEGRAM_BOT_TOKEN"


async def set_reactions_parallel(
    bot: Bot,
    chat_id: int,
    message_id: int,
    emojis: Sequence[str],
) -> None:
    """Set multiple reactions on a message in a single API call.

    Telegram's API supports setting multiple reactions at once. We build the
    list of ReactionTypeEmoji and call set_message_reaction once. This is more
    efficient and avoids race conditions from multiple sequential calls.
    """
    if not emojis:
        return

    reaction_types: List[ReactionTypeEmoji] = []
    for raw_emoji in emojis:
        emoji = (raw_emoji or "").strip()
        if not emoji:
            continue
        reaction_types.append(ReactionTypeEmoji(emoji=emoji))

    if not reaction_types:
        return

    await bot.set_message_reaction(
        chat_id=chat_id,
        message_id=message_id,
        reaction=reaction_types,
    )

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


async def react_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """React to a replied message with the provided emojis.

    Usage: reply to a message with `/react 👍 😂 🔥`
    """
    if not update.message:
        return

    if not update.message.reply_to_message:
        await update.message.reply_text(
            "Please reply to a message and use: /react 👍 😂 🔥"
        )
        return

    emojis: List[str] = context.args or []
    if not emojis:
        await update.message.reply_text(
            "Provide emojis after the command, e.g., /react 👍 😂 🔥"
        )
        return

    # Safely resolve chat_id even when effective_chat is absent in tests
    effective_chat = getattr(update, "effective_chat", None)
    chat_id = getattr(effective_chat, "id", None) if effective_chat else update.message.chat_id
    target_message_id = update.message.reply_to_message.message_id

    await set_reactions_parallel(
        bot=context.bot,
        chat_id=chat_id,
        message_id=target_message_id,
        emojis=emojis,
    )

    await update.message.reply_text("Reactions added ✨")


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
    application.add_handler(CommandHandler("react", react_command))

    # Register a message handler for all text messages that are not commands
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo_text))

    logger.info("Starting bot...")
    application.run_polling(close_loop=False)


if __name__ == "__main__":
    main()
