from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
)

from bot.config import settings
from bot.handlers.audio import (
    cmd_help,
    cmd_separate,
    cmd_start,
    cmd_status,
    handle_voice,
)
from bot.handlers.generate import generate_handler
from bot.handlers.notes import cmd_note, cmd_notes, handle_text_note
from bot.handlers.youtube import handle_url


def main():
    app = ApplicationBuilder().token(settings.telegram_token).build()

    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("help", cmd_help))
    app.add_handler(CommandHandler("separate", cmd_separate))
    app.add_handler(CommandHandler("note", cmd_note))
    app.add_handler(CommandHandler("notes", cmd_notes))
    app.add_handler(CommandHandler("status", cmd_status))

    app.add_handler(generate_handler())

    app.add_handler(MessageHandler(filters.VOICE | filters.AUDIO, handle_voice))
    app.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND & filters.Regex(r"https?://(?:youtu|soundcloud)"),
        handle_url,
    ))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_note))

    print(f"Bot started. API: {settings.api_url}")
    app.run_polling()


if __name__ == "__main__":
    main()
