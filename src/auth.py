import bcrypt
from db import get_user_by_username, add_user
from input_validation import validate_username, validate_password
from encryption import encrypt_data, decrypt_data

SUPER_ADMIN = {'username': 'super_admin', 'password': 'Admin_123?', 'role': 'super_admin'}

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def check_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())

def login(username: str, password: str) -> str | None:
    from db import log_event
    if username == SUPER_ADMIN['username'] and password == SUPER_ADMIN['password']:
        log_event(f"Succesvolle login: {username}")
        return SUPER_ADMIN['role']
    user = get_user_by_username(username)
    if user and check_password(password, user['password_hash']):
        log_event(f"Succesvolle login: {username}")
        return user['role']
    else:
        log_event(f"Fout wachtwoord voor gebruiker: {username}")
    return None

def register_user(username: str, password: str, role: str, first_name: str, last_name: str) -> bool:
    from db import log_event
    if not (validate_username(username) and validate_password(password)):
        return False
    password_hash = hash_password(password)
    result = add_user(username, password_hash, role, first_name, last_name)
    if result:
        log_event(f"Aangemaakte gebruiker: {username} ({role})")
    return result