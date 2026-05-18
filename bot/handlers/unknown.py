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
        f"/balance — Check credits and buy more generations\n"
        f"/contacts — Support & bug reports\n\n"
        f"/terms — Terms & Policies\n\n"
        f"Or just describe your fantasy — I'll create a hot prompt right away! 🔥💦")