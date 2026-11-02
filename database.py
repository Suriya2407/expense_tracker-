
import sqlite3
import pandas as pd

DB_NAME = "expenses.db"


def get_connection():
    return sqlite3.connect(DB_NAME)


def create_tables():
    with get_connection() as conn:

        conn.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                transaction_type TEXT NOT NULL,
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                transaction_date TEXT NOT NULL,
                payment_method TEXT NOT NULL,
                description TEXT
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS budgets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                month TEXT NOT NULL UNIQUE,
                amount REAL NOT NULL
            )
        """)


def add_transaction(
    transaction_type,
    amount,
    category,
    transaction_date,
    payment_method,
    description
):
    with get_connection() as conn:

        conn.execute("""
            INSERT INTO transactions (
                transaction_type,
                amount,
                category,
                transaction_date,
                payment_method,
                description
            )
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            transaction_type,
            amount,
            category,
            transaction_date,
            payment_method,
            description
        ))


def get_transactions():
    with get_connection() as conn:

        return pd.read_sql_query(
            "SELECT * FROM transactions ORDER BY transaction_date DESC, id DESC",
            conn
        )


def delete_transaction(transaction_id):
    with get_connection() as conn:

        conn.execute(
            "DELETE FROM transactions WHERE id = ?",
            (transaction_id,)
        )


def save_budget(month, amount):
    with get_connection() as conn:

        conn.execute("""
            INSERT INTO budgets (month, amount)
            VALUES (?, ?)
            ON CONFLICT(month)
            DO UPDATE SET amount = excluded.amount
        """, (month, amount))


def get_budget(month):
    with get_connection() as conn:

        result = conn.execute(
            "SELECT amount FROM budgets WHERE month = ?",
            (month,)
        ).fetchone()

    return result[0] if result else 0.0


create_tables()