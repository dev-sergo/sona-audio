import asyncio
import os
import re
import tempfile

import httpx
from telegram import Update
from telegram.ext import ContextTypes

from bot.config import settings

API = settings.api_url

_URL_RE = re.compile(
    r"https?://(?:www\.|m\.)?(?:youtube\.com/watch\?[^\s]*v=|youtu\.be/|soundcloud\.com/)\S+"
)


async def handle_url(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    text = update.message.text or ""
    match = _URL_RE.search(text)
    if not match:
        return

    url = match.group(0)
    msg = await update.message.reply_text("Downloading audio...")

    with tempfile.TemporaryDirectory() as tmpdir:
        out_template = os.path.join(tmpdir, "audio.%(ext)s")
        proc = await asyncio.create_subprocess_exec(
            "yt-dlp", "-x", "--audio-format", "mp3", "--audio-quality", "0",
            "-o", out_template, "--no-playlist", url,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        _, stderr = await proc.communicate()

        if proc.returncode != 0:
            err = stderr.decode(errors="replace")[-300:]
            await msg.edit_text(f"Download failed.\n`{err}`", parse_mode="Markdown")
            return

        files = [f for f in os.listdir(tmpdir) if f.endswith(".mp3")]
        if not files:
            await msg.edit_text("File not found after download.")
            return

        audio_bytes = open(os.path.join(tmpdir, files[0]), "rb").read()

    mode = ctx.user_data.get("mode")

    if mode == "note":
        ctx.user_data.pop("mode", None)
        await msg.edit_text("Transcribing and saving note...")
        async with httpx.AsyncClient(timeout=120.0) as client:
            resp = await client.post(
                f"{API}/notes",
                files={"file": ("audio.mp3", audio_bytes, "audio/mpeg")},
            )
            resp.raise_for_status()
            note = resp.json()
        await msg.edit_text(
            f"Note saved\n*{note['title']}*\n\n{note['summary']}",
            parse_mode="Markdown",
        )
        return

    # default: separate stems
    ctx.user_data.pop("mode", None)
    await msg.edit_text("Downloaded. Splitting into stems...")
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(
            f"{API}/separate",
            files={"file": ("audio.mp3", audio_bytes, "audio/mpeg")},
        )
        resp.raise_for_status()
        job = resp.json()

    await msg.edit_text(
        f"Done. Job: `{job['job_id']}`\n/status {job['job_id']}",
        parse_mode="Markdown",
    )
