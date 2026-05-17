# Imports
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from telegram import Bot

# Handlers
from bot.handlers.start import start
from bot.handlers.help import help
from bot.handlers.credits import credits
from bot.handlers.buy import buy
from bot.handlers.terms import terms
from bot.handlers.contacts import contacts
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
app.add_handler(CommandHandler("credits", credits))
app.add_handler(CommandHandler("buy", buy))
app.add_handler(CommandHandler("terms", terms))
app.add_handler(CommandHandler("contacts", contacts))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
# (always in the end)
app.add_handler(MessageHandler(filters.COMMAND, unknown))