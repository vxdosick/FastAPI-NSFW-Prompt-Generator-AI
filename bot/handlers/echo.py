# Imports
import asyncio
import html
import json
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes
from telegram.constants import ChatAction, ChatType
from openai import OpenAI

# DB
from db.db_ops import get_or_create_user
from db.database import async_session_maker

# Utils
from bot.utils.is_rate_limited import is_rate_limited
from bot.handlers.balance import build_payment_keyboard
from bot.handlers.prompts import cache_prompt_for_saving

# Define tokens
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
    "Hold on a sec 🙂 I'm still finishing your previous prompt.\n\n"
    "I won't process this new message on purpose — when you get the result above, "
    "just send your next idea again 💦"
)


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


async def _reply_out_of_credits(update: Update, user_id: str) -> None:
    await update.message.reply_text(
        "Oh... just when it was getting good? ❤️ You're out of credits.\n"
        "Don't stop now — your hottest ideas are just one click away.\n\n"
        "Unlock full access instantly:",
        reply_markup=await build_payment_keyboard(user_id),
    )


async def _repeat_typing(context: ContextTypes.DEFAULT_TYPE, chat_id: int) -> None:
    """Keep Telegram 'typing…' visible while a long sync call runs off the event loop."""
    try:
        while True:
            await context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
            await asyncio.sleep(4.5)
    except asyncio.CancelledError:
        return


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type != ChatType.PRIVATE:
        return

    user_id = str(update.effective_user.id)

    # 1) Busy-check FIRST: any text from a user with an active generation is rejected
    # without touching the model, the DB, or the rate limiter. Only the first spam
    # message inside one "busy session" gets a polite reply; the rest are ignored.
    status = await _acquire_or_report_busy(user_id)
    if status == "warn_now":
        await update.message.reply_text(_BUSY_PLEASE_WAIT)
        return
    if status == "silent":
        return
    # status == "acquired" — we now own the slot until _release_busy in finally.

    try:
        # 2) Length check — only meaningful for a brand-new request.
        if len(update.message.text) > 800:
            await update.message.reply_text(
                f"Oops! 😅 Your message is a bit too long (over 800 characters).\n\n"
                f"Please keep it under 800 characters and try again 💦\n"
                f"(Tip: Focus on key details like character, pose, style, and vibe!)")
            return

        # 3) Soft rate limiter (separate from busy-check; protects against
        # rapid-fire requests AFTER a previous one already finished).
        if is_rate_limited(user_id):
            await update.message.reply_text(
                f"Please take a short pause between messages — I need a moment to keep up 🙂\n\n"
                f"Wait a few seconds, then try again 💦")
            return

        async with async_session_maker() as db:
            user = await get_or_create_user(user_id, db)

            if user.credits <= 0:
                await _reply_out_of_credits(update, user_id)
                return

            client = OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=OPENAI_API_KEY,
            )

            chat_id_param = update.effective_chat.id

            def _call_openrouter():
                return client.chat.completions.create(
                    extra_body={},
                    model=AI_MODEL,
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": update.message.text},
                    ],
                    response_format=PROMPT_RESPONSE_FORMAT,
                )

            typing_task = asyncio.create_task(_repeat_typing(context, chat_id_param))
            try:
                completion = await asyncio.to_thread(_call_openrouter)
            finally:
                typing_task.cancel()
                try:
                    await typing_task
                except asyncio.CancelledError:
                    pass

            raw = completion.choices[0].message.content
            if not raw or not raw.strip():
                await update.message.reply_text(
                    f"Oops! 😅 Something went wrong.\n\n"
                    f"Please try again in a moment 💦")
                return

            try:
                data = json.loads(raw)
            except json.JSONDecodeError:
                await update.message.reply_text(
                    f"Oops! 😅 Something went wrong.\n\n"
                    f"Please try again in a moment 💦")
                return

            is_error = bool(data.get("error"))
            prompt = (data.get("prompt") or "").strip()
            title = (data.get("title") or "").strip()
            if title:
                title = " ".join(title.split()[:3])

            if is_error or not prompt:
                await update.message.reply_text(
                    f"Oops! 😅 I couldn't process that request.\n\n"
                    f"It looks like you might have asked for something else entirely (not a prompt request), "
                    f"or it involved minors/extreme illegal content — that's a no-go.\n\n"
                    f"Please describe a fantasy for adult characters (18+ only) and keep it focused on a hot NSFW prompt 😉\n\n"
                    f"Try again with something spicy and clear! 💦")
                return

            user.credits -= 1
            await db.commit()
            await db.refresh(user)

            await update.message.reply_text(
                f"Here we go! 😏🔥\n\n"
                f"Your uncensored NSFW prompt is ready and supercharged for epic results!\n"
                f"Copy it below and paste into your favorite model (Flux, Pony XL, "
                f"Illustrious, RealVisXL, SDXL, Midjourney, Grok & more) 😉\n\n"
                f"Prompt: ⬇️💦\n\n"
                f"<code>{html.escape(prompt)}</code>",
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                "Save Prompt 🍓",
                                callback_data=cache_prompt_for_saving(prompt, title),
                            )
                        ]
                    ]
                ),
            )

    finally:
        # ALWAYS free the slot, no matter how we exit (success, return, raise).
        await _release_busy(user_id)
