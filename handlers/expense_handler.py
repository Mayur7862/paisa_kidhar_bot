from telegram import Update
from telegram.ext import ContextTypes

from services.parser import parse_expense

from database import (
    save_expense,
    get_special_category,
    save_tracker_value,
    get_last_tracker_value
)

import pandas as pd

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