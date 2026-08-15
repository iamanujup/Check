# Quiz Cloner Userbot

Pyrogram-based Telegram userbot that can:

- `/clone TOKEN` — scrape a quiz and send a TXT file
- MongoDB cache by token
- Automatically vote the first poll option
- Capture question/options/correct answer/explanation
- `/status` — show scraper status
- `/cached TOKEN` — check cache

## Setup

### 1. Get Telegram API credentials

Create an application at Telegram's official developer portal and obtain `API_ID` and `API_HASH`.

### 2. Generate a Pyrogram session string

Generate a session string using a trusted Pyrogram session-string generator or your own script. Never publish the session string.

### 3. Install

```bash
pip install -r requirements.txt
```

### 4. Configure

Copy `.env.example` to `.env` and fill:

```text
API_ID=
API_HASH=
SESSION_STRING=
MONGO_URI=
DB_NAME=QuizCloner
QUIZBOT_USERNAME=QuizBot
```

Export the variables in your shell or load them with your preferred environment manager.

### 5. Run

```bash
python main.py
```

## Commands

```text
/clone TOKEN
/status
/cached TOKEN
```

## Important

The bot interaction depends on the target quiz bot's current messages, buttons and behavior. Keep the implementation compliant with Telegram and the target bot's rules. Do not commit `.env` or a session string.
