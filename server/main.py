# Imports
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import PlainTextResponse, RedirectResponse
from telegram import Update
import stripe

# Bot imports
from bot.bot import app as tg_app, bot
from db.db_ops import add_credits, get_or_create_user
from db.database import async_session_maker, engine
from db.models import Base

# Define tokens
from core.config import (
    STRIPE_LIVE_SECRET_KEY,
    STRIPE_LIVE_WEBHOOK_SECRET,
    PAYMENT_CONTENT,
    PAYMENT_EURO_PRICE,
    PAYMENT_BOT_CREDITS,
    BOT_LINK,
    LEGAL_PAGE_URL,
)
stripe.api_key = STRIPE_LIVE_SECRET_KEY
STRIPE_BOT_METADATA = "Prompt_Generator_Bot"

SITE_HOME_URL = "https://nsfwprompts.app"

# Project initialisation
async def init_telegram():
    await bot.initialize()
    await tg_app.initialize()

@asynccontextmanager
async def lifespan(server: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await init_telegram()
    try:
        yield
    finally:
        await engine.dispose()


# FastAPI server creating
server = FastAPI(lifespan=lifespan)

# FastAPI Endpoints
@server.get("/", include_in_schema=False)
async def root():
    return RedirectResponse(url=SITE_HOME_URL, status_code=302)

@server.get("/terms", include_in_schema=False)
async def terms():
    return RedirectResponse(url=LEGAL_PAGE_URL, status_code=302)

@server.get("/health")
async def health():
    return PlainTextResponse("ok")

@server.post("/create-checkout-session/{user_id}")
async def create_checkout(user_id: str):
    payment_metadata = {
        "bot_name": STRIPE_BOT_METADATA,
        "telegram_user_id": user_id,
        "credits": PAYMENT_BOT_CREDITS
    }

    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[{
            "price_data": {
                "currency": "eur",
                "product_data": {
                    "name": PAYMENT_CONTENT,
                },
                "unit_amount": int(PAYMENT_EURO_PRICE),
            },
            "quantity": 1,
        }],
        mode="payment",
        metadata=payment_metadata,
        # save user information
        payment_intent_data= {
            "metadata": payment_metadata,
        },
        success_url=f"{BOT_LINK}?start=payment_success",
        cancel_url=f"{BOT_LINK}?start=payment_cancel"
    )
    return {"url": session.url}

# Stripe webhook
@server.post("/stripe-webhook")
async def stripe_webhook(request: Request):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(
            payload,
            sig_header,
            STRIPE_LIVE_WEBHOOK_SECRET
        )
    except Exception as e:
        print("STRIPE WEBHOOK ERROR:", e)
        raise HTTPException(status_code=400)

    print("EVENT TYPE:", event["type"])

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]

        payment_intent_id = session.get("payment_intent")
        if not payment_intent_id:
            print("STRIPE WEBHOOK ERROR: NO PAYMENT INTENT")
            return {"status": "ok"}

        pi = stripe.PaymentIntent.retrieve(payment_intent_id)
        metadata = dict(session.get("metadata") or {})
        metadata.update(dict(pi.get("metadata") or {}))

        telegram_user_id = metadata.get("telegram_user_id")
        credits = int(metadata.get("credits", 0))

        print("STRIPE WEBHOOK: PAYMENT OK:", telegram_user_id, credits)

        if not telegram_user_id or credits <= 0:
            print("STRIPE WEBHOOK ERROR: INVALID METADATA")
            return {"status": "ok"}
        
        async with async_session_maker() as db:
            await get_or_create_user(telegram_user_id, db)

            await add_credits(telegram_user_id, credits, db)

    return {"status": "ok"}

# Telegram webhook
@server.post("/tg-webhook")
async def telegram_webhook(request: Request):
    payload = await request.json()
    update = Update.de_json(payload, bot)
    await tg_app.process_update(update)
    return {"ok": True}
