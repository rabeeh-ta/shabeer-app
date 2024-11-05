import os
import sqlite3

# Use the /tmp directory for the database file on Vercel
DATABASE_PATH = '/tmp/reimbursements.db'

def connect_db():
    """Connect to the SQLite database."""
    return sqlite3.connect(DATABASE_PATH)

def init_db():
    """Initialize the database and create tables if they don't exist."""
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS reimbursements (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            employee_id TEXT,
                            name TEXT,
                            date TEXT,
                            amount REAL,
                            description TEXT,
                            serial_number TEXT
                        )''')
        conn.commit()

# Initialize the database if it hasn't been created yet
if not os.path.exists(DATABASE_PATH):
    init_db()
