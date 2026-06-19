import html

from telegram.ext import ContextTypes

from bot.handlers.balance import (
    build_payment_keyboard,
    _payment_content,
    _price_label,
    _stars_price,
)
from bot.handlers.contacts import _support_handle_and_url
from bot.handlers.start import _START_EXAMPLE_PROMPT
from bot.handlers.whats_new import WHATS_NEW_TEXT
from bot.utils.guest_reply import open_bot_line, open_bot_markup, send_reply_message
from db.db_ops import get_or_create_user
from db.database import async_session_maker
from core.config import LEGAL_PAGE_URL

_GUEST_KNOWN = frozenset(
    {"start", "help", "balance", "terms", "contacts", "prompts", "whats_new"}
)


def _parse_command(text: str) -> str | None:
    stripped = text.strip()
    if not stripped.startswith("/"):
        return None
    name = stripped.split()[0].lstrip("/").lower()
    if "@" in name:
        name = name.split("@", 1)[0]
    return name or None


async def try_handle_guest_command(
    message,
    context: ContextTypes.DEFAULT_TYPE,
    user_id: str,
    text: str,
) -> bool:
    if not message.guest_query_id:
        return False

    cmd = _parse_command(text)
    if cmd is None:
        return False

    if cmd not in _GUEST_KNOWN:
        await send_reply_message(
            message,
            context,
            "Don't know that one here, love 😅\n\n"
            "/start · /help · /balance · /prompts\n"
            "/whats_new · /contacts · /terms\n\n"
            f"Or @ me with a fantasy 🔥\n\n{open_bot_line()}",
            parse_mode="HTML",
        )
        return True

    if cmd == "start":
        async with async_session_maker() as db:
            user = await get_or_create_user(user_id, db)
        await send_reply_message(
            message,
            context,
            f"Hey... you summoned me 💕\n\n"
            f"<b>NSFW Prompt Generator AI</b> — spicy ideas → Flux, Pony, SDXL prompts 😈\n\n"
            f"💎 <b>Credits:</b> {user.credits}\n\n"
            f"Try:\n<code>{_START_EXAMPLE_PROMPT}</code>\n\n"
            f"For everything else — {open_bot_line()}",
            parse_mode="HTML",
        )
        return True

    if cmd == "help":
        await send_reply_message(
            message,
            context,
            "Little cheat sheet for you 💕\n\n"
            "Here in this chat, tag me like this:\n"
            "<code>@nsfw_prompt_generator_bot your scene</code>\n"
            "or <code>@nsfw_prompt_generator_bot /balance</code>\n\n"
            "/start — hello & credits\n"
            "/help — this menu\n"
            "/balance — credits & top-up ❤️\n"
            "/prompts — saved prompts 🍓\n"
            "/whats_new — what's new 🚀\n"
            "/contacts — reach me\n\n"
            "Plain /commands without @ won't reach me here — always tag me first 😉\n\n"
            f"{open_bot_line()}",
            parse_mode="HTML",
        )
        return True

    if cmd == "balance":
        async with async_session_maker() as db:
            user = await get_or_create_user(user_id, db)
        payment_content = _payment_content()
        price = _price_label()
        stars_price = _stars_price()
        await send_reply_message(
            message,
            context,
            f"Your balance 💎\n\n"
            f"💕 <b>Credits:</b> {user.credits}\n\n"
            f"Stripe — <b>{html.escape(price)}</b> → "
            f"<b>{html.escape(payment_content)}</b>\n"
            f"Stars — <b>{stars_price} ⭐</b> → "
            f"<b>{html.escape(payment_content)}</b>\n\n"
            f"Pick how you want to pay, love ❤️",
            parse_mode="HTML",
            reply_markup=await build_payment_keyboard(user_id, guest=True),
        )
        return True

    if cmd == "terms":
        await send_reply_message(
            message,
            context,
            f"Quick & honest 💕\n\n"
            f"• No subscriptions — pay only for what you use\n"
            f"• Credits land right after payment\n"
            f'<a href="{LEGAL_PAGE_URL}">Terms, Privacy & Refunds</a>\n\n'
            f"{open_bot_line()}",
            parse_mode="HTML",
        )
        return True

    if cmd == "contacts":
        display, url = _support_handle_and_url()
        if url and display:
            body = (
                f"Need me? 💕\n\n"
                f"Bug, question, or just want to say hi:\n\n"
                f'<a href="{url}">{display}</a>\n\n'
                f"{open_bot_line()}"
            )
        else:
            body = (
                "Support's quiet right now, love 😅\n"
                f"Try again a little later 💕\n\n"
                f"{open_bot_line()}"
            )
        await send_reply_message(message, context, body, parse_mode="HTML")
        return True

    if cmd == "whats_new":
        await send_reply_message(
            message,
            context,
            f"{WHATS_NEW_TEXT}\n\n{open_bot_line()}",
            parse_mode="HTML",
        )
        return True

    if cmd == "prompts":
        await send_reply_message(
            message,
            context,
            "Saved prompts live in my private chat, love 🍓\n\n"
            "I can't flip through your list right here — "
            "but open me and tap /prompts 💕",
            parse_mode="HTML",
            reply_markup=open_bot_markup("My saved prompts 🍓"),
        )
        return True

    return False
