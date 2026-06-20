# Imports
import asyncio
import html
import json
import re
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes, filters
from telegram.constants import ChatAction
from openai import OpenAI

# DB
from db.db_ops import get_or_create_user
from db.database import async_session_maker

# Utils
from bot.handlers.balance import build_payment_keyboard
from bot.handlers.guest_commands import try_handle_guest_command
from bot.handlers.prompts import cache_prompt_token, SAVE_START_PREFIX
from bot.utils.guest_reply import active_bot_link, bot_start_url, send_reply_message
from bot.utils.is_rate_limited import is_rate_limited

from core.supported_models import supported_models_phrase
from core.config import (
    OPENAI_API_KEY,
    AI_MODEL,
    SYSTEM_PROMPT,
)


PROMPT_RESPONSE_FORMAT = {
    "type": "json_schema",
    "json_schema": {
        "name": "nsfw_prompt_generation",
        "strict": True,
        "schema": {
            "type": "object",
            "properties": {
                "error": {
                    "type": "boolean",
                    "description": (
                        "True if the user request is off-topic, unsafe, or cannot be turned into a valid prompt."
                    ),
                },
                "prompt": {
                    "type": "string",
                    "description": (
                        "Final English image prompt, ~300–400 characters. Must be empty when error is true."
                    ),
                },
                "title": {
                    "type": "string",
                    "description": (
                        "2–3 short English words labeling the scene for the user's saved list. "
                        "Must be empty when error is true."
                    ),
                },
                "reason": {
                    "type": "string",
                    "description": (
                        "Short machine-oriented tag or note when error is true (e.g. off_topic, minors, "
                        "not_a_prompt_request). Empty string when error is false."
                    ),
                },
            },
            "required": ["error", "prompt", "title", "reason"],
            "additionalProperties": False,
        },
    },
}

# Single source of truth for per-user "generation in progress" state.
# Stored under one asyncio lock so check + mutation is atomic across coroutines.
_busy_lock = asyncio.Lock()
# user_id -> {"warned": bool}  (warned == True means we already replied "please wait" for this session)
_busy_state: dict[str, dict] = {}

_BUSY_PLEASE_WAIT = (
    "One sec, love... still on your last one 💕\n"
    "Send the next idea when it's done 😊"
)


class GuestTextFilter(filters.MessageFilter):

    def filter(self, message):
        return bool(message.guest_query_id and message.text)


GUEST_TEXT = GuestTextFilter()


def _strip_bot_mention(text: str, bot_username: str | None) -> str:
    cleaned = text.strip()
    if not bot_username:
        return cleaned
    pattern = rf"@?{re.escape(bot_username)}\s*"
    return re.sub(pattern, "", cleaned, flags=re.IGNORECASE).strip()


async def _bot_username(context: ContextTypes.DEFAULT_TYPE) -> str | None:
    cached = context.bot_data.get("bot_username")
    if cached:
        return cached
    me = await context.bot.get_me()
    username = (me.username or "").strip() or None
    if username:
        context.bot_data["bot_username"] = username
    return username


async def _reply_out_of_credits(
    message,
    context: ContextTypes.DEFAULT_TYPE,
    user_id: str,
) -> None:
    await send_reply_message(
        message,
        context,
        "Oh no... credits ran out right when it was getting fun ❤️\n"
        "Top up and we keep going — one tap:",
        reply_markup=await build_payment_keyboard(
            user_id, guest=bool(message.guest_query_id)
        ),
    )


def _prompt_reply_markup(message, prompt: str, title: str) -> InlineKeyboardMarkup:
    token = cache_prompt_token(prompt, title)
    rows = []

    if message.guest_query_id:
        save_url = bot_start_url(f"{SAVE_START_PREFIX}{token}")
        if save_url:
            rows.append([InlineKeyboardButton("Save Prompt 🍓", url=save_url)])
    else:
        rows.append(
            [
                InlineKeyboardButton(
                    "Save Prompt 🍓",
                    callback_data=f"save_prompt:{token}",
                )
            ]
        )

    bot_link = active_bot_link()
    if message.guest_query_id and bot_link:
        rows.append(
            [InlineKeyboardButton("Open me privately 💕", url=bot_link)]
        )
    return InlineKeyboardMarkup(rows)


# Returns one of:
#   "acquired"   -> nobody was busy, we just marked this user busy. Caller must call _release_busy in finally.
#   "warn_now"   -> user is already busy; this is the first spam during the active session, send the polite reply.
#   "silent"     -> user is already busy and was already warned; ignore silently.
async def _acquire_or_report_busy(user_id: str) -> str:
    async with _busy_lock:
        state = _busy_state.get(user_id)
        if state is None:
            _busy_state[user_id] = {"warned": False}
            return "acquired"
        if not state["warned"]:
            state["warned"] = True
            return "warn_now"
        return "silent"


