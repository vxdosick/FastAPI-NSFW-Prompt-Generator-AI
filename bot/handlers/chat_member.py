from telegram import Update
from telegram.constants import ChatMemberStatus
from telegram.ext import ContextTypes

from db.db_ops import set_user_blocked
from db.database import async_session_maker


async def my_chat_member(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    event = update.my_chat_member
    if event is None:
        return

    telegram_id = str(event.from_user.id)
    status = event.new_chat_member.status

    if status == ChatMemberStatus.KICKED:
        is_blocked = True
    elif status == ChatMemberStatus.MEMBER:
        is_blocked = False
    else:
        return

    async with async_session_maker() as db:
        await set_user_blocked(telegram_id, is_blocked, db)
