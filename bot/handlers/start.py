# Imports
import html

from telegram import Update
from telegram.ext import ContextTypes

# DB
from db.db_ops import get_or_create_user
from db.database import async_session_maker

from bot.handlers.balance import STARS_START_PARAM, send_stars_invoice
from bot.handlers.prompts import SAVE_START_PREFIX, save_prompt_from_token
from core.config import MAX_SAVED_PROMPTS

_START_EXAMPLE_PROMPT = (
    "Generate a cyberpunk succubus, neon lighting, highly detailed, 8k"
)


async def _handle_start_deeplink(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    param: str,
) -> bool:
    if param in (STARS_START_PARAM, "buy_stars"):
        user_id = str(update.effective_user.id)
        await send_stars_invoice(
            context,
            update.effective_chat.id,
            user_id,
        )
        return True

    if param.startswith(SAVE_START_PREFIX):
        token = param[len(SAVE_START_PREFIX):]
        if not token:
            return False

        user_id = str(update.effective_user.id)
        saved_title, status = await save_prompt_from_token(user_id, token)

        if status == "expired":
            await update.message.reply_text(
                "That one's gone, love — generate it again 🔄"
            )
            return True

        if status == "full":
            await update.message.reply_text(
                f"Only {MAX_SAVED_PROMPTS} spots, love 🍓\n"
                f"Open /prompts to make room 💕"
            )
            return True

        await update.message.reply_text(
            f"Saved as {html.escape(saved_title)} ✅\n"
            f"/prompts whenever you want it back 💕",
            parse_mode="HTML",
        )
        return True

    if param == "payment_success":
        await update.message.reply_text(
            "Payment landed 💎\n"
            "Credits should be on your balance — let's create something hot 🔥"
        )
        return True

    if param == "payment_cancel":
        await update.message.reply_text(
            "No worries, love 💕\n"
            "/balance whenever you're ready ❤️"
        )
        return True

    return False


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args and await _handle_start_deeplink(update, context, context.args[0]):
        return

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
