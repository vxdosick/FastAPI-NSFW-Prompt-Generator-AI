# Imports
from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ChatType

# DB
from db.db_ops import get_or_create_user
from db.database import async_session_maker

async def credits(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type != ChatType.PRIVATE:
        return
    user_id = str(update.effective_user.id)

    async with async_session_maker() as db:
        user = await get_or_create_user(user_id, db)

    await update.message.reply_text(
            f"Your generations status 💎😏\n\n"
            f"Free generations left: {user.credits} 🎁\n\n"
            f"5 free generations for new users🎁\n"
            f"Out of free ones? Go unlimited with /buy 🔥\n\n"
            f"Ready for more? Just send your fantasy! 💦")
