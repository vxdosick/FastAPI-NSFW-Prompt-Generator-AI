# Imports
import httpx
from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ChatType

# Define tokens
from core.config import SERVER_URL

async def buy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type != ChatType.PRIVATE:
        return
    user_id = str(update.effective_user.id)

    async with httpx.AsyncClient() as client:
        r = await client.post(f"{SERVER_URL}/create-checkout-session/{user_id}")
        data = r.json()
        await update.message.reply_text(
            (
            f"Ready to unlock more spicy generations? 😏🔥\n\n"
            f"One simple purchase — no subscriptions, no hidden fees, no monthly traps.\n"
            f"Everything is transparent and honest 💎\n\n"
            f"For just €1.99 you get 50 full generations!\n"
            f"That's less than a coffee ☕ — but way hotter and more satisfying 😉\n\n"
            f"Pay once → instantly get your 50 generations added.\n"
            f"As simple as that!\n\n"
            f"<a href='{data['url']}'>🛒 Grab 50 generations for €1.99 now!</a>\n\n"
            f"Let's keep the creativity flowing! 💦"
            ),
            parse_mode="HTML",
            disable_web_page_preview=True)