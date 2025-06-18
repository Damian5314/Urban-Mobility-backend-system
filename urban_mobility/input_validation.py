import re
from datetime import datetime

def validate_username(username: str) -> bool:
    """
    Validate username according to requirements:
    - 8-10 characters
    - Start with letter or underscore
    - Can contain letters, numbers, underscores, apostrophes, periods
    - Case insensitive
    """
    if not username or len(username) < 8 or len(username) > 10:
        return False
    
    # Must start with letter or underscore
    if not re.match(r'^[A-Za-z_]', username):
        return False
    
    # Can only contain allowed characters
    if not re.fullmatch(r"[A-Za-z0-9_'.]{8,10}", username):
        return False
    
    return True

def validate_password(password: str) -> bool:
    """
    Validate password according to requirements:
    - 12-30 characters
    - At least one lowercase letter
    - At least one uppercase letter  
    - At least one digit
    - At least one special character from ~!@#$%&_-+=`|\(){}[]:;'<>,.?/
    """
    if not password or len(password) < 12 or len(password) > 30:
        return False
    
    # Check for required character types
    has_lower = bool(re.search(r'[a-z]', password))
    has_upper = bool(re.search(r'[A-Z]', password))
    has_digit = bool(re.search(r'\d', password))
    has_special = bool(re.search(r'[~!@#$%&_\-+=`|\\(){}[\]:;\'<>,.?/]', password))
    
    return has_lower and has_upper and has_digit and has_special

def validate_zip_code(zipcode: str) -> bool:
    """
    Validate Dutch zip code format: DDDDXX (4 digits + 2 uppercase letters)
    """
    return bool(re.fullmatch(r'[1-9][0-9]{3}[A-Z]{2}', zipcode))

def validate_mobile_phone(phone: str) -> bool:
    """
    Validate mobile phone format: DDDDDDDD (8 digits)
    Note: +31-6- prefix is added automatically
    """
    return bool(re.fullmatch(r'[0-9]{8}', phone))

def validate_driving_license(license_number: str) -> bool:
    """
    Validate driving license format: XXDDDDDDD or XDDDDDDDD
    """
    pattern1 = r'[A-Z]{2}[0-9]{7}'  # XXDDDDDDD
    pattern2 = r'[A-Z][0-9]{8}'     # XDDDDDDDD
    return bool(re.fullmatch(pattern1, license_number) or re.fullmatch(pattern2, license_number))

