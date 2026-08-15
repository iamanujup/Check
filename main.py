import asyncio
import time

from pyrogram import Client, filters
from pyrogram.errors import FloodWait

from config import API_ID, API_HASH, SESSION_STRING, QUIZBOT_USERNAME
from database import get_cached_quiz, save_quiz
from formatter import format_quiz, make_txt

app = Client(
    "quiz_cloner_userbot",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=SESSION_STRING,
)

is_running = False
job = {"token": None, "polls": [], "started": 0, "stop": None}


def clean_text(text):
    import re
    if not text:
        return ""
    text = re.sub(r"https?://\S+|www\.\S+", "", str(text))
    text = re.sub(r"@\w+", "", text)
    return re.sub(r"\s+", " ", text).strip()


async def capture_poll(client, message, polls):
    try:
        await client.vote_poll(message.chat.id, message.id, [0])
    except FloodWait as e:
        await asyncio.sleep(e.value)
        try:
            await client.vote_poll(message.chat.id, message.id, [0])
        except Exception:
            return False
    except Exception:
        return False

    for _ in range(20):
        await asyncio.sleep(0.5)
        try:
            updated = await client.get_messages(message.chat.id, message.id)
            if not updated or not updated.poll:
                continue
            poll = updated.poll
            if poll.correct_option_id is None:
                continue

            polls.append({
                "question": clean_text(poll.question),
                "options": [clean_text(o.text) for o in poll.options],
                "correct": poll.correct_option_id,
                "explanation": clean_text(getattr(poll, "explanation", "")) or "📚",
                "_message_id": message.id,
            })
            return True
        except Exception:
            continue
    return False


async def click_start_button(client, chat_id):
    try:
        async for message in client.get_chat_history(chat_id, limit=30):
            markup = message.reply_markup
            if not markup or not hasattr(markup, "inline_keyboard"):
                continue
            for row in markup.inline_keyboard:
                for button in row:
                    if "start quiz" in (button.text or "").lower():
                        try:
                            await message.click(button.text)
                        except Exception:
                            await message.click()
                        return True
    except Exception as e:
        print("Start button error:", e)
    return False


async def scrape_quiz(client, token):
    polls = []
    stop_event = asyncio.Event()
    job["polls"] = polls
    job["stop"] = stop_event

    try:
        await client.send_message(QUIZBOT_USERNAME, "/stop")
    except Exception:
        pass

    await asyncio.sleep(1)
    await client.send_message(QUIZBOT_USERNAME, f"/start {token}")

    deadline = time.monotonic() + 30
    started = False
    while time.monotonic() < deadline:
        if await click_start_button(client, QUIZBOT_USERNAME):
            started = True
            break
        await asyncio.sleep(1)

    if not started:
        return []

    last_activity = time.monotonic()
    seen = set()

    async def watcher():
        nonlocal last_activity
        while not stop_event.is_set():
            try:
                async for message in client.get_chat_history(QUIZBOT_USERNAME, limit=50):
                    if message.id in seen:
                        continue
                    if message.date and message.date.timestamp() < job["started"]:
                        continue
                    if not message.poll or not message.poll.is_quiz:
                        continue

                    seen.add(message.id)
                    last_activity = time.monotonic()
                    await capture_poll(client, message, polls)

                await asyncio.sleep(0.7)
            except Exception as e:
                print("Watcher error:", e)
                await asyncio.sleep(1)

    task = asyncio.create_task(watcher())
    try:
        while time.monotonic() - last_activity <= 25:
            await asyncio.sleep(1)
            if len(polls) > 0:
                last_activity = time.monotonic()
        return polls
    finally:
        stop_event.set()
        task.cancel()
        try:
            await task
        except BaseException:
            pass


@app.on_message(filters.command("clone") & filters.private)
async def clone_handler(client, message):
    global is_running

    if len(message.command) < 2:
        await message.reply_text("Usage: `/clone TOKEN`")
        return

    token = message.command[1].strip()

    cached = await get_cached_quiz(token)
    if cached:
        text = format_quiz(cached["questions"])
        await client.send_document(
            message.chat.id,
            make_txt(text, f"{token}.txt"),
            caption=f"⚡ Cached quiz\nQuestions: {len(cached['questions'])}",
        )
        return

    if is_running:
        await message.reply_text("⏳ Scraper Busy — another quiz is running.")
        return

    is_running = True
    job.update({"token": token, "polls": [], "started": time.time(), "stop": None})
    status = await message.reply_text(f"🚀 Cloning `{token}`...")

    try:
        polls = await scrape_quiz(client, token)
        for p in polls:
            p.pop("_message_id", None)

        if not polls:
            await status.edit_text("❌ No quiz polls captured.")
            return

        await save_quiz(token, polls)
        text = format_quiz(polls)

        await client.send_document(
            message.chat.id,
            make_txt(text, f"{token}.txt"),
            caption=f"✅ Quiz cloned\nQuestions: {len(polls)}",
        )
        await status.edit_text(f"✅ Completed\nQuestions: `{len(polls)}`")

    except Exception as e:
        await status.edit_text(f"❌ Error: `{str(e)[:700]}`")
    finally:
        is_running = False
        job.update({"token": None, "polls": [], "started": 0, "stop": None})


@app.on_message(filters.command("status") & filters.private)
async def status_handler(client, message):
    if is_running:
        await message.reply_text(
            f"🟢 Running\nToken: `{job['token']}`\nCaptured: `{len(job['polls'])}`"
        )
    else:
        await message.reply_text("⚪ Idle")


@app.on_message(filters.command("cached") & filters.private)
async def cached_handler(client, message):
    if len(message.command) < 2:
        await message.reply_text("Usage: `/cached TOKEN`")
        return
    item = await get_cached_quiz(message.command[1].strip())
    if not item:
        await message.reply_text("❌ Not found in cache.")
        return
    await message.reply_text(f"✅ Cached\nQuestions: `{len(item['questions'])}`")


if __name__ == "__main__":
    print("Quiz Cloner Userbot started.")
    app.run()
