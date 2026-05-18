# Imports
from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ChatType

# DB
from db.db_ops import get_or_create_user
from db.database import async_session_maker

_START_EXAMPLE_PROMPT = (
    "Generate a cyberpunk succubus, neon lighting, highly detailed, 8k"
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type != ChatType.PRIVATE:
        return

    user_id = str(update.effective_user.id)

    async with async_session_maker() as db:
        user = await get_or_create_user(user_id, db)

    await update.message.reply_text(
        f"Hey! 😈\n"
        f"<b>Welcome to NSFW Prompt Generator AI.</b>\n\n"
        f"Send me any spicy idea, and I'll turn it into a hyper-detailed, "
        f"uncensored prompt for Flux, Pony, SDXL, or Stable Diffusion.\n\n"
        f"💰 <b>Your Balance:</b> {user.credits} free credits\n\n"
        f"🔥 <b>Try it right now!</b> Tap to copy this example, paste it into "
        f"the chat and send:\n\n"
        f"<code>{_START_EXAMPLE_PROMPT}</code>",
        parse_mode="HTML",
    )
