import sqlite3
import os
from datetime import datetime
from encryption import encrypt_data, decrypt_data

DB_PATH = 'data/data.db'

def ensure_data_dir():
    if not os.path.exists('data'):
        os.makedirs('data')

def get_db():
    ensure_data_dir()
    return sqlite3.connect(DB_PATH)

def init_db():
    with get_db() as conn:
        c = conn.cursor()
        
        # Users table
        c.execute('''CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL,
            first_name TEXT,
            last_name TEXT,
            registration_date TEXT
        )''')
        
        # Travellers table with all required fields (sensitive data encrypted)
        c.execute('''CREATE TABLE IF NOT EXISTS travellers (
            customer_id TEXT PRIMARY KEY,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            birthday TEXT NOT NULL,
            gender TEXT NOT NULL,
            street_name TEXT NOT NULL,
            house_number TEXT NOT NULL,
            zip_code TEXT NOT NULL,
            city TEXT NOT NULL,
            email_address TEXT NOT NULL,
            mobile_phone TEXT NOT NULL,
            driving_license_number TEXT NOT NULL,
            registration_date TEXT NOT NULL
        )''')
        
        # Scooters table with all required fields
        c.execute('''CREATE TABLE IF NOT EXISTS scooters (
            serial_number TEXT PRIMARY KEY,
            brand TEXT NOT NULL,
            model TEXT NOT NULL,
            top_speed INTEGER NOT NULL,
            battery_capacity INTEGER NOT NULL,
            state_of_charge INTEGER NOT NULL,
            target_range_soc TEXT NOT NULL,
            location TEXT NOT NULL,
            out_of_service_status INTEGER DEFAULT 0,
            mileage REAL DEFAULT 0.0,
            last_maintenance_date TEXT,
            in_service_date TEXT NOT NULL
        )''')
        
        # Logs table
        c.execute('''CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            username TEXT,
            description TEXT NOT NULL,
            additional_info TEXT,
            suspicious INTEGER DEFAULT 0
        )''')
        
        # Restore codes table
        c.execute('''CREATE TABLE IF NOT EXISTS restore_codes (
            code TEXT PRIMARY KEY,
            system_admin_username TEXT NOT NULL,
            backup_name TEXT NOT NULL,
            created_date TEXT NOT NULL,
            used INTEGER DEFAULT 0
        )''')
        
        conn.commit()

# Helper function to find user by username (handles both encrypted and unencrypted)
def _find_user_row(username):
    with get_db() as conn:
        c = conn.cursor()
        c.execute('SELECT username, password_hash, role, first_name, last_name, registration_date FROM users')
        rows = c.fetchall()
        
        for row in rows:
            try:
                # Try to decrypt the stored username
                decrypted_username = decrypt_data(row[0])
                if decrypted_username.lower() == username.lower():
                    return row
            except:
                # Handle legacy unencrypted data
                if row[0].lower() == username.lower():
                    return row
        return None

