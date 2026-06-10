# NSFW Prompt Generator AI

### Bot name: [@nsfw_prompt_generator_bot](https://t.me/nsfw_prompt_generator_bot)

This bot has an official version on Telegram.

### Functionality / Features

NSFW Prompt Generator AI is an AI-powered assistant designed to generate detailed prompts for adult-oriented image generation models. Key features include:

- AI-powered Prompt Generation – create structured, high-detail prompts based on user descriptions.
- Model Optimization – prompts are optimized for Flux, Pony XL, Illustrious, RealVisXL, SDXL, Midjourney, Grok-2 and other compatible models.
- Unrestricted Creative Input – supports explicit, uncensored prompt construction according to user requests.
- Ready-to-Use Output – generates copy-ready prompts for seamless integration into image generation workflows.
- Fast & Lightweight – simple interface without complex dashboards or unnecessary steps.
- Free Trial Access – new users receive a limited number of free generations to explore functionality.
- This bot streamlines the process of creating high-quality adult prompts, making prompt engineering faster, more accessible, and more efficient for AI image generation platforms.
- Save or delete up to 5 prompts. This limit may be increased in the future.

### Roadmap

**Done**

- 2026-06-10:
    - [x] A “Roadmap” section has been added to `README.md` to track progress and the latest features
    - [x] Implement Maintenance Mode (to temporarily disable the bot)
    - [x] Add a script for quick `Webhook` integration
    - [x] Implement a section to showcase new features and updates (`/whats_new` handler)
    - [x] A new column, `is_blocked`, has been added to the database

**Planned**
- xxxx-xx-xx:
    - [ ] Upgrade the licence for this product
    - [ ] Refine push notifications for different scenarios
    - [ ] Improve the system prompt and make it more straightforward

Keep an eye out for new feature ideas, or send your own suggestions to my Telegram – [@velvetmommy](http://t.me/velvetmommy). I’d be happy to hear any suggestions

### List of bot's comands

1. /start - Getting started
2. /help - Help with usage
3. /balance - Check credits and buy generations ❤️
4. /prompts - View saved prompts 🍓
5. /whats_new - Latest updates and changelog 🚀
6. /terms - Privacy Policy and Refund Policy
7. /contacts - Contact the developer or report a bug 👨‍💻

### Main stack

- Python 3.12.12
- Telegram Bot API (python-telegram-bot)
- FastAPI — REST API layer
- PostgreSQL (Neon) — lightweight database
- SQLAlchemy 2.0 — ORM
- OpenRouter API — AI integration
- Uvicorn — ASGI server
- Render - deployment
- Ngrok - local tunneling for webhook testing
- Stripe - Payment system
- Alembic (For database migrations)

### Useful commands

1. Environment creating

```bash
python -m venv venv
```

1. Install dependencies

```bash
pip install -r requirements.txt
```

1. Copy environment variables from `.env.example` into a new `.env` file in the project root and fill in your values.
2. Run database migrations

```bash
alembic upgrade head
```

1. Start server

- development mode

```bash
uvicorn server.main:server --reload
```

- production mode

```bash
uvicorn server.main:server --host 0.0.0.0 --port 8000
```

1. Ngrok starting (development mode)

```bash
ngrok http 8000
```

1. Preservation of requirements (if they change)

```bash
pip freeze > requirements.txt
```

8. Register Telegram webhook (uses `BOT_TOKEN` and `SERVER_URL` from `.env`)

```bash
python -m core.set_webhook
```

### VERY IMPORTANT

Before using this software, please read the [LICENSE](./LICENSE). Thank you – let’s make life a little bit easier for programmers ❤️

### Product site: [nsfw_prompt_generator_bot](https://ai-prompt-generator-telegram-bot-server.onrender.com)