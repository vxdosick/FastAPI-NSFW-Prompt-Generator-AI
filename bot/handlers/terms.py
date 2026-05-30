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
    (
    f"Terms & Policies 😇\n\n"
    f"Everything is simple and transparent:\n"
    f"• No subscriptions — pay only for what you use\n"
    f"• Instant delivery of generations after payment\n"
    f"<a href=\"{SERVER_URL}/terms\">Terms of Use, Privacy Policy and Refund Policy</a>\n"),
    parse_mode="HTML",
    disable_web_page_preview=True
    )