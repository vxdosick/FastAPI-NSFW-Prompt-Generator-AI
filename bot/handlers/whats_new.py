from telegram import Update
from telegram.ext import ContextTypes

TELEGRAM_CHANNEL_USERNAME = "nsfwprompts_ai"


def build_whats_new_text() -> str:
    channel = TELEGRAM_CHANNEL_USERNAME.strip().lstrip("@")
    link = f"https://t.me/{channel}"
    handle = f"@{channel}"
    return (
        "What's new 🚀\n\n"
        "All updates live in my Telegram channel now — "
        "new features, news, Q&A, and a peek behind the scenes 💕\n\n"
        f'<a href="{link}">{handle}</a>\n\n'
        "Come say hi when you want the latest ✨"
    )


WHATS_NEW_TEXT = build_whats_new_text()


async def whats_new(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        build_whats_new_text(),
        parse_mode="HTML",
        disable_web_page_preview=True,
    )
