# NSFW Prompt Generator AI
### Bot name: @nsfw_prompt_generator_bot
### [LINK](https://t.me/nsfw_prompt_generator_bot)

This bot has an official version running via Render.com

### Functionality / Features
NSFW Prompt Generator AI is an AI-powered assistant designed to generate detailed prompts for adult-oriented image generation models. Key features include:

* AI-powered Prompt Generation – create structured, high-detail prompts based on user descriptions.
* Model Optimization – prompts are optimized for Flux, Pony XL, Illustrious, RealVisXL, SDXL, Midjourney, Grok-2 and other compatible models.
* Unrestricted Creative Input – supports explicit, uncensored prompt construction according to user requests.
* Ready-to-Use Output – generates copy-ready prompts for seamless integration into image generation workflows.
* Fast & Lightweight – simple interface without complex dashboards or unnecessary steps.
* Free Trial Access – new users receive a limited number of free generations to explore functionality.
* This bot streamlines the process of creating high-quality adult prompts, making prompt engineering faster, more accessible, and more efficient for AI image generation platforms.

### List of bot's comands
1. /start - Getting started
2. /help - Help with usage
3. /credits - Number of generations
4. /buy - Buy generation ❤️
5. /terms - Privacy Policy and Refund Policy

### Main stack
- Python 3.12.12
- Telegram Bot API (python-telegram-bot)
- FastAPI — REST API layer
- SQLite — lightweight database
- SQLAlchemy 2.0 — ORM
- OpenRouter API — AI integration
- Uvicorn — ASGI server
- Render - deployment
- Ngrok - local tunneling for webhook testing
- Stripe - Payment system

### Useful commands
0. Environment creating
```bash
python -m venv venv
```
1. Install dependencies
```bash
pip install -r requirements.txt
```
2. Create .env file in root direction and write inside:
```bash
BOT_TOKEN=telegram bot token
BOT_LINK=https://t.me/bot_name

SERVER_URL=link from Render.com (production mode)

STRIPE_LIVE_SECRET_KEY=stripe live secret key
STRIPE_LIVE_WEBHOOK_SECRET=stripe live webhook secret

OPENAI_API_KEY=openrouter api key
AI_MODEL=ai model (for examle: x-ai/grok-4-fast)

PAYMENT_CONTENT=name of payment (for examle: 50 Generations 🤗)
PAYMENT_EURO_PRICE=price in eur (for examle: 199) (in cents)
PAYMENT_BOT_CREDITS=adding credits (for example: 50)

OWNER_TELEGRAM_ID=your telegram id
OWNER_START_CREDITS=number of credits for the developer (for example: 10,000)
```
3. Start server
- development mode
```bash
uvicorn server.main:server --reload
```
- production mode
```bash
uvicorn server.main:server --host 0.0.0.0 --port 8000
```
4. Ngrok starting (development mode)
```bash
ngrok http 8000
```
5. Preservation of requirements (if they change)
```bash
pip freeze > requirements.txt
```
6. Webhook - Telegram Initialisation
```bash
curl -F "url=(APP_URL)/tg-webhook" https://api.telegram.org/bot(BOT_TOKEN)/setWebhook
```

### VERY IMPORTANT
Before using this software, please read the [LICENSE](./LICENSE). Thank you – let’s make life a little bit easier for programmers ❤️