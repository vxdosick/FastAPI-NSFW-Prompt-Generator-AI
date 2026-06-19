# Imports
from telegram import Update
from telegram.ext import ContextTypes
from core.config import SUPPORT_TELEGRAM


def _support_handle_and_url():
    raw = (SUPPORT_TELEGRAM or "").strip()
    if not raw:
        return None, None
    display = raw if raw.startswith("@") else f"@{raw}"
    username = display.lstrip("@")
    if not username:
        return None, None
    return display, f"https://t.me/{username}"


async def contacts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    display, url = _support_handle_and_url()
    if url and display:
        await update.message.reply_text(
            f"Need me? 💕\n\n"
            f"Bug, question, or just want to say hi — message here:\n\n"
            f'<a href="{url}">{display}</a>',
            parse_mode="HTML",
            disable_web_page_preview=True,
        )
    else:
        await update.message.reply_text(
            f"Support's quiet right now, love 😅\n"
            f"Try again a little later 💕"
        )
