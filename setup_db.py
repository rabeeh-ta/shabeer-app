import os
import sqlite3

# Use the /tmp directory for the database file on Vercel
DATABASE_PATH = '/tmp/reimbursements.db'

def connect_db():
    return sqlite3.connect(DATABASE_PATH)

# Check if the database exists; if not, initialize it
if not os.path.exists(DATABASE_PATH):
    conn = connect_db()
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
    conn.close()