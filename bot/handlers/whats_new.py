from telegram import Update
from telegram.constants import ChatType
from telegram.ext import ContextTypes

WHATS_NEW_TEXT = (
    "🚀 Latest updates\n\n"
    "📅 2026-06-10\n"
    "• Added a “What's New” section (/whats_new command) Users will be able to keep up to date with the latest updates.\n\n"
    "💎 Keep an eye out for updates – the bot is constantly being developed."
)


async def whats_new(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type != ChatType.PRIVATE:
        return

    await update.message.reply_text(WHATS_NEW_TEXT)
