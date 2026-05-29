# Imports
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    MessageHandler,
    PreCheckoutQueryHandler,
    filters,
)
from telegram import Bot

# Handlers
from bot.handlers.start import start
from bot.handlers.help import help
from bot.handlers.balance import (
    STARS_CALLBACK_DATA,
    balance,
    stars_payment,
    stars_pre_checkout,
    stars_successful_payment,
)
from bot.handlers.terms import terms
from bot.handlers.contacts import contacts
from bot.handlers.prompts import (
    PROMPTS_CALLBACK_PREFIX,
    SAVE_PROMPT_CALLBACK_PREFIX,
    prompts,
    prompts_callback,
    save_prompt_callback,
)
from bot.handlers.echo import echo
from bot.handlers.unknown import unknown

# Define tokens
from core.config import BOT_TOKEN

# TB App creating
bot = Bot(BOT_TOKEN)
app = Application.builder().token(BOT_TOKEN).concurrent_updates(True).build()

# Define TB handlers
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("help", help))
app.add_handler(CommandHandler("balance", balance))
app.add_handler(CommandHandler("terms", terms))
app.add_handler(CommandHandler("contacts", contacts))
app.add_handler(CommandHandler("prompts", prompts))
app.add_handler(CallbackQueryHandler(stars_payment, pattern=f"^{STARS_CALLBACK_DATA}$"))
app.add_handler(CallbackQueryHandler(save_prompt_callback, pattern=f"^{SAVE_PROMPT_CALLBACK_PREFIX}:"))
app.add_handler(CallbackQueryHandler(prompts_callback, pattern=f"^{PROMPTS_CALLBACK_PREFIX}:"))
app.add_handler(PreCheckoutQueryHandler(stars_pre_checkout))
app.add_handler(MessageHandler(filters.SUCCESSFUL_PAYMENT, stars_successful_payment))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
# (always in the end)
app.add_handler(MessageHandler(filters.COMMAND, unknown))