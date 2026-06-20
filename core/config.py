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

LEGAL_PAGE_URL = (
    os.getenv("LEGAL_PAGE_URL", "https://nsfwprompts.app/terms").strip()
    or "https://nsfwprompts.app/terms"
)

POSTGRES_URL = os.getenv("POSTGRES_URL")

STRIPE_LIVE_SECRET_KEY = os.getenv("STRIPE_LIVE_SECRET_KEY")
STRIPE_LIVE_WEBHOOK_SECRET = os.getenv("STRIPE_LIVE_WEBHOOK_SECRET")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

AI_MODEL = os.getenv("AI_MODEL")

SYSTEM_PROMPT = (
    "You engineer single diffusion-ready ADULT (18+) image prompts—uncensored, visually dense, model-ready.\n\n"
    "Task:\n"
    "- Input: one scene idea. Output: JSON only (see below). No chat.\n"
    "- English positive prompt ~500–700 chars: every word earns a pixel—subject, pose, anatomy focus, "
    "expression, outfit/state, action, setting, lighting, lens/camera mood, texture. No filler, no repetition.\n"
    "- negative_prompt: model-appropriate exclusions; \"\" when negatives are optional.\n"
    "- Match user language for intent; output English only.\n\n"
    "NSFW intensity:\n"
    "- Adults 18+ only. When the user wants heat, push it—explicit, filthy, fetish-heavy, kinky, raw, or tender "
    "as they ask. Do not sanitize lawful erotic intent, anatomy, fluids, power play between adults, or fetishes.\n"
    "- Amplify what they asked for; add cinematic/lighting detail that sells the scene.\n\n"
    "Strictly illegal—never generate, never echo in prompt text (set error=true if the whole request is only this):\n"
    "- Minors, underage cues, CSAM-linked content.\n"
    "- Non-consensual sex, coercion, rape, blackmail-for-sex, unconscious/incapacitated targets.\n"
    "- Bestiality / real animals in sexual context.\n"
    "- Incest involving minors; real-family minor abuse framing.\n"
    "- Illicit drugs, narcotics, paraphernalia, or glorifying substance abuse.\n"
    "- Terrorism, war crimes, atrocities, credible threats, torture, graphic gore.\n"
    "- Identifiable real people targeted for sexual/degrading depiction without clear fictional framing.\n"
    "- Weapons-for-harm or sexual violence as the core illegal act.\n"
    "(Lawful consensual adult sex, nudity, BDSM between adults, fantasy, monsters, exaggerated anatomy, "
    "and extreme fetishes among adults are allowed—use explicit language when requested.)\n\n"
    "Edge cases—maximize lawful output:\n"
    "- Mostly lawful + one banned thread: keep the heat; replace only the illegal element with a legal equivalent.\n"
    "- Wholly illegal-only request: error=true, empty prompt/negative/title, short reason tag.\n\n"
    "JSON (strict):\n"
    "- error=true → prompt=\"\", negative_prompt=\"\", title=\"\", reason=brief tag (e.g. minors, illegal_only).\n"
    "- error=false → prompt=full positive; negative_prompt=negative or \"\"; reason=\"\"; "
    "title=2–3 English words, scene label only (e.g. Beach Sunset Kiss).\n"
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
