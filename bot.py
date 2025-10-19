import logging
import os
import random
import re
from dataclasses import dataclass
from typing import Final, Optional, Pattern, Sequence

from telegram import ReactionTypeEmoji, Update
from telegram.error import TelegramError
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

# Configure basic logging to stdout for visibility
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# Environment variables
BOT_TOKEN_ENV: Final[str] = "TELEGRAM_BOT_TOKEN"
EMOJIS_ENV: Final[str] = "TELEGRAM_REACTION_EMOJIS"  # comma-separated emojis, e.g. "👍,🔥,😄"
IS_BIG_ENV: Final[str] = "TELEGRAM_REACTION_BIG"      # true/false (default: false)
REACT_TO_BOTS_ENV: Final[str] = "TELEGRAM_REACT_TO_BOTS"  # true/false (default: false)
REGEX_ENV: Final[str] = "TELEGRAM_REACTION_MATCH_REGEX"   # optional regex; if set, only react when matches
ALLOWED_CHAT_IDS_ENV: Final[str] = "TELEGRAM_ALLOWED_CHAT_IDS"  # CSV of chat ids; if set, only these
ALLOWED_USER_IDS_ENV: Final[str] = "TELEGRAM_ALLOWED_USER_IDS"  # CSV of user ids; if set, only these


@dataclass(frozen=True)
class BotConfig:
    emojis: Sequence[str]
    is_big: bool
    react_to_bots: bool
    message_regex: Optional[Pattern[str]]
    allowed_chat_ids: Optional[set[int]]
    allowed_user_ids: Optional[set[int]]


def _parse_bool(value: Optional[str], default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "y", "on"}


def _parse_csv_ints(value: Optional[str]) -> Optional[set[int]]:
    if not value:
        return None
    result: set[int] = set()
    for part in value.split(","):
        part = part.strip()
        if not part:
            continue
        try:
            result.add(int(part))
        except ValueError:
            logger.warning("Ignoring non-integer id in CSV: %s", part)
    return result or None


def _parse_emojis(value: Optional[str]) -> Sequence[str]:
    if not value:
        return ["👍"]
    emojis = [e.strip() for e in value.split(",") if e.strip()]
    return emojis or ["👍"]


def _compile_regex(value: Optional[str]) -> Optional[Pattern[str]]:
    if not value:
        return None
    try:
        return re.compile(value)
    except re.error as exc:
        logger.error("Invalid %s: %s", REGEX_ENV, exc)
        raise SystemExit(1)


def load_config_from_env() -> BotConfig:
    return BotConfig(
        emojis=_parse_emojis(os.getenv(EMOJIS_ENV)),
        is_big=_parse_bool(os.getenv(IS_BIG_ENV), default=False),
        react_to_bots=_parse_bool(os.getenv(REACT_TO_BOTS_ENV), default=False),
        message_regex=_compile_regex(os.getenv(REGEX_ENV)),
        allowed_chat_ids=_parse_csv_ints(os.getenv(ALLOWED_CHAT_IDS_ENV)),
        allowed_user_ids=_parse_csv_ints(os.getenv(ALLOWED_USER_IDS_ENV)),
    )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a greeting message when the /start command is issued."""
    user_first_name = update.effective_user.first_name if update.effective_user else "there"
    await update.message.reply_text(f"Hello, {user_first_name}! 👋\nSend me any message and I will echo it back.")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a help message when the /help command is issued."""
    help_text = (
        "I react to messages with configured emoji(s).\n\n"
        "Environment variables:\n"
        f"- {EMOJIS_ENV}: comma-separated emojis (default: 👍)\n"
        f"- {IS_BIG_ENV}: true/false for big reaction (default: false)\n"
        f"- {REACT_TO_BOTS_ENV}: react to bot messages (default: false)\n"
        f"- {REGEX_ENV}: optional regex to filter messages\n"
        f"- {ALLOWED_CHAT_IDS_ENV}: CSV of chat ids allowlist\n"
        f"- {ALLOWED_USER_IDS_ENV}: CSV of user ids allowlist\n"
    )
    if update.message:
        await update.message.reply_text(help_text)


async def react_to_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Add an emoji reaction to incoming messages based on configuration."""
    message = update.effective_message
    chat = update.effective_chat
    user = update.effective_user

    if not message or not chat:
        return

    # Access config stored in application bot_data
    cfg: BotConfig = context.bot_data.get("config")  # type: ignore[assignment]
    if cfg is None:
        logger.error("Configuration missing from bot_data; skipping reaction")
        return

    if not cfg.react_to_bots and user and getattr(user, "is_bot", False):
        return

    if cfg.allowed_chat_ids is not None and chat.id not in cfg.allowed_chat_ids:
        return

    if cfg.allowed_user_ids is not None and user and user.id not in cfg.allowed_user_ids:
        return

    if cfg.message_regex is not None:
        text_to_check = message.text or message.caption or ""
        if not cfg.message_regex.search(text_to_check):
            return

    try:
        chosen = random.choice(list(cfg.emojis))
        await context.bot.set_message_reaction(
            chat_id=chat.id,
            message_id=message.id,
            reaction=[ReactionTypeEmoji(emoji=chosen)],
            is_big=cfg.is_big,
        )
        logger.debug("Reacted to message %s in chat %s with %s", message.id, chat.id, chosen)
    except TelegramError as exc:
        logger.warning("Failed to set reaction: %s", exc)


def main() -> None:
    token = os.getenv(BOT_TOKEN_ENV)
    if not token:
        logger.error(
            "Bot token not found. Please set the %s environment variable.", BOT_TOKEN_ENV,
        )
        raise SystemExit(1)

    config = load_config_from_env()
    logger.info(
        "Starting reaction bot with emojis=%s, is_big=%s, react_to_bots=%s, regex=%s, allowed_chats=%s, allowed_users=%s",
        ",".join(config.emojis),
        config.is_big,
        config.react_to_bots,
        getattr(config.message_regex, "pattern", None),
        (len(config.allowed_chat_ids) if config.allowed_chat_ids else None),
        (len(config.allowed_user_ids) if config.allowed_user_ids else None),
    )

    application = Application.builder().token(token).build()

    # Stash config for handlers
    application.bot_data["config"] = config

    # Register command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))

    # React to most user-visible message types; avoid status updates
    message_filter = (~filters.StatusUpdate.ALL) & (~filters.COMMAND)
    application.add_handler(MessageHandler(message_filter, react_to_message))

    application.run_polling(close_loop=False)


if __name__ == "__main__":
    main()
