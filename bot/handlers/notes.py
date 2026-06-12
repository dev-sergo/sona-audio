import httpx
from telegram import Update
from telegram.ext import ContextTypes

from bot.config import settings

API = settings.api_url


async def cmd_note(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    ctx.user_data["mode"] = "note"
    await update.message.reply_text(
        "Write the note text or send a voice message.\n/cancel — cancel"
    )


async def handle_text_note(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if ctx.user_data.get("mode") != "note":
        return
    ctx.user_data.pop("mode", None)

    text = update.message.text
    msg = await update.message.reply_text("Saving note...")

    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(f"{API}/notes", data={"text": text})
        resp.raise_for_status()
        note = resp.json()

    await msg.edit_text(
        f"Note saved\n*{note['title']}*\n\n{note['summary']}",
        parse_mode="Markdown",
    )


async def cmd_notes(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    search = " ".join(ctx.args) if ctx.args else None
    params = {"limit": 10}
    if search:
        params["search"] = search

    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.get(f"{API}/notes", params=params)
        resp.raise_for_status()
        data = resp.json()

    if not data["notes"]:
        await update.message.reply_text("No notes yet.")
        return

    lines = [f"Notes ({data['total']} total)\n"]
    for note in data["notes"]:
        tags = " ".join(f"#{t}" for t in note["tags"][:3])
        lines.append(f"[{note['id']}] {note['title']}  {tags}")

    await update.message.reply_text("\n".join(lines))
