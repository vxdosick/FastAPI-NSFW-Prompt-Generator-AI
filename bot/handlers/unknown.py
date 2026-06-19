# Imports
from telegram import Update
from telegram.ext import ContextTypes
async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"Don't know that one, love 😅\n\n"
        f"/start · /help · /balance · /prompts\n"
        f"/whats_new · /contacts · /terms\n\n"
        f"Or just tell me a fantasy — I'm listening 🔥💕"
    )
