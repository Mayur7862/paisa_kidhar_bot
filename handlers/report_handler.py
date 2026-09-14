import os

from telegram import Update
from telegram.ext import ContextTypes

from services.export_service import create_excel

from database import (
    get_today_expenses,
    get_all_expenses,
    get_expenses_by_tag,
    get_special_categories,
    get_tracker_history
)

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

    special_data = {}

    special_categories = get_special_categories(
        update.effective_user.id
    )

    for category_row in special_categories:

        category = category_row[0]

        history = get_tracker_history(
            update.effective_user.id,
            category
        )

        special_data[category] = history

    create_excel(
        rows,
        special_data,
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
