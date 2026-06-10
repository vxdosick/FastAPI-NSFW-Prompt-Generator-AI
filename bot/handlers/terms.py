# Imports
from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ChatType

# Define tokens
from core.config import SERVER_URL

async def terms(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type != ChatType.PRIVATE:
        return

    await update.message.reply_text(
        f"Quick & honest 💕\n\n"
        f"• No subscriptions — pay only for what you use\n"
        f"• Credits land right after payment\n"
        f'<a href="{SERVER_URL}/terms">Terms, Privacy & Refunds</a>',
        parse_mode="HTML",
        disable_web_page_preview=True,
    )
