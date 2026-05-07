# Imports
from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ChatType

# DB
from db.db_ops import get_or_create_user
from db.database import SessionLocal

async def credits(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type != ChatType.PRIVATE:
        return
    user_id = str(update.effective_user.id)

    db = SessionLocal()

    try:
        user = get_or_create_user(user_id, db)
    finally:
        db.close()

    await update.message.reply_text(
            f"Your generations status 💎😏\n\n"
            f"Free generations left: {user.credits} 🎁\n\n"
            f"5 free generations for new users🎁\n"
            f"Out of free ones? Go unlimited with /buy 🔥\n\n"
            f"Ready for more? Just send your fantasy! 💦")