from telegram import Update
from telegram.ext import ContextTypes

from services.parser import parse_expense

from database import (
    save_expense,
    get_special_category,
    save_tracker_value,
    get_last_tracker_value,
    get_category_summary,
    get_overall_summary
)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):

    # Special category follow-up
    if "pending_expense" in context.user_data:

        try:
            tracker_value = float(update.message.text)

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

            if tracker_value < previous[0]:

                await update.message.reply_text(
                    f"Value cannot be smaller than the previous reading ({previous[0]}).\nPlease enter a valid value."
                )

                return

            difference = tracker_value - previous[0]

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

        category_stats = get_category_summary(
            update.effective_user.id,
            expense["category"]
        )

        overall_stats = get_overall_summary(
            update.effective_user.id
        )

        message = (
            f"✅ Added ₹{expense['amount']} to {expense['category'].title()}"
        )

        if previous:

            message += (
                f"\n\n📊 Tracker"
                f"\n• Previous: {previous[0]}"
                f"\n• Current: {tracker_value}"
                f"\n• Difference: {difference}"
            )

        else:

            message += (
                f"\n\n📊 Tracker"
                f"\n• Current: {tracker_value}"
                f"\n• First reading recorded"
            )

        message += (
            f"\n\n📂 {expense['category'].title()}"
            f"\n• Today: ₹{category_stats['today']}"
            f"\n• This Week: ₹{category_stats['week']}"
            f"\n• This Month: ₹{category_stats['month']}"
            f"\n\n💰 Overall"
            f"\n• Today: ₹{overall_stats['today']}"
            f"\n• This Week: ₹{overall_stats['week']}"
            f"\n• This Month: ₹{overall_stats['month']}"
        )

        await update.message.reply_text(message)

        return

    # Normal expense flow
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

    category_stats = get_category_summary(
        update.effective_user.id,
        result["category"]
    )

    overall_stats = get_overall_summary(
        update.effective_user.id
    )

    message = (
        f"✅ Added ₹{result['amount']} to {result['category'].title()}"
        f"\n\n📂 {result['category'].title()}"
        f"\n• Today: ₹{category_stats['today']}"
        f"\n• This Week: ₹{category_stats['week']}"
        f"\n• This Month: ₹{category_stats['month']}"
        f"\n\n💰 Overall"
        f"\n• Today: ₹{overall_stats['today']}"
        f"\n• This Week: ₹{overall_stats['week']}"
        f"\n• This Month: ₹{overall_stats['month']}"
    )

    await update.message.reply_text(message)