from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    Application,
    MessageHandler,
    CommandHandler,
    ContextTypes,
    filters
)

from database import (
    init_db,
    save_expense,
    get_today_expenses,
    get_all_expenses,
    get_expenses_by_tag,
    save_special_category,
    get_special_category,
    save_tracker_value,
    get_last_tracker_value
)

from export_service import create_excel

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
            tags.append(word[1:])
        else:
            note_words.append(word)

    note = " ".join(note_words)

    return {
        "amount": amount,
        "category": category,
        "note": note,
        "tags": tags
    }


async def today_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    rows = get_today_expenses(
        update.effective_user.id
    )

    if not rows:
        await update.message.reply_text(
            "No expenses logged today."
        )
        return

    category_totals = {}
    grand_total = 0

    for category, amount in rows:

        category_totals[category] = (
            category_totals.get(category, 0) + amount
        )

        grand_total += amount

    message = "Today's Spending\n\n"

    for category, total in category_totals.items():
        message += f"{category}: ₹{total}\n"

    message += f"\nTotal: ₹{grand_total}"

    await update.message.reply_text(message)

async def export_command( update: Update, context: ContextTypes.DEFAULT_TYPE):

    rows = get_all_expenses(
        update.effective_user.id
    )

    if not rows:
        await update.message.reply_text(
            "No expenses found."
        )
        return

    filename = "expenses.xlsx"

    create_excel(
        rows,
        filename
    )

    with open(filename, "rb") as file:

        await update.message.reply_document(
            document=file,
            filename=filename
        )
    # currently, the file is deleted after sending it to the user. we switch to bytesio later and generate in memory 
    os.remove(filename)

async def tag_command( update: Update, context: ContextTypes.DEFAULT_TYPE):

    if len(context.args) == 0:

        await update.message.reply_text(
            "Usage: /tag goa"
        )

        return

    tag = context.args[0].lower()

    rows = get_expenses_by_tag(
        update.effective_user.id,
        tag
    )

    if not rows:

        await update.message.reply_text(
            f"No expenses found for #{tag}"
        )

        return

    category_totals = {}
    grand_total = 0

    for category, amount in rows:

        category_totals[category] = (
            category_totals.get(category, 0) + amount
        )

        grand_total += amount

    message = f"Tag: #{tag}\n\n"

    for category, total in category_totals.items():

        message += (
            f"{category}: ₹{total}\n"
        )

    message += (
        f"\nTotal: ₹{grand_total}"
    )

    await update.message.reply_text(
        message
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

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):

    # User is replying to a special category question
    if "pending_expense" in context.user_data:

        try:
            tracker_value = float(
                update.message.text
            )

        except ValueError:
            await update.message.reply_text(
                "Please enter a number."
            )
            return

        expense = context.user_data["pending_expense"]

        previous = get_last_tracker_value(
        update.effective_user.id,
        expense["category"]
        )

        difference = None
        if previous:
            difference = (
                tracker_value -
                previous[0]
            )

        save_expense(
            user_id=update.effective_user.id,
            amount=expense["amount"],
            category=expense["category"],
            note=expense["note"],
            tags=expense["tags"]
        )

        save_tracker_value(
            user_id=update.effective_user.id,
            category=expense["category"],
            tracker_value=tracker_value,
            previous_value=(
                previous[0]
                if previous
                else None
            ),
            difference=difference
        )

        del context.user_data["pending_expense"]

        message = (
            f"Added ₹{expense['amount']} "
            f"to {expense['category']}"
        )

        if difference is not None:
            message += (
                f"\nDifference since last reading: "
                f"{difference}"
            )

        await update.message.reply_text(
            message
        )

        return

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

    # Check if category is special
    special = get_special_category(
        update.effective_user.id,
        result["category"]
    )

    if special:

        context.user_data["pending_expense"] = result

        tracker_name = special[0]

        await update.message.reply_text(
            f"Enter {tracker_name}:"
        )

        return

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

    init_db()

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(
        CommandHandler(
            "today",
            today_command
        )
    )

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            handle_message
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

    print("Paisa Kidhar Bot Started...")

    app.run_polling()


if __name__ == "__main__":
    main()