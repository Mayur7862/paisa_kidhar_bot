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

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS special_categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        category TEXT,
        tracker_type TEXT
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


def get_today_expenses(user_id):

    conn = sqlite3.connect("paisa_kidhar.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT category, amount
        FROM expenses
        WHERE user_id = ?
        AND DATE(created_at) = DATE('now')
    """, (user_id,))

    rows = cursor.fetchall()
    conn.close()
    return rows

def get_all_expenses(user_id):

    conn = sqlite3.connect("paisa_kidhar.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            created_at,
            amount,
            category,
            note,
            tags
        FROM expenses
        WHERE user_id = ?
        ORDER BY created_at DESC
    """, (user_id,))

    rows = cursor.fetchall()
    conn.close()
    return rows

def get_expenses_by_tag(user_id, tag):

    conn = sqlite3.connect("paisa_kidhar.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT category, amount
        FROM expenses
        WHERE user_id = ?
        AND tags LIKE ?
    """, (
        user_id,
        f"%{tag}%"
    ))

    rows = cursor.fetchall()
    conn.close()
    return rows

def save_special_category(
    user_id,
    category,
    tracker_type
):

    conn = sqlite3.connect("paisa_kidhar.db")
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO special_categories
        (
            user_id,
            category,
            tracker_type
        )
        VALUES (?, ?, ?)
    """, (
        user_id,
        category.lower(),
        tracker_type.lower()
    ))

    conn.commit()
    conn.close()

def get_special_category(
    user_id,
    category
):

    conn = sqlite3.connect("paisa_kidhar.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT tracker_type
        FROM special_categories
        WHERE user_id = ?
        AND category = ?
    """, (
        user_id,
        category.lower()
    ))

    row = cursor.fetchone()

    conn.close()

    return row