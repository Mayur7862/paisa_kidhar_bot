import pandas as pd


def create_excel(rows, filename):
    """
    rows comes from SQLite:
    [
        (
            created_at,
            amount,
            category,
            note,
            tags
        )
    ]
    """

    df = pd.DataFrame(
        rows,
        columns=[
            "Date",
            "Amount",
            "Category",
            "Note",
            "Tags"
        ]
    )

    df.to_excel(
        filename,
        index=False
    )