# Imports
import html
import secrets

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.error import BadRequest
from telegram.ext import ContextTypes

# Config
from core.config import MAX_SAVED_PROMPTS

# DB
from db.db_ops import delete_saved_prompt, get_saved_prompts, save_prompt
from db.database import async_session_maker

SAVE_PROMPT_CALLBACK_PREFIX = "save_prompt"
SAVE_START_PREFIX = "save_"
PROMPTS_CALLBACK_PREFIX = "prompts"

_prompt_save_cache: dict[str, dict[str, str]] = {}

_EMPTY_PROMPTS_TEXT = (
    "Nothing saved yet, love 🍓\n\n"
    "Generate something hot and tap Save under it 💕"
)


def cache_prompt_token(prompt: str, title: str = "") -> str:
    token = secrets.token_urlsafe(8)
    _prompt_save_cache[token] = {"prompt": prompt, "title": title}
    return token


def cache_prompt_for_saving(prompt: str, title: str = "") -> str:
    token = cache_prompt_token(prompt, title)
    return f"{SAVE_PROMPT_CALLBACK_PREFIX}:{token}"


async def save_prompt_from_token(user_id: str, token: str) -> tuple[str | None, str]:
    """Returns (saved_title, status) where status is saved | full | expired."""
    cached = _prompt_save_cache.get(token)
    if not cached:
        return None, "expired"

    prompt = cached.get("prompt", "")
    title = cached.get("title", "")

    async with async_session_maker() as db:
        was_saved, saved_prompts = await save_prompt(user_id, prompt, title, db)

    if not was_saved:
        return None, "full"

    _prompt_save_cache.pop(token, None)
    saved_title = saved_prompts[-1].get("title", "Prompt") if saved_prompts else "Prompt"
    return saved_title, "saved"


def _format_prompt_message(item: dict, position: int, total: int) -> str:
    title = html.escape(str(item.get("title", "Prompt")))
    prompt_text = html.escape(str(item.get("prompt", "")))
    return (
        f"Saved prompts 🍓 · up to {MAX_SAVED_PROMPTS}\n\n"
        f"<b>{title}</b> ({position + 1}/{total})\n\n"
        f"<code>{prompt_text}</code>\n\n"
        f"Tap to copy ⬆️"
    )


def _prompt_keyboard(position: int, total: int) -> InlineKeyboardMarkup:
    delete_row = [
        InlineKeyboardButton(
            "Delete prompt ❌",
            callback_data=f"{PROMPTS_CALLBACK_PREFIX}:del:{position}",
        )
    ]
    if total <= 1:
        return InlineKeyboardMarkup([delete_row])

    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "⬅️",
                    callback_data=f"{PROMPTS_CALLBACK_PREFIX}:prev:{position}",
                ),
                InlineKeyboardButton(
                    "➡️",
                    callback_data=f"{PROMPTS_CALLBACK_PREFIX}:next:{position}",
                ),
            ],
            delete_row,
        ]
    )


def _wrap_index(position: int, total: int, delta: int) -> int:
    return (position + delta) % total


async def _edit_prompt_view(message, item: dict, position: int, total: int) -> None:
    text = _format_prompt_message(item, position, total)
    markup = _prompt_keyboard(position, total)
    try:
        await message.edit_text(text, parse_mode="HTML", reply_markup=markup)
    except BadRequest:
        await message.edit_reply_markup(reply_markup=markup)


async def prompts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)

    async with async_session_maker() as db:
        saved_prompts = await get_saved_prompts(user_id, db)

    if not saved_prompts:
        await update.message.reply_text(_EMPTY_PROMPTS_TEXT)
        return

    position = len(saved_prompts) - 1
    item = saved_prompts[position]
    await update.message.reply_text(
        _format_prompt_message(item, position, len(saved_prompts)),
        parse_mode="HTML",
        reply_markup=_prompt_keyboard(position, len(saved_prompts)),
    )


async def prompts_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not query or not query.message:
        return

    parts = (query.data or "").split(":")
    if len(parts) != 3 or parts[0] != PROMPTS_CALLBACK_PREFIX:
        return

    action = parts[1]
    try:
        position = int(parts[2])
    except ValueError:
        await query.answer()
        return

    user_id = str(query.from_user.id)

    async with async_session_maker() as db:
        saved_prompts = await get_saved_prompts(user_id, db)

        if not saved_prompts:
            await query.answer("Nothing left to show, love 🍓", show_alert=True)
            try:
                await query.message.edit_text(_EMPTY_PROMPTS_TEXT, reply_markup=None)
            except BadRequest:
                pass
            return

        if position < 0 or position >= len(saved_prompts):
            position = len(saved_prompts) - 1

        if action == "prev":
            new_position = _wrap_index(position, len(saved_prompts), -1)
            await query.answer()
            await _edit_prompt_view(
                query.message,
                saved_prompts[new_position],
                new_position,
                len(saved_prompts),
            )
            return

        if action == "next":
            new_position = _wrap_index(position, len(saved_prompts), 1)
            await query.answer()
            await _edit_prompt_view(
                query.message,
                saved_prompts[new_position],
                new_position,
                len(saved_prompts),
            )
            return

        if action == "del":
            _, remaining = await delete_saved_prompt(user_id, position, db)

            if not remaining:
                await query.answer("Prompt deleted 🗑", show_alert=False)
                try:
                    await query.message.edit_text(_EMPTY_PROMPTS_TEXT, reply_markup=None)
                except BadRequest:
                    pass
                return

            new_position = min(position, len(remaining) - 1)
            await query.answer("Prompt deleted 🗑", show_alert=False)
            await _edit_prompt_view(
                query.message,
                remaining[new_position],
                new_position,
                len(remaining),
            )


async def save_prompt_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not query or not query.message:
        return

    _, _, token = (query.data or "").partition(":")
    user_id = str(query.from_user.id)
    saved_title, status = await save_prompt_from_token(user_id, token)

    if status == "expired":
        await query.answer()
        await query.message.reply_text(
            "That one's gone, love — generate it again 🔄"
        )
        return

    if status == "full":
        await query.answer()
        await query.message.reply_text(
            f"Only {MAX_SAVED_PROMPTS} spots, love 🍓\n"
            f"Open /prompts to make room 💕"
        )
        return

    await query.answer("Prompt saved 🍓", show_alert=False)
    await query.message.reply_text(
        f"Saved as {html.escape(saved_title)} ✅\n"
        f"/prompts whenever you want it back 💕",
        parse_mode="HTML",
    )
