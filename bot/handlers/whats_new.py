from telegram import Update
from telegram.constants import ChatType
from telegram.ext import ContextTypes

WHATS_NEW_TEXT = (
    "What's new 🚀\n\n"
    "📅 2026-06-10\n"
    "• /whats_new — keep up with me here 💕\n"
    "• I've changed the bot's text for you ❤️\n\n"
    "I'm always getting better for you ✨"
)


async def whats_new(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type != ChatType.PRIVATE:
        return

    await update.message.reply_text(WHATS_NEW_TEXT)
