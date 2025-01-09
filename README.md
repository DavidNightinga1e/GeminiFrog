# Gemini Frog
## Telegram bot that acts as a client for Google AI Gemini

# Setup

## Local 
For debugging or other purposes you can just run bot locally on your machine:
1. Clone the repository
2. Create venv if you are into it
3. Run `python -m pip install -r requirements.txt`
4. Create file `.env` with contains from **.env file paragraph**
5. Run `python app.py`

## Docker
1. Clone the repository
2. Create file `.env` with contains from **.env file paragraph**
3. Run `docker compose up --build` or `docker compose up --build -d`

## .env file
BOT_TOKEN is provided by BotFather [(docs)](https://core.telegram.org/bots/tutorial#obtain-your-bot-token)<br>
API_KEY is provided by Google AI Studio [(docs)](https://ai.google.dev/gemini-api/docs/api-key)<br>
PASS is whatever you want<br>
MODEL is Google's model name, for example `gemini-1.5-flash`
```
BOT_TOKEN=1234567890:AABBCCDDEEFFGGHH-JJKKLLMM
BOT_TOKEN_DEV=1234567890:AABBCCDDEEFFGGHH-JJKKLLMM
API_KEY=AABBCCDDEEFFGGHH
PASS=yourpass
MODEL=gemini-1.5-flash
```

## Bot Setup

Remember to add the `/auth` and `/reset` commands via BotFather [(docs)](https://core.telegram.org/bots/features#commands)<br>

# Usage

Just send `/auth` to the bot, then reply with your PASS. The bot is now relaying your text messages 
to Gemini. To reset your chat with Gemini and clear the conversation history, use the `/reset` command.