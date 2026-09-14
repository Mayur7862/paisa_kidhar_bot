import sqlite3

from datetime import datetime, timedelta


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

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tracker_values (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            category TEXT,
            tracker_value REAL,
            previous_value REAL,
            difference REAL,
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

def save_tracker_value(
    user_id,
    category,
    tracker_value,
    previous_value,
    difference
):

    conn = sqlite3.connect("paisa_kidhar.db")
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO tracker_values
        (
            user_id,
            category,
            tracker_value,
            previous_value,
            difference
        )
        VALUES (?, ?, ?, ?, ?)
    """, (
        user_id,
        category,
        tracker_value,
        previous_value,
        difference
    ))

    conn.commit()
    conn.close()

def get_last_tracker_value(
    user_id,
    category
):

    conn = sqlite3.connect("paisa_kidhar.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT tracker_value
        FROM tracker_values
        WHERE user_id = ?
        AND category = ?
        ORDER BY id DESC
        LIMIT 1
    """, (
        user_id,
        category
    ))

    row = cursor.fetchone()
    conn.close()
    return row

def get_tracker_history(
    user_id,
    category
):

    conn = sqlite3.connect("paisa_kidhar.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            created_at,
            previous_value,
            tracker_value,
            difference
        FROM tracker_values
        WHERE user_id = ?
        AND category = ?
        ORDER BY created_at
    """, (
        user_id,
        category
    ))

    rows = cursor.fetchall()
    conn.close()
    return rows

def get_special_categories(user_id):

    conn = sqlite3.connect("paisa_kidhar.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT category
        FROM special_categories
        WHERE user_id = ?
    """, (user_id,))

    rows = cursor.fetchall()
    conn.close()
    return rows

def get_category_summary(user_id, category):

    today = datetime.now().date()

    week_start = today - timedelta(days=today.weekday())

    month_start = today.replace(day=1)

    conn = sqlite3.connect("paisa_kidhar.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT COALESCE(SUM(amount), 0)
        FROM expenses
        WHERE user_id = ?
        AND category = ?
        AND DATE(created_at) = ?
    """, (
        user_id,
        category,
        str(today)
    ))
    today_total = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COALESCE(SUM(amount), 0)
        FROM expenses
        WHERE user_id = ?
        AND category = ?
        AND DATE(created_at) >= ?
    """, (
        user_id,
        category,
        str(week_start)
    ))
    week_total = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COALESCE(SUM(amount), 0)
        FROM expenses
        WHERE user_id = ?
        AND category = ?
        AND DATE(created_at) >= ?
    """, (
        user_id,
        category,
        str(month_start)
    ))
    month_total = cursor.fetchone()[0]

    conn.close()

    return {
        "today": today_total,
        "week": week_total,
        "month": month_total
    }

def get_overall_summary(user_id):

    today = datetime.now().date()

    week_start = today - timedelta(days=today.weekday())

    month_start = today.replace(day=1)

    conn = sqlite3.connect("paisa_kidhar.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT COALESCE(SUM(amount), 0)
        FROM expenses
        WHERE user_id = ?
        AND DATE(created_at) = ?
    """, (
        user_id,
        str(today)
    ))
    today_total = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COALESCE(SUM(amount), 0)
        FROM expenses
        WHERE user_id = ?
        AND DATE(created_at) >= ?
    """, (
        user_id,
        str(week_start)
    ))
    week_total = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COALESCE(SUM(amount), 0)
        FROM expenses
        WHERE user_id = ?
        AND DATE(created_at) >= ?
    """, (
        user_id,
        str(month_start)
    ))
    month_total = cursor.fetchone()[0]

    conn.close()

    return {
        "today": today_total,
        "week": week_total,
        "month": month_total
    }