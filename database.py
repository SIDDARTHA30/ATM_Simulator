import sqlite3

# Connect to SQLite DB
conn = sqlite3.connect("atm.db", check_same_thread=False)
c = conn.cursor()

# Create users table
c.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    pin TEXT,
    balance REAL
)
''')

# Create transactions table
c.execute('''
CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    type TEXT,
    amount REAL,
    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
''')

conn.commit()
