# Shared prompt generation pipeline (credits, OpenRouter, replies).

from __future__ import annotations

import asyncio
import html
import json
import re

from openai import OpenAI
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.constants import ChatAction
from telegram.ext import ContextTypes

from bot.handlers.balance import build_payment_keyboard
from bot.handlers.prompts import cache_prompt_token, SAVE_START_PREFIX
from bot.utils.guest_reply import active_bot_link, bot_start_url, send_reply_message
from bot.utils.is_rate_limited import is_rate_limited
from core.config import AI_MODEL, OPENAI_API_KEY
from core.model_guidelines import get_model_display_name, resolve_command_slug
from core.prompt_builder import build_system_prompt
from core.prompt_schema import PROMPT_RESPONSE_FORMAT
from core.supported_models import supported_models_phrase
from db.db_ops import get_or_create_user
from db.database import async_session_maker

_BUSY_LOCK = asyncio.Lock()
_BUSY_STATE: dict[str, dict] = {}

_BUSY_PLEASE_WAIT = (
    "One sec, love... still on your last one 💕\n"
    "Send the next idea when it's done 😊"
)

_GENERAL_HEADER = "<b>General prompt</b> 😏💕"


def parse_model_invocation(text: str) -> tuple[str, str] | None:
    stripped = text.strip()
    if not stripped.startswith("/"):
        return None

    parts = stripped.split(None, 1)
    command = parts[0].lstrip("/")
    slug = resolve_command_slug(command)
    if slug is None:
        return None

    scene = parts[1].strip() if len(parts) > 1 else ""
    return slug, scene


async def _acquire_or_report_busy(user_id: str) -> str:
    async with _BUSY_LOCK:
        state = _BUSY_STATE.get(user_id)
        if state is None:
            _BUSY_STATE[user_id] = {"warned": False}
            return "acquired"
        if not state["warned"]:
            state["warned"] = True
            return "warn_now"
        return "silent"


async def _release_busy(user_id: str) -> None:
    async with _BUSY_LOCK:
        _BUSY_STATE.pop(user_id, None)


async def _repeat_typing(context: ContextTypes.DEFAULT_TYPE, chat_id: int) -> None:
    try:
        while True:
            await context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
            await asyncio.sleep(4.5)
    except asyncio.CancelledError:
        return


def _prompt_reply_markup(
    message,
    prompt: str,
    title: str,
    negative_prompt: str = "",
) -> InlineKeyboardMarkup:
    token = cache_prompt_token(prompt, title, negative_prompt)
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
        rows.append([InlineKeyboardButton("Open me privately 💕", url=bot_link)])
    return InlineKeyboardMarkup(rows)


def _format_generation_message(
    model_slug: str | None,
    prompt: str,
    negative_prompt: str,
    save_hint: str,
) -> str:
    if model_slug:
        header = f"<b>{html.escape(get_model_display_name(model_slug))}</b> 😏💕"
    else:
        header = _GENERAL_HEADER

    body = (
        f"{header}\n\n"
        f"<b>Positive</b>\n"
        f"<code>{html.escape(prompt)}</code>"
    )

    negative = negative_prompt.strip()
    if negative:
        body += f"\n\n<b>Negative</b>\n<code>{html.escape(negative)}</code>"
    else:
        body += "\n\n<b>Negative</b>\n<i>(none needed for this target)</i>"

    body += (
        f"\n\nCopy & paste into {supported_models_phrase()} 🔥"
        f"{save_hint}"
    )
    return body


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


async def run_prompt_generation(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    scene_text: str,
    *,
    model_slug: str | None,
) -> None:
    message = update.effective_message
    if not message:
        return

    user = update.effective_user
    if not user:
        return

    user_id = str(user.id)
    prompt_text = scene_text.strip()
    if not prompt_text:
        if model_slug:
            cmd = model_slug
            name = get_model_display_name(model_slug)
            await send_reply_message(
                message,
                context,
                f"Tell me the scene for {name}, love 💕\n"
                f"Example:\n<code>/{cmd} sunset beach, red dress, soft golden light</code>",
                parse_mode="HTML",
            )
        else:
            await send_reply_message(
                message,
                context,
                "Tell me what to paint, love 💕\n"
                "Scene, mood, outfit — I'll turn it into a prompt 🔥\n\n"
                "Or pick a model: /models",
            )
        return

    status = await _acquire_or_report_busy(user_id)
    if status == "warn_now":
        await send_reply_message(message, context, _BUSY_PLEASE_WAIT)
        return
    if status == "silent":
        return

    typing_chat_id = (
        message.guest_bot_caller_chat.id
        if message.guest_bot_caller_chat
        else message.chat_id
    )

    try:
        if len(prompt_text) > 800:
            await send_reply_message(
                message,
                context,
                "That's a lot at once, love 😅\n"
                "Keep it under 800 chars — scene, pose, mood — then send again 💕",
            )
            return

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

            system_prompt = build_system_prompt(model_slug)
            client = OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=OPENAI_API_KEY,
            )

            def _call_openrouter():
                return client.chat.completions.create(
                    extra_body={},
                    model=AI_MODEL,
                    messages=[
                        {"role": "system", "content": system_prompt},
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
            negative_prompt = (data.get("negative_prompt") or "").strip()
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

            reply_text = _format_generation_message(
                model_slug,
                prompt,
                negative_prompt,
                save_hint,
            )

            await send_reply_message(
                message,
                context,
                reply_text,
                parse_mode="HTML",
                reply_markup=_prompt_reply_markup(
                    message,
                    prompt,
                    title,
                    negative_prompt,
                ),
            )

    finally:
        await _release_busy(user_id)


def strip_bot_mention(text: str, bot_username: str | None) -> str:
    cleaned = text.strip()
    if not bot_username:
        return cleaned
    pattern = rf"@?{re.escape(bot_username)}\s*"
    return re.sub(pattern, "", cleaned, flags=re.IGNORECASE).strip()
