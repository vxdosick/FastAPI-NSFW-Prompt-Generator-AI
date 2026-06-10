# Imports
import subprocess
import sys

from core.config import BOT_TOKEN, SERVER_URL


def main() -> None:
    if not BOT_TOKEN or not SERVER_URL:
        print("BOT_TOKEN and SERVER_URL must be set in .env", file=sys.stderr)
        sys.exit(1)

    webhook_url = f"{SERVER_URL.strip().rstrip('/')}/tg-webhook"
    api_url = f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook"

    result = subprocess.run(
        [
            "curl",
            "-F",
            f"url={webhook_url}",
            "-F",
            'allowed_updates=["message","my_chat_member"]',
            api_url,
        ],
        capture_output=True,
        text=True,
    )
    if result.stdout:
        print(result.stdout, end="")
    if result.stderr:
        print(result.stderr, end="", file=sys.stderr)
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()