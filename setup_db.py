import sqlite3

def setup_database():
    conn = sqlite3.connect('reimbursements.db')
    cursor = conn.cursor()

    # Create the reimbursements table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reimbursements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id TEXT,
            name TEXT,
            date TEXT,
            serial_number TEXT
        )
    ''')

    # Create the reimbursement_amounts table for storing multiple amounts
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reimbursement_amounts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            reimbursement_id INTEGER,
            amount REAL,
            description TEXT,
            FOREIGN KEY (reimbursement_id) REFERENCES reimbursements (id)
        )
    ''')

    conn.commit()

    # List all tables in the database
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print("Tables in database:", tables)

    conn.close()
    print("Tables created successfully.")

if __name__ == '__main__':
    setup_database()