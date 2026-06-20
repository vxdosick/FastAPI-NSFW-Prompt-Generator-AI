"""Per-model slash commands — /ponyxl, /fluxedup, etc."""

from telegram import Update
from telegram.ext import ContextTypes

from bot.handlers.generation import run_prompt_generation
from core.model_guidelines import resolve_command_slug


async def model_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.effective_message
    if not message or not message.text:
        return

    command = message.text.split()[0].lstrip("/")
    slug = resolve_command_slug(command)
    if slug is None:
        return

    parts = message.text.split(None, 1)
    scene = parts[1].strip() if len(parts) > 1 else ""
    await run_prompt_generation(update, context, scene, model_slug=slug)
