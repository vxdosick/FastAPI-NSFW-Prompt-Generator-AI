# Imports
from telegram import Bot, Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    ChatMemberHandler,
    CommandHandler,
    MessageHandler,
    PreCheckoutQueryHandler,
    TypeHandler,
    filters,
)

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
from bot.handlers.whats_new import whats_new
from bot.handlers.prompts import (
    PROMPTS_CALLBACK_PREFIX,
    SAVE_PROMPT_CALLBACK_PREFIX,
    prompts,
    prompts_callback,
    save_prompt_callback,
)
from bot.handlers.chat_member import my_chat_member
from bot.handlers.echo import echo, GUEST_TEXT
from bot.handlers.unknown import unknown
from bot.utils.maintenance import maintenance_gate

# Define tokens
from core.config import ACTIVE_BOT_TOKEN, USE_DEV_BOT

# TB App creating
bot = Bot(ACTIVE_BOT_TOKEN)
app = Application.builder().token(ACTIVE_BOT_TOKEN).concurrent_updates(True).build()

if USE_DEV_BOT:
    print("USE_DEV_BOT=true — running with DEV_BOT_TOKEN")

# Maintenance gate (group -1 runs before all other handlers)
app.add_handler(TypeHandler(Update, maintenance_gate), group=-1)

# Define TB handlers
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("help", help))
app.add_handler(CommandHandler("balance", balance))
app.add_handler(CommandHandler("terms", terms))
app.add_handler(CommandHandler("contacts", contacts))
app.add_handler(CommandHandler("prompts", prompts))
app.add_handler(CommandHandler("whats_new", whats_new))
app.add_handler(ChatMemberHandler(my_chat_member, ChatMemberHandler.MY_CHAT_MEMBER))
app.add_handler(CallbackQueryHandler(stars_payment, pattern=f"^{STARS_CALLBACK_DATA}$"))
app.add_handler(CallbackQueryHandler(save_prompt_callback, pattern=f"^{SAVE_PROMPT_CALLBACK_PREFIX}:"))
app.add_handler(CallbackQueryHandler(prompts_callback, pattern=f"^{PROMPTS_CALLBACK_PREFIX}:"))
app.add_handler(PreCheckoutQueryHandler(stars_pre_checkout))
app.add_handler(MessageHandler(filters.SUCCESSFUL_PAYMENT, stars_successful_payment))
app.add_handler(MessageHandler(GUEST_TEXT, echo))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND & ~GUEST_TEXT, echo))
# (always in the end)
app.add_handler(MessageHandler(filters.COMMAND, unknown))