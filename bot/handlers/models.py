"""List supported model commands."""

from telegram import Update
from telegram.ext import ContextTypes

from core.model_guidelines import models_help_lines


def models_help_text() -> str:
    lines = models_help_lines()
    return (
        "Pick a model, love — then your scene on the same line 💕\n\n"
        "Example:\n"
        "<code>/ponyxl cyberpunk succubus, neon rain, 8k</code>\n\n"
        "Or send any scene without a command for a <b>general prompt</b>.\n\n"
        + "\n".join(lines)
    )


async def models(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(models_help_text(), parse_mode="HTML")
