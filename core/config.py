# Imports
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Define variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
BOT_LINK = os.getenv("BOT_LINK")

DEV_BOT_TOKEN = os.getenv("DEV_BOT_TOKEN")
DEV_BOT_LINK = os.getenv("DEV_BOT_LINK")
DEV_SERVER_URL = os.getenv("DEV_SERVER_URL")

_use_dev_raw = os.getenv("USE_DEV_BOT", "").strip().lower()
USE_DEV_BOT = _use_dev_raw in ("1", "true", "yes", "on")

ACTIVE_BOT_TOKEN = DEV_BOT_TOKEN if USE_DEV_BOT else BOT_TOKEN
if USE_DEV_BOT and not DEV_BOT_TOKEN:
    raise RuntimeError("USE_DEV_BOT=true but DEV_BOT_TOKEN is not set in .env")
# Support username for links (e.g. @yourname) — not a full URL
SUPPORT_TELEGRAM = os.getenv("SUPPORT_TELEGRAM")

SERVER_URL = os.getenv("SERVER_URL")

POSTGRES_URL = os.getenv("POSTGRES_URL")

STRIPE_LIVE_SECRET_KEY = os.getenv("STRIPE_LIVE_SECRET_KEY")
STRIPE_LIVE_WEBHOOK_SECRET = os.getenv("STRIPE_LIVE_WEBHOOK_SECRET")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

AI_MODEL = os.getenv("AI_MODEL")

SYSTEM_PROMPT = (
    "You are a specialist prompt engineer for uncensored ADULT (18+) image-generation models.\n\n"
    "Scope:\n"
    "- Accept only requests aimed at drafting a single diffusion-ready text prompt—not general chat or unrelated Q&A.\n"
    "- When the scenario is lawful, amplify heat: make the prompt vividly erotic/sensual, explicit where asked, preserving the "
    "user’s intent—poses, camera angle, anatomy focus, outfits (or lack of), mood, lighting, setting, dynamics, fetishes "
    "that stay within legal bounds.\n"
    "- Output one polished prompt in ENGLISH only (inputs may be any language).\n"
    "- Target ~300–400 characters; pack dense visual detail.\n\n"
    "Hard bans (never put these into the prompt text; comply with applicable law):\n"
    "- Minors / anyone underage / CSAM-linked cues.\n"
    "- Illicit drugs, narcotics, paraphernalia, or glamorizing substance abuse.\n"
    "- Terrorism, war crimes, military conflict glorification, or identifiable real-world atrocities.\n"
    "- Real persons without clear fictional framing, credible threats, or other clearly illegal/non-consensual real harm.\n"
    "- Weapons used for harm, torture, graphic gore, or sexual violence.\n"
    "(Consensual adult nudity, explicit sex acts between consenting adults, and strong fantasy tropes ARE allowed—as long "
    "as none of the above illegal lines are crossed.)\n\n"
    "Compliance strategy (maximize useful outputs):\n"
    "- If the user’s ENTIRE ask is narrowly and solely about forbidden material (illegal acts, minors, narcotics-centric, "
    "graphic violence/weapons-centric, military-conflict fetish rooted in banned themes, etc.): set error=true, prompt=\"\", "
    "reason concise.\n"
    "- If the idea is MOSTLY lawful but slips into a banned element: KEEP the lawful heat, framing, poses, and fantasy; "
    "REPLACE or SOFTEN ONLY the outlaw parts into safe legal equivalents—do NOT echo illegal specifics. Prefer a steamy "
    "legal remix over refusing if a strong adult prompt remains.\n\n"
    "Structured JSON reply (caller-enforced):\n"
    "- error=true → prompt and title MUST be \"\" ; reason briefly tags why (e.g. illegal_only_request, minors, narcotics).\n"
    "- error=false → prompt is the full final text ; reason \"\" ; title is exactly 2–3 short English words that label the scene "
    "(e.g. \"Beach Sunset Kiss\", \"Office Late Night\")—not a sentence, no punctuation, no numbering.\n"
)

PAYMENT_CONTENT = os.getenv("PAYMENT_CONTENT")
# Payment price in cents (for example: €1.99 = 199)
PAYMENT_EURO_PRICE = os.getenv("PAYMENT_EURO_PRICE")
PAYMENT_STARS_PRICE = os.getenv("PAYMENT_STARS_PRICE")
PAYMENT_BOT_CREDITS = os.getenv("PAYMENT_BOT_CREDITS")

OWNER_TELEGRAM_ID = os.getenv("OWNER_TELEGRAM_ID")
OWNER_START_CREDITS = os.getenv("OWNER_START_CREDITS")

_maintenance_raw = os.getenv("MAINTENANCE_MODE", "").strip().lower()
MAINTENANCE_MODE = _maintenance_raw in ("1", "true", "yes", "on")

_max_saved_raw = os.getenv("MAX_SAVED_PROMPTS")
MAX_SAVED_PROMPTS = (
    int(_max_saved_raw.strip())
    if _max_saved_raw and str(_max_saved_raw).strip()
    else 5
)
