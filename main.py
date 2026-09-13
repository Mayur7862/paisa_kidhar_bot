from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, MessageHandler, ContextTypes, filters

from database import init_db, save_expense

import os

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")


def parse_expense(text):

    parts = text.split()

    if not parts:
        return None

    # First word must be amount
    try:
        amount = float(parts[0])
    except:
        return None

    # Second word is category
    category = parts[1].lower() if len(parts) > 1 else "Missing"

    tags = []
    note_words = []

    # Everything after amount & category
    for word in parts[2:]:

        if word.startswith("#"):
            tags.append(word[1:])  # Remove #

        else:
            note_words.append(word)

    note = " ".join(note_words)

    return {
        "amount": amount,
        "category": category,
        "note": note,
        "tags": tags
    }


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):

    result = parse_expense(update.message.text)

    if result is None:
        await update.message.reply_text(
            "Amount missing.\nExample: 100 food"
        )
        return

    if result["category"] == "Missing":
        await update.message.reply_text(
            "Category missing."
        )
        return

    # Save expense in SQLite
    save_expense(
        user_id=update.effective_user.id,
        amount=result["amount"],
        category=result["category"],
        note=result["note"],
        tags=result["tags"]
    )

    await update.message.reply_text(
        f"Added ₹{result['amount']} to {result['category']}"
    )


def main():

    # Create DB/table if not present
    init_db()

    app = Application.builder().token(BOT_TOKEN).build()

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