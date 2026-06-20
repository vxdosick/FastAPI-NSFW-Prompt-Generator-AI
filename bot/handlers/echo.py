# Imports
from telegram import Update
from telegram.ext import ContextTypes, filters

from bot.handlers.guest_commands import try_handle_guest_command
from bot.handlers.generation import (
    parse_model_invocation,
    run_prompt_generation,
    strip_bot_mention,
)


class GuestTextFilter(filters.MessageFilter):

    def filter(self, message):
        return bool(message.guest_query_id and message.text)


GUEST_TEXT = GuestTextFilter()


async def _bot_username(context: ContextTypes.DEFAULT_TYPE) -> str | None:
    cached = context.bot_data.get("bot_username")
    if cached:
        return cached
    me = await context.bot.get_me()
    username = (me.username or "").strip() or None
    if username:
        context.bot_data["bot_username"] = username
    return username


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.effective_message
    if not message or not message.text:
        return

    user = update.effective_user
    if not user:
        return

    user_id = str(user.id)
    prompt_text = strip_bot_mention(message.text, await _bot_username(context))

    if not prompt_text:
        await run_prompt_generation(update, context, "", model_slug=None)
        return

    if message.guest_query_id and await try_handle_guest_command(
        message, context, user_id, prompt_text
    ):
        return

    model_invocation = parse_model_invocation(prompt_text)
    if model_invocation:
        slug, scene = model_invocation
        await run_prompt_generation(update, context, scene, model_slug=slug)
        return

    await run_prompt_generation(update, context, prompt_text, model_slug=None)
