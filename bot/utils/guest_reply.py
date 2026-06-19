import secrets

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import ContextTypes

from core.config import BOT_LINK, DEV_BOT_LINK, USE_DEV_BOT


def active_bot_link() -> str:
    raw = DEV_BOT_LINK if USE_DEV_BOT else BOT_LINK
    return (raw or "").strip()


def open_bot_line() -> str:
    link = active_bot_link()
    if link:
        return f'<a href="{link}">Open me in private chat</a> 💕'
    return "Open @nsfw_prompt_generator_bot in a private chat 💕"


def open_bot_markup(label: str = "Open me privately 💕") -> InlineKeyboardMarkup | None:
    link = active_bot_link()
    if not link:
        return None
    return InlineKeyboardMarkup([[InlineKeyboardButton(label, url=link)]])


async def send_reply_message(
    message,
    context: ContextTypes.DEFAULT_TYPE,
    text: str,
    *,
    parse_mode: str | None = None,
    reply_markup=None,
) -> None:
    if message.guest_query_id:
        result = InlineQueryResultArticle(
            id=secrets.token_hex(8),
            title="NSFW Prompt Generator AI",
            input_message_content=InputTextMessageContent(
                message_text=text,
                parse_mode=parse_mode,
            ),
            reply_markup=reply_markup,
        )
        await context.bot.answer_guest_query(message.guest_query_id, result)
        return

    await message.reply_text(
        text,
        parse_mode=parse_mode,
        reply_markup=reply_markup,
        disable_web_page_preview=True,
    )
