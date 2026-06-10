# Imports
import html

import httpx
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, LabeledPrice, Update
from telegram.constants import ChatType
from telegram.ext import ContextTypes

# DB
from db.db_ops import add_credits, get_or_create_user
from db.database import async_session_maker

# Define tokens
from core.config import PAYMENT_BOT_CREDITS, PAYMENT_CONTENT, PAYMENT_EURO_PRICE, PAYMENT_STARS_PRICE, SERVER_URL

STARS_CALLBACK_DATA = "buy_stars"


def _price_label() -> str:
    try:
        cents = int(PAYMENT_EURO_PRICE)
    except (TypeError, ValueError):
        return "€1.99"
    return f"€{cents / 100:.2f}"


def _credit_pack() -> int:
    return int(str(PAYMENT_BOT_CREDITS).strip())


def _payment_content() -> str:
    return str(PAYMENT_CONTENT).strip()


def _stars_price() -> int:
    return int(str(PAYMENT_STARS_PRICE).strip())


async def _create_checkout_url(user_id: str) -> str | None:
    if not SERVER_URL:
        return None

    try:
        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.post(f"{SERVER_URL}/create-checkout-session/{user_id}")
            response.raise_for_status()
            data = response.json()
    except (httpx.HTTPError, ValueError) as e:
        print("STRIPE CHECKOUT LINK ERROR:", e)
        return None

    return data.get("url")


async def build_payment_keyboard(user_id: str) -> InlineKeyboardMarkup:
    checkout_url = await _create_checkout_url(user_id)
    stars_price = _stars_price()
    buttons = []

    if checkout_url:
        buttons.append(InlineKeyboardButton("Stripe 💳", url=checkout_url))
    buttons.append(
        InlineKeyboardButton(f"Pay {stars_price} ⭐", callback_data=STARS_CALLBACK_DATA)
    )

    return InlineKeyboardMarkup([buttons])


async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type != ChatType.PRIVATE:
        return

    user_id = str(update.effective_user.id)

    async with async_session_maker() as db:
        user = await get_or_create_user(user_id, db)

    payment_content = _payment_content()
    price = _price_label()
    stars_price = _stars_price()

    await update.message.reply_text(
        f"Your balance 💎\n\n"
        f"💕 <b>Credits:</b> {user.credits}\n\n"
        f"Stripe — <b>{html.escape(price)}</b> → "
        f"<b>{html.escape(payment_content)}</b>\n"
        f"Stars — <b>{stars_price} ⭐</b> → "
        f"<b>{html.escape(payment_content)}</b>\n\n"
        f"Pick how you want to pay, love ❤️",
        parse_mode="HTML",
        reply_markup=await build_payment_keyboard(user_id),
        disable_web_page_preview=True,
    )


async def stars_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not query or query.message.chat.type != ChatType.PRIVATE:
        return

    await query.answer()

    user_id = str(query.from_user.id)
    credit_pack = _credit_pack()
    payment_content = _payment_content()
    stars_price = _stars_price()

    await query.message.reply_invoice(
        title=payment_content,
        description=f"More steamy prompts for you — {payment_content} ✨",
        payload=f"stars:{user_id}:{credit_pack}",
        provider_token="",
        currency="XTR",
        prices=[LabeledPrice(payment_content, stars_price)],
    )


async def stars_pre_checkout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.pre_checkout_query
    payload_parts = (query.invoice_payload or "").split(":")
    expected_credits = str(_credit_pack())
    stars_price = _stars_price()

    is_valid = (
        query.currency == "XTR"
        and query.total_amount == stars_price
        and len(payload_parts) == 3
        and payload_parts[0] == "stars"
        and payload_parts[1] == str(query.from_user.id)
        and payload_parts[2] == expected_credits
    )

    if not is_valid:
        await query.answer(ok=False, error_message="Something's off with this payment, love 💕")
        return

    await query.answer(ok=True)


async def stars_successful_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type != ChatType.PRIVATE:
        return

    payment = update.message.successful_payment
    payload_parts = (payment.invoice_payload or "").split(":")
    credit_pack = _credit_pack()
    payment_content = _payment_content()
    stars_price = _stars_price()

    is_valid = (
        payment.currency == "XTR"
        and payment.total_amount == stars_price
        and len(payload_parts) == 3
        and payload_parts[0] == "stars"
        and payload_parts[1] == str(update.effective_user.id)
        and payload_parts[2] == str(credit_pack)
    )

    if not is_valid:
        await update.message.reply_text(
            "Got your payment, love — but I couldn't confirm it 😅\n"
            "Please /contacts and we'll sort it out 💕"
        )
        return

    async with async_session_maker() as db:
        await get_or_create_user(str(update.effective_user.id), db)
        await add_credits(str(update.effective_user.id), credit_pack, db)

    await update.message.reply_text(
        f"Thank you... ⭐\n\n"
        f"{payment_content} added to your balance 💎\n"
        f"Can't wait to see what you'll create 😈"
    )
