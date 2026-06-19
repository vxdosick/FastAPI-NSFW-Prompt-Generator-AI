# Imports
from telegram import Update
from telegram.ext import ContextTypes
# Define tokens
from core.config import LEGAL_PAGE_URL

async def terms(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"Quick & honest 💕\n\n"
        f"• No subscriptions — pay only for what you use\n"
        f"• Credits land right after payment\n"
        f'<a href="{LEGAL_PAGE_URL}">Terms, Privacy & Refunds</a>',
        parse_mode="HTML",
        disable_web_page_preview=True,
    )
