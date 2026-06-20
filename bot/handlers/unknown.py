# Imports
from telegram import Update
from telegram.ext import ContextTypes


async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Don't know that one, love 😅\n\n"
        "/start · /help · /balance · /prompts · /models\n"
        "/whats_new · /contacts · /terms\n\n"
        "Or just tell me a fantasy — I'm listening 🔥💕"
    )