def validate_email(email: str) -> bool:
    """
    Validate email format
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.fullmatch(pattern, email))

def validate_gps_coordinates(latitude: str, longitude: str) -> bool:
    """
    Validate GPS coordinates for Rotterdam region with 5 decimal places
    Rotterdam latitude: ~51.9225, longitude: ~4.47917
    """
    try:
        lat = float(latitude)
        lon = float(longitude)
        
        # Check if coordinates are in Rotterdam region (rough bounds)
        if not (51.8 <= lat <= 52.1 and 4.2 <= lon <= 4.8):
            return False
        
        # Check 5 decimal places precision
        lat_str = f"{lat:.5f}"
        lon_str = f"{lon:.5f}"
        
        return lat_str == latitude and lon_str == longitude
    except ValueError:
        return False

def validate_flexible_gps_coordinate(coord_str: str, coord_type: str) -> bool:
    """
    Flexible GPS coordinate validation
    coord_type: 'lat' for latitude, 'lon' for longitude
    """
    if not coord_str:
        return False
    
    try:
        coord = float(coord_str)
        
        if coord_type == 'lat':
            # Latitude: flexible range around Netherlands
            return 50.0 <= coord <= 54.0
        elif coord_type == 'lon':
            # Longitude: flexible range around Netherlands
            return 3.0 <= coord <= 8.0
        
        return True
    except ValueError:
        return False

def validate_serial_number(serial: str) -> bool:
    """
    Validate scooter serial number: 10-17 alphanumeric characters
    """
    if not serial or len(serial) < 10 or len(serial) > 17:
        return False
    return bool(re.fullmatch(r'[A-Za-z0-9]{10,17}', serial))

def validate_date_iso(date_str: str) -> bool:
    """
    Validate date in ISO 8601 format: YYYY-MM-DD
    """
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except ValueError:
        return False

def validate_date_dutch(date_str: str) -> bool:
    """
    Validate date in Dutch format: DD-MM-YYYY
    """
    try:
        datetime.strptime(date_str, '%d-%m-%Y')
        return True
    except ValueError:
        return False

def validate_flexible_date(date_str: str) -> bool:
    """
    Validate date in multiple flexible formats
    Accepts: DD-MM-YYYY, DD/MM/YYYY, DD.MM.YYYY, DD-MM-YY, DD/MM/YY, DD.MM.YY
    """
    if not date_str:
        return False
    
    # Try different date formats
    formats = [
        '%d-%m-%Y',   # 15-03-2024
        '%d/%m/%Y',   # 15/03/2024
        '%d.%m.%Y',   # 15.03.2024
        '%d-%m-%y',   # 15-03-24
        '%d/%m/%y',   # 15/03/24
        '%d.%m.%y',   # 15.03.24
        '%d %m %Y',   # 15 03 2024
        '%d %m %y',   # 15 03 24
    ]
    
    for fmt in formats:
        try:
            parsed_date = datetime.strptime(date_str, fmt)
            # Convert 2-digit years to 4-digit (assume 20xx for years 00-30, 19xx for 31-99)
            if parsed_date.year < 100:
                if parsed_date.year <= 30:
                    parsed_date = parsed_date.replace(year=parsed_date.year + 2000)
                else:
                    parsed_date = parsed_date.replace(year=parsed_date.year + 1900)
            return True
        except ValueError:
            continue
    
    return False

def convert_dutch_to_iso(dutch_date: str) -> str:
    """
    Convert Dutch date format (DD-MM-YYYY) to ISO format (YYYY-MM-DD)
    """
    try:
        date_obj = datetime.strptime(dutch_date, '%d-%m-%Y')
        return date_obj.strftime('%Y-%m-%d')
    except ValueError:
        return ""

def convert_iso_to_dutch(iso_date: str) -> str:
    """
    Convert ISO date format (YYYY-MM-DD) to Dutch format (DD-MM-YYYY)
    """
    try:
        date_obj = datetime.strptime(iso_date, '%Y-%m-%d')
        return date_obj.strftime('%d-%m-%Y')
    except ValueError:
        return iso_date

def convert_flexible_date_to_iso(date_str: str) -> str:
    """
    Convert flexible date format to ISO format (YYYY-MM-DD)
    """
    if not date_str:
        return ""
    
    formats = [
        '%d-%m-%Y', '%d/%m/%Y', '%d.%m.%Y', '%d-%m-%y', 
        '%d/%m/%y', '%d.%m.%y', '%d %m %Y', '%d %m %y'
    ]
    
    for fmt in formats:
        try:
            parsed_date = datetime.strptime(date_str, fmt)
            # Convert 2-digit years
            if parsed_date.year < 100:
                if parsed_date.year <= 30:
                    parsed_date = parsed_date.replace(year=parsed_date.year + 2000)
                else:
                    parsed_date = parsed_date.replace(year=parsed_date.year + 1900)
            return parsed_date.strftime('%Y-%m-%d')
        except ValueError:
            continue
    
    return ""

def validate_birthday_dutch(birthday: str) -> bool:
    """
    Validate birthday date in Dutch format (must be in the past and reasonable)
    """
    if not validate_date_dutch(birthday):
        return False
    
    try:
        birth_date = datetime.strptime(birthday, '%d-%m-%Y')
        current_date = datetime.now()
        
        # Must be in the past
        if birth_date >= current_date:
            return False
        
        # Must be reasonable (not older than 120 years)
        age_days = (current_date - birth_date).days
        if age_days > 120 * 365:
            return False
        
        # Must be at least 16 years old (for scooter license)
        if age_days < 16 * 365:
            return False
        
        return True
    except ValueError:
        return False

def validate_gender(gender: str) -> bool:
    """
    Validate gender (male or female)
    """
    return gender.lower() in ['male', 'female', 'm', 'f', 'man', 'vrouw']

def validate_city(city: str) -> bool:
    """
    Validate city name (must be from predefined list)
    """
    valid_cities = [
        'Rotterdam', 'Amsterdam', 'Den Haag', 'Utrecht', 'Eindhoven',
        'Groningen', 'Tilburg', 'Almere', 'Breda', 'Nijmegen'
    ]
    return city in valid_cities

def get_valid_cities() -> list:
    """
    Get list of valid city names
    """
    return [
        'Rotterdam', 'Amsterdam', 'Den Haag', 'Utrecht', 'Eindhoven',
        'Groningen', 'Tilburg', 'Almere', 'Breda', 'Nijmegen'
    ]

def validate_percentage(value: str) -> bool:
    """
    Validate percentage value (0-100)
    """
    try:
        val = int(value)
        return 0 <= val <= 100
    except ValueError:
        return False

def validate_positive_integer(value: str) -> bool:
    """
    Validate positive integer
    """
    try:
        val = int(value)
        return val > 0
    except ValueError:
        return False

def validate_positive_float(value: str) -> bool:
    """
    Validate positive float
    """
    try:
        val = float(value)
        return val >= 0.0
    except ValueError:
        return False

def validate_soc_range(min_soc: str, max_soc: str) -> bool:
    """
    Validate State of Charge range (min should be less than max)
    """
    try:
        min_val = int(min_soc)
        max_val = int(max_soc)
        return 0 <= min_val < max_val <= 100
    except ValueError:
        return False

def validate_name(name: str) -> bool:
    """
    Validate first/last name (basic validation)
    """
    if not name or len(name.strip()) < 1:
        return False
    
    # Only letters, spaces, apostrophes, hyphens
    return bool(re.fullmatch(r"[A-Za-z\s'\-]{1,50}", name.strip()))

def validate_street_name(street: str) -> bool:
    """
    Validate street name
    """
    if not street or len(street.strip()) < 1:
        return False
    
    # Letters, numbers, spaces, common punctuation
    return bool(re.fullmatch(r"[A-Za-z0-9\s.\-']{1,100}", street.strip()))

def validate_house_number(house_num: str) -> bool:
    """
    Validate house number (can include letters for apartments)
    """
    if not house_num or len(house_num.strip()) < 1:
        return False
    
    # Numbers, possibly followed by letters
    return bool(re.fullmatch(r'[0-9]+[A-Za-z]?', house_num.strip()))

def validate_brand_model(text: str) -> bool:
    """
    Validate brand/model name
    """
    if not text or len(text.strip()) < 1:
        return False
    
    return bool(re.fullmatch(r"[A-Za-z0-9\s\-_.]{1,50}", text.strip()))

def sanitize_input(text: str) -> str:
    """
    Basic input sanitization to prevent injection attacks
    """
    if not text:
        return ""
    
    # Remove null bytes and control characters
    sanitized = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', str(text))
    
    # Limit length
    return sanitized[:1000]

def validate_search_term(search_term: str) -> bool:
    """
    Validate search term (basic safety check)
    """
    if not search_term or len(search_term.strip()) < 1:
        return False
    
    # Prevent excessively long search terms
    if len(search_term) > 100:
        return False
    
    # Allow alphanumeric, spaces, and common punctuation
    return bool(re.fullmatch(r"[A-Za-z0-9\s@.\-_']{1,100}", search_term.strip()))

def check_back_command(user_input: str) -> bool:
    """
    Check if user wants to go back
    """
    return user_input.lower().strip() in ['terug', 'back', 'b', 't', 'exit', 'quit']

# Validation helper functions
def get_validation_error_message(field: str, value: str) -> str:
    """
    Get appropriate error message for failed validation
    """
    error_messages = {
        'username': 'Gebruikersnaam moet 8-10 tekens zijn, beginnen met letter/underscore, en mag alleen letters, cijfers, _, \', . bevatten',
        'password': 'Wachtwoord moet 12-30 tekens zijn met minimaal 1 kleine letter, 1 hoofdletter, 1 cijfer en 1 speciaal teken',
        'zip_code': 'Postcode moet format DDDDXX hebben (bijv. 1234AB)',
        'mobile_phone': 'Telefoonnummer moet 8 cijfers zijn',
        'driving_license': 'Rijbewijsnummer moet format XXDDDDDDD of XDDDDDDDD hebben',
        'email': 'Ongeldig email adres',
        'birthday': 'Geboortedatum moet geldig zijn en tussen 16-120 jaar geleden (DD-MM-YYYY)',
        'birthday_dutch': 'Geboortedatum moet geldig zijn en tussen 16-120 jaar geleden (DD-MM-YYYY)',
        'flexible_date': 'Datum moet geldig zijn (bijv. 15-03-2024, 15/03/24, 15.03.2024)',
        'gender': 'Geslacht moet \'male\' of \'female\' zijn',
        'city': 'Stad moet een van de geldige steden zijn',
        'gps': 'GPS coördinaten moeten geldig zijn voor Rotterdam gebied met 5 decimalen',
        'serial_number': 'Serienummer moet 10-17 alfanumerieke tekens zijn',
        'date': 'Datum moet format YYYY-MM-DD hebben',
        'date_dutch': 'Datum moet format DD-MM-YYYY hebben',
        'percentage': 'Waarde moet tussen 0 en 100 zijn',
        'positive_integer': 'Waarde moet een positief getal zijn',
        'positive_float': 'Waarde moet een positief getal zijn',
        'name': 'Naam mag alleen letters, spaties, apostroffen en koppeltekens bevatten',
        'search_term': 'Zoekterm bevat ongeldige tekens'
    }
    return error_messages.get(field, f'Ongeldige waarde voor {field}: {value}')

def get_validated_input_with_back(prompt: str, validator_func, validation_type: str, allow_empty: bool = False) -> str:
    """
    Get validated input from user with retry on invalid input and back option
    Returns None if user wants to go back
    """
    while True:
        value = input(f"{prompt}: ").strip()
        
        if check_back_command(value):
            return None
        
        if allow_empty and not value:
            return ""
        
        if validator_func(value):
            return value
        else:
            print(f"❌ {get_validation_error_message(validation_type, value)}")
            print("Probeer opnieuw.")