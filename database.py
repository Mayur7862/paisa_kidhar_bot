import sqlite3


def init_db():

    conn = sqlite3.connect("paisa_kidhar.db")

    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            amount REAL,
            category TEXT,
            note TEXT,
            tags TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()


def save_expense(user_id, amount, category, note, tags):

    conn = sqlite3.connect("paisa_kidhar.db")

    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO expenses
        (user_id, amount, category, note, tags)
        VALUES (?, ?, ?, ?, ?)
    """, (
        user_id,
        amount,
        category,
        note,
        ",".join(tags)
    ))

    conn.commit()
    conn.close()
