import os

from dotenv import load_dotenv

from telegram.ext import (
    Application,
    MessageHandler,
    CommandHandler,
    filters
)

from database import init_db

from handlers.expense_handler import handle_message

from handlers.report_handler import (
    today_command,
    export_command,
    tag_command
)

from handlers.special_handler import (
    make_special_command
)
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")



def main():

    init_db()

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(
        CommandHandler(
            "today",
            today_command
        )
    )

    app.add_handler(
        CommandHandler(
            "export",
            export_command
        )
    )

    app.add_handler(
        CommandHandler(
            "tag",
            tag_command
        )
    )

    app.add_handler(
        CommandHandler(
            "make_special",
            make_special_command
        )
    )

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            handle_message
        )
    )

    print("Paisa Kidhar Bot Started...")

    app.run_polling()


if __name__ == "__main__":
    main()