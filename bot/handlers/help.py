# Imports
from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ChatType

async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type != ChatType.PRIVATE:
        return
    await update.message.reply_text(
        f"Little cheat sheet for you 💕\n\n"
        f"Send any spicy scene — I'll craft a detailed uncensored prompt 🔥\n\n"
        f"/start — hello & credits\n"
        f"/help — this menu\n"
        f"/balance — credits & top-up ❤️\n"
        f"/prompts — saved prompts 🍓\n"
        f"/whats_new — what's new 🚀\n"
        f"/contacts — reach me\n\n"
        f"Go on, love... describe something wicked 😉"
    )
