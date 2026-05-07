# Imports
from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ChatType

async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type != ChatType.PRIVATE:
        return
    
    await update.message.reply_text(
        f"Oops! 😅 That command doesn't exist yet.\n\n"
        f"Try one of these:\n"
        f"/start — Welcome message & generations info\n"
        f"/help — How to use me\n"
        f"/credits — Check free generations left\n"
        f"/buy — Get more generations (€1.99 for 30)\n\n"
        f"/terms — Terms & Policies\n\n"
        f"Or just describe your fantasy — I'll create a hot prompt right away! 🔥💦")