# User management functions
def get_user_by_username(username: str):
    row = _find_user_row(username)
    if row:
        try:
            decrypted_username = decrypt_data(row[0])
        except:
            decrypted_username = row[0]  # Legacy unencrypted data
            
        return {
            'username': decrypted_username,
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
            # Encrypt sensitive data
            encrypted_username = encrypt_data(username)
            c.execute('''INSERT INTO users (username, password_hash, role, first_name, last_name, registration_date) 
                        VALUES (?, ?, ?, ?, ?, ?)''',
                      (encrypted_username, password_hash, role, first_name, last_name, datetime.now().isoformat()))
            conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False

def get_all_users():
    with get_db() as conn:
        c = conn.cursor()
        c.execute('SELECT username, role, first_name, last_name, registration_date FROM users')
        rows = c.fetchall()
        users = []
        for row in rows:
            try:
                decrypted_username = decrypt_data(row[0])
                users.append({
                    'username': decrypted_username,
                    'role': row[1],
                    'first_name': row[2],
                    'last_name': row[3],
                    'registration_date': row[4]
                })
            except:
                # Handle legacy unencrypted data
                users.append({
                    'username': row[0],
                    'role': row[1],
                    'first_name': row[2],
                    'last_name': row[3],
                    'registration_date': row[4]
                })
        return users

def update_user(username, new_first_name=None, new_last_name=None):
    try:
        # Find the actual stored username (encrypted or unencrypted)
        row = _find_user_row(username)
        if not row:
            return False
            
        stored_username = row[0]  # Use the actual stored username
        
        with get_db() as conn:
            c = conn.cursor()
            if new_first_name:
                c.execute('UPDATE users SET first_name=? WHERE username=?', (new_first_name, stored_username))
            if new_last_name:
                c.execute('UPDATE users SET last_name=? WHERE username=?', (new_last_name, stored_username))
            conn.commit()
        return True
    except:
        return False

def delete_user(username):
    try:
        # Find the actual stored username (encrypted or unencrypted)
        row = _find_user_row(username)
        if not row:
            return False
            
        stored_username = row[0]  # Use the actual stored username
        
        with get_db() as conn:
            c = conn.cursor()
            c.execute('DELETE FROM users WHERE username=?', (stored_username,))
            conn.commit()
        return True
    except:
        return False

def reset_user_password(username, new_password_hash):
    try:
        # Find the actual stored username (encrypted or unencrypted)
        row = _find_user_row(username)
        if not row:
            return False
            
        stored_username = row[0]  # Use the actual stored username
        
        with get_db() as conn:
            c = conn.cursor()
            c.execute('UPDATE users SET password_hash=? WHERE username=?', (new_password_hash, stored_username))
            conn.commit()
        return True
    except:
        return False

# Traveller management functions
def add_traveller(first_name, last_name, birthday, gender, street_name, house_number, 
                 zip_code, city, email_address, mobile_phone, driving_license_number):
    try:
        import uuid
        customer_id = str(uuid.uuid4())[:12]  # Generate unique customer ID
        
        with get_db() as conn:
            c = conn.cursor()
            # Encrypt sensitive data
            encrypted_email = encrypt_data(email_address)
            encrypted_phone = encrypt_data(mobile_phone)
            encrypted_street = encrypt_data(street_name)
            encrypted_house_number = encrypt_data(house_number)
            
            c.execute('''INSERT INTO travellers 
                        (customer_id, first_name, last_name, birthday, gender, street_name, 
                         house_number, zip_code, city, email_address, mobile_phone, 
                         driving_license_number, registration_date) 
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                      (customer_id, first_name, last_name, birthday, gender, encrypted_street,
                       encrypted_house_number, zip_code, city, encrypted_email, encrypted_phone,
                       driving_license_number, datetime.now().isoformat()))
            conn.commit()
        return customer_id
    except Exception as e:
        print(f"Error adding traveller: {e}")
        return None

def get_traveller_by_id(customer_id):
    """Get a single traveller by customer_id"""
    with get_db() as conn:
        c = conn.cursor()
        c.execute('SELECT * FROM travellers WHERE customer_id=?', (customer_id,))
        row = c.fetchone()
        if row:
            try:
                return {
                    'customer_id': row[0],
                    'first_name': row[1],
                    'last_name': row[2],
                    'birthday': row[3],
                    'gender': row[4],
                    'street_name': decrypt_data(row[5]),
                    'house_number': decrypt_data(row[6]),
                    'zip_code': row[7],
                    'city': row[8],
                    'email_address': decrypt_data(row[9]),
                    'mobile_phone': decrypt_data(row[10]),
                    'driving_license_number': row[11],
                    'registration_date': row[12]
                }
            except:
                # Handle legacy unencrypted data
                return {
                    'customer_id': row[0],
                    'first_name': row[1],
                    'last_name': row[2],
                    'birthday': row[3],
                    'gender': row[4],
                    'street_name': row[5],
                    'house_number': row[6],
                    'zip_code': row[7],
                    'city': row[8],
                    'email_address': row[9],
                    'mobile_phone': row[10],
                    'driving_license_number': row[11],
                    'registration_date': row[12]
                }
        return None

def get_all_travellers():
    with get_db() as conn:
        c = conn.cursor()
        c.execute('SELECT * FROM travellers')
        rows = c.fetchall()
        travellers = []
        for row in rows:
            try:
                travellers.append({
                    'customer_id': row[0],
                    'first_name': row[1],
                    'last_name': row[2],
                    'birthday': row[3],
                    'gender': row[4],
                    'street_name': decrypt_data(row[5]),
                    'house_number': decrypt_data(row[6]),
                    'zip_code': row[7],
                    'city': row[8],
                    'email_address': decrypt_data(row[9]),
                    'mobile_phone': decrypt_data(row[10]),
                    'driving_license_number': row[11],
                    'registration_date': row[12]
                })
            except:
                # Handle legacy unencrypted data
                travellers.append({
                    'customer_id': row[0],
                    'first_name': row[1],
                    'last_name': row[2],
                    'birthday': row[3],
                    'gender': row[4],
                    'street_name': row[5],
                    'house_number': row[6],
                    'zip_code': row[7],
                    'city': row[8],
                    'email_address': row[9],
                    'mobile_phone': row[10],
                    'driving_license_number': row[11],
                    'registration_date': row[12]
                })
        return travellers

def search_travellers(search_term):
    travellers = get_all_travellers()
    results = []
    search_lower = search_term.lower()
    
    for traveller in travellers:
        # Search in multiple fields
        searchable_text = f"{traveller['first_name']} {traveller['last_name']} {traveller['customer_id']} {traveller['email_address']}".lower()
        if search_lower in searchable_text:
            results.append(traveller)
    return results

def update_traveller(customer_id, **kwargs):
    try:
        with get_db() as conn:
            c = conn.cursor()
            update_fields = []
            values = []
            
            for field, value in kwargs.items():
                if field in ['street_name', 'house_number', 'email_address', 'mobile_phone']:
                    # Encrypt sensitive fields
                    values.append(encrypt_data(value))
                else:
                    values.append(value)
                update_fields.append(f"{field}=?")
            
            values.append(customer_id)
            query = f"UPDATE travellers SET {', '.join(update_fields)} WHERE customer_id=?"
            c.execute(query, values)
            conn.commit()
            
            # Check if any rows were affected
            return c.rowcount > 0
    except Exception as e:
        print(f"Error updating traveller: {e}")
        return False

def delete_traveller(customer_id):
    try:
        with get_db() as conn:
            c = conn.cursor()
            c.execute('DELETE FROM travellers WHERE customer_id=?', (customer_id,))
            conn.commit()
            
            # Check if any rows were affected
            return c.rowcount > 0
    except Exception as e:
        print(f"Error deleting traveller: {e}")
        return False

# Scooter management functions
def add_scooter(brand, model, serial_number, top_speed, battery_capacity, 
               state_of_charge, target_range_soc, location, last_maintenance_date=None):
    try:
        with get_db() as conn:
            c = conn.cursor()
            c.execute('''INSERT INTO scooters 
                        (serial_number, brand, model, top_speed, battery_capacity, 
                         state_of_charge, target_range_soc, location, last_maintenance_date, in_service_date) 
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                      (serial_number, brand, model, top_speed, battery_capacity, state_of_charge,
                       target_range_soc, location, last_maintenance_date, datetime.now().isoformat()))
            conn.commit()
        return True
    except Exception as e:
        print(f"Error adding scooter: {e}")
        return False

def get_scooter_by_serial(serial_number):
    """Get a single scooter by serial number"""
    with get_db() as conn:
        c = conn.cursor()
        c.execute('SELECT * FROM scooters WHERE serial_number=?', (serial_number,))
        row = c.fetchone()
        if row:
            return {
                'serial_number': row[0],
                'brand': row[1],
                'model': row[2],
                'top_speed': row[3],
                'battery_capacity': row[4],
                'state_of_charge': row[5],
                'target_range_soc': row[6],
                'location': row[7],
                'out_of_service_status': row[8],
                'mileage': row[9],
                'last_maintenance_date': row[10],
                'in_service_date': row[11]
            }
        return None

def get_all_scooters():
    with get_db() as conn:
        c = conn.cursor()
        c.execute('SELECT * FROM scooters')
        rows = c.fetchall()
        scooters = []
        for row in rows:
            scooters.append({
                'serial_number': row[0],
                'brand': row[1],
                'model': row[2],
                'top_speed': row[3],
                'battery_capacity': row[4],
                'state_of_charge': row[5],
                'target_range_soc': row[6],
                'location': row[7],
                'out_of_service_status': row[8],
                'mileage': row[9],
                'last_maintenance_date': row[10],
                'in_service_date': row[11]
            })
        return scooters

def search_scooters(search_term):
    scooters = get_all_scooters()
    results = []
    search_lower = search_term.lower()
    
    for scooter in scooters:
        searchable_text = f"{scooter['brand']} {scooter['model']} {scooter['serial_number']}".lower()
        if search_lower in searchable_text:
            results.append(scooter)
    return results

def update_scooter(serial_number, user_role, **kwargs):
    # Define which fields each role can update
    service_engineer_fields = ['state_of_charge', 'location', 'out_of_service_status', 'mileage', 'last_maintenance_date']
    admin_fields = service_engineer_fields + ['brand', 'model', 'top_speed', 'battery_capacity', 'target_range_soc']
    
    try:
        with get_db() as conn:
            c = conn.cursor()
            update_fields = []
            values = []
            
            for field, value in kwargs.items():
                # Check role permissions
                if user_role == 'service_engineer' and field not in service_engineer_fields:
                    continue
                elif user_role in ['system_admin', 'super_admin'] and field not in admin_fields:
                    continue
                
                values.append(value)
                update_fields.append(f"{field}=?")
            
            if not update_fields:
                return False
                
            values.append(serial_number)
            query = f"UPDATE scooters SET {', '.join(update_fields)} WHERE serial_number=?"
            c.execute(query, values)
            conn.commit()
            
            # Check if any rows were affected
            return c.rowcount > 0
    except Exception as e:
        print(f"Error updating scooter: {e}")
        return False

def delete_scooter(serial_number):
    try:
        with get_db() as conn:
            c = conn.cursor()
            c.execute('DELETE FROM scooters WHERE serial_number=?', (serial_number,))
            conn.commit()
            
            # Check if any rows were affected
            return c.rowcount > 0
    except Exception as e:
        print(f"Error deleting scooter: {e}")
        return False

# Restore code management
def add_restore_code(code, system_admin_username, backup_name):
    try:
        with get_db() as conn:
            c = conn.cursor()
            c.execute('''INSERT INTO restore_codes (code, system_admin_username, backup_name, created_date) 
                        VALUES (?, ?, ?, ?)''',
                      (code, system_admin_username, backup_name, datetime.now().isoformat()))
            conn.commit()
        return True
    except:
        return False

def get_restore_code(code):
    with get_db() as conn:
        c = conn.cursor()
        c.execute('SELECT * FROM restore_codes WHERE code=? AND used=0', (code,))
        row = c.fetchone()
        if row:
            return {
                'code': row[0],
                'system_admin_username': row[1],
                'backup_name': row[2],
                'created_date': row[3],
                'used': row[4]
            }
        return None

def use_restore_code(code):
    try:
        with get_db() as conn:
            c = conn.cursor()
            c.execute('UPDATE restore_codes SET used=1 WHERE code=?', (code,))
            conn.commit()
        return True
    except:
        return False

def revoke_restore_code(code):
    try:
        with get_db() as conn:
            c = conn.cursor()
            c.execute('DELETE FROM restore_codes WHERE code=?', (code,))
            conn.commit()
        return True
    except:
        return False

# Logging functions
def log_event(description, username="", additional_info="", suspicious=False):
    try:
        with get_db() as conn:
            c = conn.cursor()
            encrypted_description = encrypt_data(description)
            encrypted_additional = encrypt_data(additional_info) if additional_info else ""
            c.execute('''INSERT INTO logs (timestamp, username, description, additional_info, suspicious) 
                        VALUES (?, ?, ?, ?, ?)''',
                      (datetime.now().isoformat(), username, encrypted_description, 
                       encrypted_additional, 1 if suspicious else 0))
            conn.commit()
    except Exception as e:
        print(f"Error logging event: {e}")

def get_logs():
    with get_db() as conn:
        c = conn.cursor()
        c.execute('SELECT * FROM logs ORDER BY timestamp DESC')
        rows = c.fetchall()
        logs = []
        for row in rows:
            try:
                logs.append({
                    'id': row[0],
                    'timestamp': row[1],
                    'username': row[2],
                    'description': decrypt_data(row[3]),
                    'additional_info': decrypt_data(row[4]) if row[4] else "",
                    'suspicious': bool(row[5])
                })
            except:
                # Handle legacy unencrypted logs
                logs.append({
                    'id': row[0],
                    'timestamp': row[1],
                    'username': row[2],
                    'description': row[3],
                    'additional_info': row[4] if row[4] else "",
                    'suspicious': bool(row[5])
                })
        return logs

def get_suspicious_logs():
    logs = get_logs()
    return [log for log in logs if log['suspicious']]