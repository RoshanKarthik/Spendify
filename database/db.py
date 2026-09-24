import sqlite3
from werkzeug.security import generate_password_hash

DB_PATH = "spendly.db"

def get_db():
    """
    Opens a connection to the SQLite database, sets row_factory to Row
    and enables foreign key constraints.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def init_db():
    """
    Creates the users and expenses tables if they do not already exist.
    """
    with get_db() as conn:
        # Users table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TEXT DEFAULT (datetime('now'))
            );
        """)

        # Expenses table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                date TEXT NOT NULL,
                description TEXT,
                created_at TEXT DEFAULT (datetime('now')),
                FOREIGN KEY (user_id) REFERENCES users (id)
            );
        """)
        conn.commit()

def seed_db():
    """
    Inserts sample data into the database if it is empty.
    """
    with get_db() as conn:
        # Check if users table already has data
        user = conn.execute("SELECT 1 FROM users LIMIT 1").fetchone()
        if user:
            return

        # Insert demo user
        hashed_pw = generate_password_hash("demo123")
        cursor = conn.execute(
            "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
            ("Demo User", "demo@spendly.com", hashed_pw)
        )
        user_id = cursor.lastrowid

        # Sample expenses across all required categories
        sample_expenses = [
            (user_id, 12.50, "Food", "2026-09-01", "Lunch at Cafe"),
            (user_id, 45.00, "Transport", "2026-09-02", "Weekly Gas"),
            (user_id, 120.00, "Bills", "2026-09-05", "Internet Bill"),
            (user_id, 30.00, "Health", "2026-09-08", "Pharmacy"),
            (user_id, 15.00, "Entertainment", "2026-09-10", "Movie Ticket"),
            (user_id, 60.00, "Shopping", "2026-09-12", "New Shirt"),
            (user_id, 10.00, "Other", "2026-09-15", "Parking fee"),
            (user_id, 25.00, "Food", "2026-09-18", "Dinner"),
        ]

        conn.executemany(
            "INSERT INTO expenses (user_id, amount, category, date, description) VALUES (?, ?, ?, ?, ?)",
            sample_expenses
        )
        conn.commit()
