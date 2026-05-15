# Imports
import asyncio
import json
from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ChatAction, ChatType
from openai import OpenAI

# DB
from db.db_ops import get_or_create_user
from db.database import async_session_maker

# Utils
from bot.utils.is_rate_limited import is_rate_limited

# Define tokens
from core.config import OPENAI_API_KEY, AI_MODEL, SYSTEM_PROMPT


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
                "reason": {
                    "type": "string",
                    "description": (
                        "Short machine-oriented tag or note when error is true (e.g. off_topic, minors, "
                        "not_a_prompt_request). Empty string when error is false."
                    ),
                },
            },
            "required": ["error", "prompt", "reason"],
            "additionalProperties": False,
        },
    },
}

_generation_busy_guard = asyncio.Lock()
_generation_busy_user_ids: set[str] = set()


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

    if len(update.message.text) > 800:
        await update.message.reply_text(
            f"Oops! 😅 Your message is a bit too long (over 800 characters).\n\n"
            f"Please keep it under 800 characters and try again 💦\n"
            f"(Tip: Focus on key details like character, pose, style, and vibe!)")
        return

    if is_rate_limited(user_id):
        await update.message.reply_text(
            f"Whoa there, slow down a bit! 😏🔥\n\n"
            f"You're sending requests too fast — let's take a quick breath.\n"
            f"Wait just 5-10 seconds and try again 😉\n\n"
            f"I want to give you the best prompts, not rush them! 💦")
        return

    async with async_session_maker() as db:
        flagged_busy_for_user = False

        try:
            user = await get_or_create_user(user_id, db)

            if user.credits <= 0:
                await update.message.reply_text(
                    f"Oops! 😅 You're out of generations.\n\n"
                    f"Get more with /buy or /credits\n\n"
                    f"Ready for more? Just send your fantasy! 💦")
                return

            async with _generation_busy_guard:
                if user_id in _generation_busy_user_ids:
                    await update.message.reply_text(
                        f"Hold on 😉 You already have a prompt generation running.\n\n"
                        f"Wait for it to finish, then send this idea again 💦")
                    return
                _generation_busy_user_ids.add(user_id)
                flagged_busy_for_user = True

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
                f"Copy it below and paste into your favorite model (Flux, Pony XL, Illustrious, RealVisXL, SDXL, Midjourney, Grok-2 & more) 😉\n\n"
                f"Prompt: ⬇️💦\n")

            await update.message.reply_text(f"{prompt}")

        finally:
            if flagged_busy_for_user:
                async with _generation_busy_guard:
                    _generation_busy_user_ids.discard(user_id)
