from telegram import Update
from telegram.ext import ContextTypes

from database import (
    save_special_category,
    get_special_category
)

async def make_special_command( update: Update, context: ContextTypes.DEFAULT_TYPE):

    if len(context.args) != 2:

        await update.message.reply_text(
            "Usage:\n/make_special petrol odometer"
        )

        return

    category = context.args[0]
    tracker = context.args[1]

    save_special_category(
        update.effective_user.id,
        category,
        tracker
    )

    await update.message.reply_text(
        f"{category} configured with {tracker}"
    )
