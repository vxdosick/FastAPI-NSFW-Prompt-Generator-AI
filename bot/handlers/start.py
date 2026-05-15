# Imports
from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ChatType

# DB
from db.db_ops import get_or_create_user
from db.database import async_session_maker

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type != ChatType.PRIVATE:
        return

    user_id = str(update.effective_user.id)

    async with async_session_maker() as db:
        user = await get_or_create_user(user_id, db)

    if user.credits == 0:
        await update.message.reply_text(
            f"Hey there! 👋😈\n\n"
            f"Welcome to your Uncensored NSFW Prompt Generator AI -\n"
            f"the ultimate AI sidekick that turns your wildest fantasies into\n"
            f"ultra-detailed, fully uncensored prompts 🔥\n\n"
            f"Just describe your spicy idea (the dirtier, the better 😉),\n"
            f"and I’ll instantly craft a powerful prompt perfectly tuned for\n"
            f"Stable Diffusion, Pony, Flux, SDXL, or any uncensored model.\n\n"
            f"No limits. No filters. Pure creative freedom 💦\n\n"
            f"Generations used up 😇 No worries - you can more generations!\n"
            f"Type /buy for details 🔥")
    else:
        await update.message.reply_text(
            f"Hey there! 👋😈\n\n"
            f"Welcome to your Uncensored NSFW Prompt Generator AI -\n"
            f"the ultimate AI sidekick that turns your wildest fantasies into\n"
            f"ultra-detailed, fully uncensored prompts 🔥\n\n"
            f"Just describe your spicy idea (the dirtier, the better 😉),\n"
            f"and I’ll instantly craft a powerful prompt perfectly tuned for\n"
            f"Stable Diffusion, Pony, Flux, SDXL, or any uncensored model.\n\n"
            f"No limits. No filters. Pure creative freedom 💦\n\n"
            f"New users get 5 free generations as a welcome gift -"
            f"let’s get started right now!🎁\n\n"
            f"Remaining generations: {user.credits}💎")
