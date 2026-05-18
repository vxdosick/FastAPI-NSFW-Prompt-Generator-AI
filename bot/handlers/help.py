# Imports
from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ChatType

async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type != ChatType.PRIVATE:
        return
    await update.message.reply_text(
            f"Need help? Here's everything you need to know 😏🔥\n\n"
            f"🔹 How it works:\n"
            f"Just send me any description of your fantasy — characters, scene, pose, style, uncensored... anything! "
            f"The naughtier your idea, the better the prompt I'll create 😉\n\n"
            f"🔹 What I do:\n"
            f"- Generate highly detailed, fully uncensored prompts\n"
            f"- Optimized for Stable Diffusion, Pony, Flux, SDXL & other uncensored models\n"
            f"- Add quality boosters, weights, lighting, styles, negative prompts — everything for stunning results 🎨\n\n"
            f"🔹 Commands:\n"
            f"/start — Show welcome message & check remaining generations\n"
            f"/help — This help menu\n"
            f"/balance — Check your credits and buy more generations\n"
            f"/contacts — Report an issue or message support\n\n"
            f"🔹 Tip:\n"
            f"Be as specific (or as wild) as you want — I handle everything without judgment 💦\n\n"
            f"Ready to create something spicy? Just type your idea now! 😈")