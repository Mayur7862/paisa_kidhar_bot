import pandas as pd


def create_excel(
    expenses,
    special_data,
    filename
):

    with pd.ExcelWriter(
        filename,
        engine="openpyxl"
    ) as writer:

        expense_df = pd.DataFrame(
            expenses,
            columns=[
                "Date",
                "Amount",
                "Category",
                "Note",
                "Tags"
            ]
        )

        expense_df.to_excel(
            writer,
            sheet_name="Expenses",
            index=False
        )

        for category, rows in special_data.items():

            tracker_df = pd.DataFrame(
                rows,
                columns=[
                    "Date",
                    "Previous",
                    "Current",
                    "Difference"
                ]
            )

            tracker_df.to_excel(
                writer,
                sheet_name=category[:31],
                index=False
            )