# NSFW Prompt Generator AI
### Bot name: [@nsfw_prompt_generator_bot](https://t.me/nsfw_prompt_generator_bot)

This bot has an official version.

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
3. /balance - Check credits and buy generations ❤️
4. /terms - Privacy Policy and Refund Policy
5. /contacts - Contact the developer or report a bug 👨‍💻

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

### Useful commands
0. Environment creating
```bash
python -m venv venv
```
1. Install dependencies
```bash
pip install -r requirements.txt
```
2. Copy environment variables from `.env.example` into a new `.env` file in the project root and fill in your values.
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
curl -F "url=(SERVER_URL)/tg-webhook" https://api.telegram.org/bot(BOT_TOKEN)/setWebhook
```

### VERY IMPORTANT
Before using this software, please read the [LICENSE](./LICENSE). Thank you – let’s make life a little bit easier for programmers ❤️