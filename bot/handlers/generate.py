import httpx
from telegram import Update
from telegram.ext import (
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

from bot.config import settings

API = settings.api_url
LYRICS, STYLE = range(2)


async def cmd_generate(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Write the song lyrics.\n/cancel — cancel"
    )
    return LYRICS


async def got_lyrics(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    ctx.user_data["lyrics"] = update.message.text
    await update.message.reply_text(
        "Now specify the style / genre.\n"
        "Examples: `hip-hop dark`, `pop upbeat`, `lo-fi instrumental`\n/cancel — cancel",
        parse_mode="Markdown",
    )
    return STYLE


async def got_style(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    lyrics = ctx.user_data.pop("lyrics", "")
    style = update.message.text

    msg = await update.message.reply_text("Creating generation job... ⚙️")

    async with httpx.AsyncClient(timeout=15.0) as client:
        resp = await client.post(
            f"{API}/generate",
            json={
                "lyrics": lyrics,
                "style": style,
                "language": "ru",
                "duration_seconds": 30,
            },
        )
        resp.raise_for_status()
        job = resp.json()

    await msg.edit_text(
        f"Job started: `{job['job_id']}`\n"
        f"Generation takes ~1-2 minutes.\n"
        f"Check progress: /status {job['job_id']}",
        parse_mode="Markdown",
    )
    return ConversationHandler.END


async def cancel(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    ctx.user_data.clear()
    await update.message.reply_text("Cancelled.")
    return ConversationHandler.END


def generate_handler() -> ConversationHandler:
    return ConversationHandler(
        entry_points=[CommandHandler("generate", cmd_generate)],
        states={
            LYRICS: [MessageHandler(filters.TEXT & ~filters.COMMAND, got_lyrics)],
            STYLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, got_style)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
