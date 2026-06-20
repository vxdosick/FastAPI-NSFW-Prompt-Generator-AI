# Imports
from telegram import Update
from telegram.ext import ContextTypes

from bot.handlers.models import models_help_text


async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Little cheat sheet for you 💕\n\n"
        "Send any spicy scene — I'll craft positive + negative prompts 🔥\n"
        "Or pick a model for a tuned result — see /models 🎯\n\n"
        "/start — hello & credits\n"
        "/help — this menu\n"
        "/models — all model commands\n"
        "/balance — credits & top-up ❤️\n"
        "/prompts — saved prompts 🍓\n"
        "/whats_new — what's new 🚀\n"
        "/contacts — reach me\n\n"
        "Go on, love... describe something wicked 😉",
        parse_mode="HTML",
    )
