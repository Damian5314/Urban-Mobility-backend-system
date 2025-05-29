from db import get_db
from db import init_db
init_db()

def add_scooter(scooter_id, location):
    with get_db() as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS scooters (
            id TEXT PRIMARY KEY,
            location TEXT
        )''')
        c.execute('INSERT INTO scooters (id, location) VALUES (?, ?)', (scooter_id, location))
        conn.commit()

def view_travellers():
    with get_db() as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS travellers (
            id TEXT PRIMARY KEY,
            naam TEXT
        )''')
        c.execute('SELECT id, naam FROM travellers')
        rows = c.fetchall()
        return [{'id': row[0], 'naam': row[1]} for row in rows]

def update_traveller(traveller_id, new_name):
    with get_db() as conn:
        c = conn.cursor()
        c.execute('UPDATE travellers SET naam=? WHERE id=?', (new_name, traveller_id))
        conn.commit()

def delete_traveller(traveller_id):
    with get_db() as conn:
        c = conn.cursor()
        c.execute('DELETE FROM travellers WHERE id=?', (traveller_id,))
        conn.commit()