import sqlite3
from datetime import datetime

DB_NAME = "expenses.db"


def get_connection():
    return sqlite3.connect(DB_NAME, check_same_thread=False)


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            merchant TEXT,
            description TEXT,
            expense_date TEXT NOT NULL,
            payment_method TEXT,
            created_at TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS budgets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL,
            amount REAL NOT NULL,
            month TEXT NOT NULL,
            UNIQUE(category, month)
        )
    """)

    conn.commit()
    conn.close()


def add_expense(
    amount,
    category,
    merchant,
    description,
    expense_date,
    payment_method
):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO expenses
        (amount, category, merchant, description,
         expense_date, payment_method, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        amount,
        category,
        merchant,
        description,
        expense_date,
        payment_method,
        datetime.now().isoformat()
    ))

    conn.commit()
    conn.close()


def get_expenses():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, amount, category, merchant,
               description, expense_date, payment_method
        FROM expenses
        ORDER BY expense_date DESC, id DESC
    """)

    rows = cursor.fetchall()
    conn.close()

    return rows


def delete_expense(expense_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM expenses WHERE id = ?",
        (expense_id,)
    )

    conn.commit()
    conn.close()


def add_or_update_budget(category, amount, month):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO budgets (category, amount, month)
        VALUES (?, ?, ?)
        ON CONFLICT(category, month)
        DO UPDATE SET amount = excluded.amount
    """, (category, amount, month))

    conn.commit()
    conn.close()


def get_budgets(month):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT category, amount
        FROM budgets
        WHERE month = ?
    """, (month,))

    rows = cursor.fetchall()
    conn.close()

    return rows