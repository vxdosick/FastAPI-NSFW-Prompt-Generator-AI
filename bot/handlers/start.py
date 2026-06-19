# Imports
from telegram import Update
from telegram.ext import ContextTypes
# DB
from db.db_ops import get_or_create_user
from db.database import async_session_maker

_START_EXAMPLE_PROMPT = (
    "Generate a cyberpunk succubus, neon lighting, highly detailed, 8k"
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)

    async with async_session_maker() as db:
        user = await get_or_create_user(user_id, db)

    await update.message.reply_text(
        f"Hey... you came 💕\n\n"
        f"<b>NSFW Prompt Generator AI</b> — whisper me a fantasy, "
        f"I'll dress it up for Flux, Pony, SDXL & more 😈\n\n"
        f"💎 <b>Credits:</b> {user.credits}\n\n"
        f"Try me — tap, copy, send:\n"
        f"<code>{_START_EXAMPLE_PROMPT}</code>",
        parse_mode="HTML",
    )
