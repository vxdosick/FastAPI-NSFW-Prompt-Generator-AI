# Imports
import html

import httpx
from telegram import Update
from telegram.constants import ChatType
from telegram.ext import ContextTypes

# DB
from db.db_ops import get_or_create_user
from db.database import async_session_maker

# Define tokens
from core.config import PAYMENT_BOT_CREDITS, PAYMENT_EURO_PRICE, SERVER_URL


def _price_label() -> str:
    try:
        cents = int(PAYMENT_EURO_PRICE)
    except (TypeError, ValueError):
        return "€1.99"
    return f"€{cents / 100:.2f}"


async def _create_checkout_url(user_id: str) -> str | None:
    if not SERVER_URL:
        return None

    try:
        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.post(f"{SERVER_URL}/create-checkout-session/{user_id}")
            response.raise_for_status()
            data = response.json()
    except (httpx.HTTPError, ValueError):
        return None

    return data.get("url")


async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type != ChatType.PRIVATE:
        return

    user_id = str(update.effective_user.id)

    async with async_session_maker() as db:
        user = await get_or_create_user(user_id, db)

    checkout_url = await _create_checkout_url(user_id)
    credit_pack = PAYMENT_BOT_CREDITS or "150"
    price = _price_label()

    if checkout_url:
        await update.message.reply_text(
            f"Your balance 💎\n\n"
            f"💰 <b>Available credits:</b> {user.credits}\n\n"
            f"Need more generations?\n"
            f"Get <b>{html.escape(str(credit_pack))} premium credits</b> for {html.escape(price)} 🔥\n\n"
            f"👉 <a href=\"{html.escape(checkout_url, quote=True)}\">Buy credits via Stripe</a>",
            parse_mode="HTML",
            disable_web_page_preview=True,
        )
        return

    await update.message.reply_text(
        f"Your balance 💎\n\n"
        f"💰 Available credits: {user.credits}\n\n"
        f"Payment link is temporarily unavailable. Please try again later."
    )
