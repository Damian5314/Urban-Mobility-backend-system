import sqlite3
from datetime import datetime
from encryption import encrypt_data, decrypt_data

DB_PATH = 'data/data.db'
LOG_PATH = 'logs.db'

def get_db():
    return sqlite3.connect(DB_PATH)

def init_db():
    with get_db() as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL,
            first_name TEXT,
            last_name TEXT,
            registration_date TEXT
        )''')
        c.execute('''CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            log_entry TEXT,
            timestamp TEXT
        )''')
        c.execute('''CREATE TABLE IF NOT EXISTS restore_codes (
            code TEXT PRIMARY KEY,
            system_admin_username TEXT,
            backup_name TEXT,
            used INTEGER
        )''')
        # Add other tables as needed
        conn.commit()

def get_user_by_username(username: str):
    with get_db() as conn:
        c = conn.cursor()
        c.execute('SELECT username, password_hash, role, first_name, last_name, registration_date FROM users WHERE username=?', (username,))
        row = c.fetchone()
        if row:
            return {
                'username': row[0],
                'password_hash': row[1],
                'role': row[2],
                'first_name': row[3],
                'last_name': row[4],
                'registration_date': row[5]
            }
        return None

def add_user(username, password_hash, role, first_name, last_name):
    try:
        with get_db() as conn:
            c = conn.cursor()
            c.execute('INSERT INTO users (username, password_hash, role, first_name, last_name, registration_date) VALUES (?, ?, ?, ?, ?, ?)',
                      (username, password_hash, role, first_name, last_name, datetime.now().isoformat()))
            conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False

def log_event(event: str):
    encrypted_entry = encrypt_data(event)
    timestamp = datetime.now().isoformat()
    with open(LOG_PATH, 'a', encoding='utf-8') as f:
        f.write(f"{timestamp}|{encrypted_entry}\n")