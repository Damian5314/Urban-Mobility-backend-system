import re

def validate_username(username: str) -> bool:
    return bool(re.fullmatch(r"[A-Za-z0-9_]{8,10}", username))

def validate_password(password: str) -> bool:
    # At least 8 chars, 1 uppercase, 1 lowercase, 1 digit, 1 special char
    return bool(re.fullmatch(r"(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^A-Za-z0-9]).{8,}", password))

def validate_zip_code(zipcode: str) -> bool:
    return bool(re.fullmatch(r"[1-9][0-9]{3}[A-Z]{2}", zipcode))

def validate_license_number(lic: str) -> bool:
    return bool(re.fullmatch(r"[A-Z]{2}-\d{2}-\d{2}", lic))