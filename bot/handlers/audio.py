import httpx
from telegram import Update
from telegram.ext import ContextTypes

from bot.config import settings

API = settings.api_url


async def cmd_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "sona — AI Audio Studio\n\n"
        "Send a voice message — get a transcription.\n"
        "Send a YouTube/SoundCloud link — I'll download and split it into stems.\n\n"
        "/generate — create a track from text\n"
        "/separate — split audio into stems\n"
        "/note — save a voice note\n"
        "/notes — list notes\n"
        "/status <job_id> — job status\n"
        "/help — this message"
    )


async def cmd_help(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await cmd_start(update, ctx)


async def handle_voice(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    mode = ctx.user_data.get("mode")

    voice = update.message.voice or update.message.audio
    audio_file = await voice.get_file()
    audio_bytes = await audio_file.download_as_bytearray()
    ext = ".ogg" if update.message.voice else ".mp3"

    if mode == "note":
        ctx.user_data.pop("mode", None)
        msg = await update.message.reply_text("Saving note...")
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(
                f"{API}/notes",
                files={"file": (f"audio{ext}", bytes(audio_bytes), "audio/ogg")},
            )
            resp.raise_for_status()
            note = resp.json()
        await msg.edit_text(
            f"Note saved\n*{note['title']}*\n\n{note['summary']}",
            parse_mode="Markdown",
        )
        return

    if mode == "separate":
        ctx.user_data.pop("mode", None)
        msg = await update.message.reply_text("Splitting stems...")
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(
                f"{API}/separate",
                files={"file": (f"audio{ext}", bytes(audio_bytes), "audio/mpeg")},
            )
            resp.raise_for_status()
            job = resp.json()
        await msg.edit_text(
            f"Job created: `{job['job_id']}`\n"
            f"Check status: /status {job['job_id']}",
            parse_mode="Markdown",
        )
        return

    msg = await update.message.reply_text("Transcribing...")
    async with httpx.AsyncClient(timeout=60.0) as client:
        resp = await client.post(
            f"{API}/transcribe",
            files={"file": (f"audio{ext}", bytes(audio_bytes), "audio/ogg")},
            data={"language": "auto"},
        )
        resp.raise_for_status()
        result = resp.json()

    await msg.edit_text(
        f"Language: {result['language']} | {result['duration_seconds']}s\n\n{result['text']}",
    )


async def cmd_separate(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    ctx.user_data["mode"] = "separate"
    await update.message.reply_text("Send an audio file to split into stems.")


async def cmd_status(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not ctx.args:
        await update.message.reply_text("Usage: /status <job_id>")
        return

    job_id = ctx.args[0]
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.get(f"{API}/jobs/{job_id}")
        if resp.status_code == 404:
            await update.message.reply_text(f"Job {job_id} not found.")
            return
        job = resp.json()

    icons = {"pending": "⏳", "running": "⚙️", "done": "✅", "error": "❌"}
    icon = icons.get(job["status"], "?")
    lines = [f"{icon} `{job_id}` — {job['status']}"]
    if job.get("error"):
        lines.append(f"Error: {job['error']}")
    if job.get("result") and job["status"] == "done":
        lines.append(f"Result: {job['result']}")

    await update.message.reply_text("\n".join(lines), parse_mode="Markdown")