async def _release_busy(user_id: str) -> None:
    async with _busy_lock:
        _busy_state.pop(user_id, None)


async def _repeat_typing(context: ContextTypes.DEFAULT_TYPE, chat_id: int) -> None:
    """Keep Telegram 'typing…' visible while a long sync call runs off the event loop."""
    try:
        while True:
            await context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
            await asyncio.sleep(4.5)
    except asyncio.CancelledError:
        return


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.effective_message
    if not message or not message.text:
        return

    user = update.effective_user
    if not user:
        return

    user_id = str(user.id)
    prompt_text = _strip_bot_mention(message.text, await _bot_username(context))
    if not prompt_text:
        await send_reply_message(
            message,
            context,
            "Tell me what to paint, love 💕\n"
            "Scene, mood, outfit — I'll turn it into a prompt 🔥",
        )
        return

    if message.guest_query_id and await try_handle_guest_command(
        message, context, user_id, prompt_text
    ):
        return

    # 1) Busy-check FIRST
    # without touching the model, the DB, or the rate limiter. Only the first spam
    # message inside one "busy session" gets a polite reply; the rest are ignored.
    status = await _acquire_or_report_busy(user_id)
    if status == "warn_now":
        await send_reply_message(message, context, _BUSY_PLEASE_WAIT)
        return
    if status == "silent":
        return
    # status == "acquired" — we now own the slot until _release_busy in finally.

    typing_chat_id = (
        message.guest_bot_caller_chat.id
        if message.guest_bot_caller_chat
        else message.chat_id
    )

    try:
        # 2) Length check — only meaningful for a brand-new request.
        if len(prompt_text) > 800:
            await send_reply_message(
                message,
                context,
                "That's a lot at once, love 😅\n"
                "Keep it under 800 chars — scene, pose, mood — then send again 💕",
            )
            return

        # 3) Soft rate limiter (separate from busy-check; protects against
        # rapid-fire requests AFTER a previous one already finished).
        if is_rate_limited(user_id):
            await send_reply_message(
                message,
                context,
                "Slow down a tiny bit for me? 💕\n"
                "Few seconds, then try again...",
            )
            return

        async with async_session_maker() as db:
            user_row = await get_or_create_user(user_id, db)

            if user_row.credits <= 0:
                await _reply_out_of_credits(message, context, user_id)
                return

            client = OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=OPENAI_API_KEY,
            )

            def _call_openrouter():
                return client.chat.completions.create(
                    extra_body={},
                    model=AI_MODEL,
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": prompt_text},
                    ],
                    response_format=PROMPT_RESPONSE_FORMAT,
                )

            typing_task = None
            if not message.guest_query_id:
                typing_task = asyncio.create_task(_repeat_typing(context, typing_chat_id))
            try:
                completion = await asyncio.to_thread(_call_openrouter)
            finally:
                if typing_task is not None:
                    typing_task.cancel()
                    try:
                        await typing_task
                    except asyncio.CancelledError:
                        pass

            raw = completion.choices[0].message.content
            if not raw or not raw.strip():
                await send_reply_message(
                    message,
                    context,
                    "Something hiccuped on my side 😅\n"
                    "Try again in a moment, love 💕",
                )
                return

            try:
                data = json.loads(raw)
            except json.JSONDecodeError:
                await send_reply_message(
                    message,
                    context,
                    "Something hiccuped on my side 😅\n"
                    "Try again in a moment, love 💕",
                )
                return

            is_error = bool(data.get("error"))
            prompt = (data.get("prompt") or "").strip()
            title = (data.get("title") or "").strip()
            if title:
                title = " ".join(title.split()[:3])

            if is_error or not prompt:
                await send_reply_message(
                    message,
                    context,
                    "I can't do that one, love 😅\n\n"
                    "Adults only (18+), and it needs to be a real prompt idea.\n"
                    "Paint me a spicy scene — I'll make it beautiful 💕",
                )
                return

            user_row.credits -= 1
            await db.commit()
            await db.refresh(user_row)

            save_hint = ""
            if message.guest_query_id:
                save_hint = (
                    "\n\n<i>Tap Save 🍓 — I'll open privately and keep it for you 💕</i>"
                )

            await send_reply_message(
                message,
                context,
                f"For you... 😏💕\n\n"
                f"<code>{html.escape(prompt)}</code>\n\n"
                f"Copy & paste into {supported_models_phrase()} 🔥"
                f"{save_hint}",
                parse_mode="HTML",
                reply_markup=_prompt_reply_markup(message, prompt, title),
            )

    finally:
        # ALWAYS free the slot, no matter how we exit (success, return, raise).
        await _release_busy(user_id)
