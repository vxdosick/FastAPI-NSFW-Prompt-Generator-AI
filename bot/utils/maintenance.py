from telegram import Update
from telegram.ext import ApplicationHandlerStop, ContextTypes

from core.config import MAINTENANCE_MODE, OWNER_TELEGRAM_ID

MAINTENANCE_REPLY = (
    "Oh... I'm so sorry to pop in with bad news 💕\n\n"
    "We're doing a little technical maintenance right now — "
    "just a short pause while everything gets polished ✨\n\n"
    "Our developer is working hard on improvements, all for you — "
    "so your prompts come back even juicier and smoother 🔥\n\n"
    "It won't be long, love... you'll be generating again very, very soon 🍓\n\n"
    "Thank you for waiting — you're the sweetest ❤️"
)


def _is_owner(user_id: int | None) -> bool:
    owner_id = (OWNER_TELEGRAM_ID or "").strip()
    if not owner_id or user_id is None:
        return False
    return str(user_id) == owner_id


async def maintenance_gate(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not MAINTENANCE_MODE:
        return

    if _is_owner(update.effective_user.id if update.effective_user else None):
        return

    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.message.reply_text(MAINTENANCE_REPLY)
    elif update.pre_checkout_query:
        await update.pre_checkout_query.answer(
            ok=False,
            error_message="Sorry, love — quick maintenance. Back very soon 💕",
        )
    elif update.message:
        await update.message.reply_text(MAINTENANCE_REPLY)
    elif update.effective_chat:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=MAINTENANCE_REPLY,
        )

    raise ApplicationHandlerStop()
