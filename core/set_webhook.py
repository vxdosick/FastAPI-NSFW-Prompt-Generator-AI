from __future__ import annotations

import json
import sys

import httpx

from core.config import BOT_TOKEN, SERVER_URL

ALLOWED_UPDATES = [
    "message",
    "guest_message",
    "callback_query",
    "pre_checkout_query",
    "my_chat_member",
]


def webhook_url() -> str:
    return f"{SERVER_URL.strip().rstrip('/')}/tg-webhook"


def set_webhook() -> dict:
    if not BOT_TOKEN or not SERVER_URL:
        raise RuntimeError("BOT_TOKEN and SERVER_URL must be set in .env")

    api_url = f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook"
    payload = {
        "url": webhook_url(),
        "allowed_updates": json.dumps(ALLOWED_UPDATES),
    }

    with httpx.Client(timeout=30) as client:
        response = client.post(api_url, data=payload)
        response.raise_for_status()
        return response.json()


def main() -> None:
    try:
        data = set_webhook()
    except RuntimeError as exc:
        print(exc, file=sys.stderr)
        sys.exit(1)
    except httpx.HTTPError as exc:
        print(f"setWebhook failed: {exc}", file=sys.stderr)
        sys.exit(1)

    print(json.dumps(data, indent=2))
    if not data.get("ok"):
        sys.exit(1)


if __name__ == "__main__":
    main()
