from cryptography.fernet import Fernet
import os

# Securely generate or load your key in production
KEY_PATH = 'data/fernet.key'

def load_or_create_key():
    if not os.path.exists(KEY_PATH):
        key = Fernet.generate_key()
        with open(KEY_PATH, 'wb') as f:
            f.write(key)
    else:
        with open(KEY_PATH, 'rb') as f:
            key = f.read()
    return key

key = load_or_create_key()
fernet = Fernet(key)

def encrypt_data(data: str) -> str:
    return fernet.encrypt(data.encode()).decode()

def decrypt_data(data: str) -> str:
    return fernet.decrypt(data.encode()).decode()