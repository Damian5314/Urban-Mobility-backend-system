import os
import zipfile
from datetime import datetime
from db import log_event

BACKUP_DIR = 'data/'
DB_FILE = 'data/data.db'

# Create a backup (zip) of the database
def create_backup(username):
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)
    backup_name = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
    backup_path = os.path.join(BACKUP_DIR, backup_name)
    with zipfile.ZipFile(backup_path, 'w') as zipf:
        zipf.write(DB_FILE, os.path.basename(DB_FILE))
    log_event(f"Backup gemaakt door {username}: {backup_name}")
    return backup_name

# Restore the database from a backup zip
def restore_backup(backup_zip, username, restore_code=None, is_super_admin=False):
    if not is_super_admin and not restore_code:
        log_event(f"Restore poging geweigerd voor {username} zonder restore-code")
        return False
    with zipfile.ZipFile(backup_zip, 'r') as zipf:
        zipf.extractall(BACKUP_DIR)
    log_event(f"Backup hersteld door {username}: {backup_zip}")
    return True