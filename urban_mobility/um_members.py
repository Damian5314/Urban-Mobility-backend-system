"""
Urban Mobility Members Management Module
Handles all CRUD operations for travellers and scooters with proper validation and permissions
"""

from db import (init_db, add_traveller, get_all_travellers, search_travellers, 
                update_traveller, delete_traveller, add_scooter, get_all_scooters,
                search_scooters, update_scooter, delete_scooter, log_event,
                add_restore_code, get_restore_code, revoke_restore_code)
from input_validation import *
from datetime import datetime
import secrets
import string

# Initialize database on module load
init_db()

# ============================================================================
# TRAVELLER MANAGEMENT FUNCTIONS
# ============================================================================

def create_traveller_interactive(username: str) -> bool:
    """
    Interactive function to create a new traveller with full validation
    Returns True if successful, False otherwise
    """
    print("\n=== Nieuwe Reiziger Toevoegen ===")
    
    try:
        # Collect and validate all required information
        first_name = get_validated_input("Voornaam", validate_name, "name")
        last_name = get_validated_input("Achternaam", validate_name, "name")
        birthday = get_validated_input("Geboortedatum (YYYY-MM-DD)", validate_birthday, "birthday")
        
        # Gender validation with options
        print("Geslacht opties: male, female, m, f, man, vrouw")
        gender = get_validated_input("Geslacht", validate_gender, "gender")
        gender = 'male' if gender.lower() in ['male', 'm', 'man'] else 'female'
        
        street_name = get_validated_input("Straatnaam", validate_street_name, "name")
        house_number = get_validated_input("Huisnummer", validate_house_number, "house_number")
        zip_code = get_validated_input("Postcode (1234AB)", validate_zip_code, "zip_code").upper()
        
        # Show available cities
        cities = get_valid_cities()
        print(f"Beschikbare steden: {', '.join(cities)}")
        city = get_validated_input("Stad", validate_city, "city")
        
        email = get_validated_input("Email adres", validate_email, "email")
        mobile_phone = get_validated_input("Mobiel (8 cijfers, +31-6- wordt toegevoegd)", validate_mobile_phone, "mobile_phone")
        license_number = get_validated_input("Rijbewijsnummer (XXDDDDDDD of XDDDDDDDD)", validate_driving_license, "driving_license").upper()
        
        # Add traveller to database
        customer_id = add_traveller(
            first_name, last_name, birthday, gender, street_name,
            house_number, zip_code, city, email, mobile_phone, license_number
        )
        
        if customer_id:
            print(f"\n✅ Reiziger succesvol toegevoegd!")
            print(f"Customer ID: {customer_id}")
            log_event(f"Nieuwe reiziger toegevoegd", username, 
                     f"ID: {customer_id}, Naam: {first_name} {last_name}, Email: {email}")
            return True
        else:
            print("\n❌ Fout bij toevoegen reiziger")
            return False
            
    except KeyboardInterrupt:
        print("\n\nActie geannuleerd door gebruiker")
        return False
    except Exception as e:
        print(f"\n❌ Onverwachte fout: {e}")
        log_event(f"Fout bij toevoegen reiziger", username, f"Fout: {str(e)}")
        return False

def display_travellers(travellers: list, title: str = "Reizigers"):
    """
    Display travellers in a formatted table
    """
    if not travellers:
        print(f"\nGeen {title.lower()} gevonden.")
        return
    
    print(f"\n=== {title} ({len(travellers)} gevonden) ===")
    print(f"{'ID':<12} {'Naam':<25} {'Email':<30} {'Telefoon':<15} {'Stad':<12}")
    print("-" * 95)
    
    for t in travellers:
        name = f"{t['first_name']} {t['last_name']}"
        phone = f"+31-6-{t['mobile_phone']}"
        print(f"{t['customer_id']:<12} {name:<25} {t['email_address']:<30} {phone:<15} {t['city']:<12}")

def search_travellers_interactive() -> list:
    """
    Interactive traveller search function
    """
    print("\n=== Reiziger Zoeken ===")
    
    search_term = get_validated_input("Zoekterm (naam, email, customer ID)", validate_search_term, "search_term")
    
    results = search_travellers(search_term)
    display_travellers(results, f"Zoekresultaten voor '{search_term}'")
    
    return results

def update_traveller_interactive(username: str) -> bool:
    """
    Interactive function to update traveller information
    """
    print("\n=== Reiziger Bijwerken ===")
    
    # First search for the traveller
    customer_id = input("Customer ID van reiziger om bij te werken: ").strip()
    
    if not customer_id:
        print("Customer ID is verplicht")
        return False
    
    # Get current traveller info
    travellers = get_all_travellers()
    current_traveller = None
    
    for t in travellers:
        if t['customer_id'] == customer_id:
            current_traveller = t
            break
    
    if not current_traveller:
        print(f"Reiziger met ID {customer_id} niet gevonden")
        return False
    
    print(f"\nHuidige gegevens van {current_traveller['first_name']} {current_traveller['last_name']}:")
    print(f"Email: {current_traveller['email_address']}")
    print(f"Telefoon: +31-6-{current_traveller['mobile_phone']}")
    print(f"Adres: {current_traveller['street_name']} {current_traveller['house_number']}, {current_traveller['zip_code']} {current_traveller['city']}")
    
    # Collect updates
    updates = {}
    
    print("\nVoer nieuwe waarden in (laat leeg om ongewijzigd te laten):")
    
    new_email = input(f"Email ({current_traveller['email_address']}): ").strip()
    if new_email:
        if validate_email(new_email):
            updates['email_address'] = new_email
        else:
            print("Ongeldige email, wordt niet bijgewerkt")
    
    new_phone = input(f"Mobiel nummer ({current_traveller['mobile_phone']}): ").strip()
    if new_phone:
        if validate_mobile_phone(new_phone):
            updates['mobile_phone'] = new_phone
        else:
            print("Ongeldig telefoonnummer, wordt niet bijgewerkt")
    
    new_street = input(f"Straatnaam ({current_traveller['street_name']}): ").strip()
    if new_street:
        if validate_street_name(new_street):
            updates['street_name'] = new_street
        else:
            print("Ongeldige straatnaam, wordt niet bijgewerkt")
    
    new_house = input(f"Huisnummer ({current_traveller['house_number']}): ").strip()
    if new_house:
        if validate_house_number(new_house):
            updates['house_number'] = new_house
        else:
            print("Ongeldig huisnummer, wordt niet bijgewerkt")
    
    if not updates:
        print("Geen wijzigingen opgegeven")
        return False
    
    # Apply updates
    success = update_traveller(customer_id, **updates)
    
    if success:
        print("✅ Reiziger succesvol bijgewerkt")
        log_event(f"Reiziger bijgewerkt", username, f"ID: {customer_id}, Velden: {list(updates.keys())}")
        return True
    else:
        print("❌ Fout bij bijwerken reiziger")
        return False

def delete_traveller_interactive(username: str) -> bool:
    """
    Interactive function to delete a traveller
    """
    print("\n=== Reiziger Verwijderen ===")
    
    customer_id = input("Customer ID van reiziger om te verwijderen: ").strip()
    
    if not customer_id:
        print("Customer ID is verplicht")
        return False
    
    # Get traveller info for confirmation
    travellers = get_all_travellers()
    traveller_to_delete = None
    
    for t in travellers:
        if t['customer_id'] == customer_id:
            traveller_to_delete = t
            break
    
    if not traveller_to_delete:
        print(f"Reiziger met ID {customer_id} niet gevonden")
        return False
    
    # Confirmation
    name = f"{traveller_to_delete['first_name']} {traveller_to_delete['last_name']}"
    confirm = input(f"Weet je zeker dat je reiziger {name} (ID: {customer_id}) wilt verwijderen? (ja/nee): ").strip().lower()
    
    if confirm not in ['ja', 'j', 'yes', 'y']:
        print("Verwijdering geannuleerd")
        return False
    
    # Delete traveller
    success = delete_traveller(customer_id)
    
    if success:
        print("✅ Reiziger succesvol verwijderd")
        log_event(f"Reiziger verwijderd", username, f"ID: {customer_id}, Naam: {name}")
        return True
    else:
        print("❌ Fout bij verwijderen reiziger")
        return False

# ============================================================================
# SCOOTER MANAGEMENT FUNCTIONS
# ============================================================================

def create_scooter_interactive(username: str) -> bool:
    """
    Interactive function to create a new scooter with full validation
    """
    print("\n=== Nieuwe Scooter Toevoegen ===")
    
    try:
        brand = get_validated_input("Merk", validate_brand_model, "brand")
        model = get_validated_input("Model", validate_brand_model, "model")
        serial_number = get_validated_input("Serienummer (10-17 tekens)", validate_serial_number, "serial_number")
        
        top_speed = get_validated_input("Topsnelheid (km/h)", validate_positive_integer, "positive_integer")
        battery_capacity = get_validated_input("Batterijcapaciteit (Wh)", validate_positive_integer, "positive_integer")
        state_of_charge = get_validated_input("Huidige batterijlading (0-100%)", validate_percentage, "percentage")
        
        # Target range SoC
        print("Batterijbereik instelling:")
        min_soc = get_validated_input("Minimum batterijniveau (%)", validate_percentage, "percentage")
        max_soc = get_validated_input("Maximum batterijniveau (%)", validate_percentage, "percentage")
        
        if not validate_soc_range(min_soc, max_soc):
            print("❌ Minimum moet kleiner zijn dan maximum")
            return False
        
        target_range_soc = f"{min_soc}-{max_soc}%"
        
        # GPS location
        print("GPS locatie (Rotterdam gebied, 5 decimalen):")
        print("Voorbeeld: Latitude 51.92250, Longitude 4.47917")
        
        while True:
            latitude = input("Latitude: ").strip()
            longitude = input("Longitude: ").strip()
            
            if validate_gps_coordinates(latitude, longitude):
                location = f"{latitude},{longitude}"
                break
            else:
                print(get_validation_error_message('gps', f"{latitude},{longitude}"))
        
        # Optional maintenance date
        maintenance_date = input("Laatste onderhoudsdatum (YYYY-MM-DD, optioneel): ").strip()
        if maintenance_date:
            if not validate_date_iso(maintenance_date):
                print("Ongeldige datum, wordt leeg gelaten")
                maintenance_date = None
        else:
            maintenance_date = None
        
        # Add scooter
        success = add_scooter(
            brand, model, serial_number, int(top_speed), int(battery_capacity),
            int(state_of_charge), target_range_soc, location, maintenance_date
        )
        
        if success:
            print(f"\n✅ Scooter succesvol toegevoegd: {serial_number}")
            log_event(f"Nieuwe scooter toegevoegd", username, 
                     f"Serienummer: {serial_number}, Merk: {brand} {model}, Locatie: {location}")
            return True
        else:
            print("\n❌ Fout bij toevoegen scooter (serienummer mogelijk al in gebruik)")
            return False
            
    except KeyboardInterrupt:
        print("\n\nActie geannuleerd door gebruiker")
        return False
    except Exception as e:
        print(f"\n❌ Onverwachte fout: {e}")
        log_event(f"Fout bij toevoegen scooter", username, f"Fout: {str(e)}")
        return False

def display_scooters(scooters: list, title: str = "Scooters"):
    """
    Display scooters in a formatted table
    """
    if not scooters:
        print(f"\nGeen {title.lower()} gevonden.")
        return
    
    print(f"\n=== {title} ({len(scooters)} gevonden) ===")
    print(f"{'Serienummer':<17} {'Merk':<12} {'Model':<15} {'Batterij %':<10} {'Locatie':<20} {'Status':<12}")
    print("-" * 95)
    
    for s in scooters:
        status = "Buiten dienst" if s['out_of_service_status'] else "In dienst"
        location = s['location'][:18] + "..." if len(s['location']) > 20 else s['location']
        print(f"{s['serial_number']:<17} {s['brand']:<12} {s['model']:<15} {s['state_of_charge']:<10} {location:<20} {status:<12}")

def display_scooter_details(scooter: dict):
    """
    Display detailed scooter information
    """
    print(f"\n=== Scooter Details: {scooter['serial_number']} ===")
    print(f"Merk/Model:        {scooter['brand']} {scooter['model']}")
    print(f"Topsnelheid:       {scooter['top_speed']} km/h")
    print(f"Batterijcapaciteit: {scooter['battery_capacity']} Wh")
    print(f"Huidige lading:    {scooter['state_of_charge']}%")
    print(f"Aanbevolen bereik: {scooter['target_range_soc']}")
    print(f"GPS Locatie:       {scooter['location']}")
    print(f"Status:            {'Buiten dienst' if scooter['out_of_service_status'] else 'In dienst'}")
    print(f"Kilometerstand:    {scooter['mileage']} km")
    print(f"Laatste onderhoud: {scooter['last_maintenance_date'] or 'Niet bekend'}")
    print(f"In dienst sinds:   {scooter['in_service_date'][:10] if scooter['in_service_date'] else 'Onbekend'}")

def search_scooters_interactive() -> list:
    """
    Interactive scooter search function
    """
    print("\n=== Scooter Zoeken ===")
    
    search_term = get_validated_input("Zoekterm (merk, model, serienummer)", validate_search_term, "search_term")
    
    results = search_scooters(search_term)
    display_scooters(results, f"Zoekresultaten voor '{search_term}'")
    
    return results

def update_scooter_interactive(username: str, user_role: str) -> bool:
    """
    Interactive function to update scooter information based on user role
    """
    print("\n=== Scooter Bijwerken ===")
    
    serial_number = input("Serienummer van scooter om bij te werken: ").strip()
    
    if not serial_number:
        print("Serienummer is verplicht")
        return False
    
    # Get current scooter info
    scooters = get_all_scooters()
    current_scooter = None
    
    for s in scooters:
        if s['serial_number'] == serial_number:
            current_scooter = s
            break
    
    if not current_scooter:
        print(f"Scooter met serienummer {serial_number} niet gevonden")
        return False
    
    # Display current info
    display_scooter_details(current_scooter)
    
    # Define which fields can be updated based on role
    if user_role == 'service_engineer':
        updatable_fields = ['state_of_charge', 'location', 'out_of_service_status', 'mileage', 'last_maintenance_date']
        print("\nAls Service Engineer kun je bijwerken: batterijlading, locatie, status, kilometerstand, onderhoudsdatum")
    else:  # super_admin or system_admin
        updatable_fields = ['brand', 'model', 'top_speed', 'battery_capacity', 'state_of_charge', 
                           'target_range_soc', 'location', 'out_of_service_status', 'mileage', 'last_maintenance_date']
        print("\nAls Administrator kun je alle velden bijwerken")
    
    # Collect updates
    updates = {}
    
    print("\nVoer nieuwe waarden in (laat leeg om ongewijzigd te laten):")
    
    if 'state_of_charge' in updatable_fields:
        new_soc = input(f"Batterijlading ({current_scooter['state_of_charge']}%): ").strip()
        if new_soc and validate_percentage(new_soc):
            updates['state_of_charge'] = int(new_soc)
        elif new_soc:
            print("Ongeldige batterijlading")
    
    if 'location' in updatable_fields:
        print("Nieuwe GPS locatie (laat leeg om ongewijzigd te laten):")
        new_lat = input(f"Latitude (huidig: {current_scooter['location'].split(',')[0] if ',' in current_scooter['location'] else ''}): ").strip()
        new_lon = input(f"Longitude (huidig: {current_scooter['location'].split(',')[1] if ',' in current_scooter['location'] else ''}): ").strip()
        
        if new_lat and new_lon:
            if validate_gps_coordinates(new_lat, new_lon):
                updates['location'] = f"{new_lat},{new_lon}"
            else:
                print("Ongeldige GPS coördinaten")
    
    if 'out_of_service_status' in updatable_fields:
        current_status = "buiten dienst" if current_scooter['out_of_service_status'] else "in dienst"
        new_status = input(f"Status ({current_status}) - voer 'uit' in voor buiten dienst, 'in' voor in dienst: ").strip().lower()
        if new_status in ['uit', 'buiten', 'out']:
            updates['out_of_service_status'] = 1
        elif new_status in ['in', 'actief', 'active']:
            updates['out_of_service_status'] = 0
    
    if 'mileage' in updatable_fields:
        new_mileage = input(f"Kilometerstand ({current_scooter['mileage']} km): ").strip()
        if new_mileage and validate_positive_float(new_mileage):
            updates['mileage'] = float(new_mileage)
        elif new_mileage:
            print("Ongeldige kilometerstand")
    
    if 'last_maintenance_date' in updatable_fields:
        new_maintenance = input(f"Laatste onderhoudsdatum ({current_scooter['last_maintenance_date'] or 'Niet bekend'}) (YYYY-MM-DD): ").strip()
        if new_maintenance:
            if validate_date_iso(new_maintenance):
                updates['last_maintenance_date'] = new_maintenance
            else:
                print("Ongeldige datum")
    
    # Admin-only fields
    if user_role in ['super_admin', 'system_admin']:
        if 'brand' in updatable_fields:
            new_brand = input(f"Merk ({current_scooter['brand']}): ").strip()
            if new_brand and validate_brand_model(new_brand):
                updates['brand'] = new_brand
        
        if 'model' in updatable_fields:
            new_model = input(f"Model ({current_scooter['model']}): ").strip()
            if new_model and validate_brand_model(new_model):
                updates['model'] = new_model
    
    if not updates:
        print("Geen wijzigingen opgegeven")
        return False
    
    # Apply updates
    success = update_scooter(serial_number, user_role, **updates)
    
    if success:
        print("✅ Scooter succesvol bijgewerkt")
        log_event(f"Scooter bijgewerkt", username, f"Serienummer: {serial_number}, Velden: {list(updates.keys())}")
        return True
    else:
        print("❌ Fout bij bijwerken scooter")
        return False

def delete_scooter_interactive(username: str) -> bool:
    """
    Interactive function to delete a scooter
    """
    print("\n=== Scooter Verwijderen ===")
    
    serial_number = input("Serienummer van scooter om te verwijderen: ").strip()
    
    if not serial_number:
        print("Serienummer is verplicht")
        return False
    
    # Get scooter info for confirmation
    scooters = get_all_scooters()
    scooter_to_delete = None
    
    for s in scooters:
        if s['serial_number'] == serial_number:
            scooter_to_delete = s
            break
    
    if not scooter_to_delete:
        print(f"Scooter met serienummer {serial_number} niet gevonden")
        return False
    
    # Show scooter details
    display_scooter_details(scooter_to_delete)
    
    # Confirmation
    brand_model = f"{scooter_to_delete['brand']} {scooter_to_delete['model']}"
    confirm = input(f"\nWeet je zeker dat je scooter {brand_model} (serienummer: {serial_number}) wilt verwijderen? (ja/nee): ").strip().lower()
    
    if confirm not in ['ja', 'j', 'yes', 'y']:
        print("Verwijdering geannuleerd")
        return False
    
    # Delete scooter
    success = delete_scooter(serial_number)
    
    if success:
        print("✅ Scooter succesvol verwijderd")
        log_event(f"Scooter verwijderd", username, f"Serienummer: {serial_number}, Merk: {brand_model}")
        return True
    else:
        print("❌ Fout bij verwijderen scooter")
        return False

# ============================================================================
# RESTORE CODE MANAGEMENT FUNCTIONS
# ============================================================================

def generate_restore_code(system_admin_username: str, backup_name: str, super_admin_username: str) -> str:
    """
    Generate a one-time restore code for a system administrator
    """
    # Generate secure random code
    code = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(12))
    
    # Add to database
    success = add_restore_code(code, system_admin_username, backup_name)
    
    if success:
        log_event(f"Restore-code gegenereerd", super_admin_username, 
                 f"Code voor {system_admin_username}, Backup: {backup_name}")
        return code
    else:
        return None

def revoke_restore_code_interactive(username: str) -> bool:
    """
    Interactive function to revoke a restore code
    """
    print("\n=== Restore-Code Intrekken ===")
    
    code = input("Restore-code om in te trekken: ").strip().upper()
    
    if not code:
        print("Restore-code is verplicht")
        return False
    
    # Check if code exists
    code_info = get_restore_code(code)
    if not code_info:
        print("Restore-code niet gevonden of al gebruikt")
        return False
    
    # Show code info
    print(f"Code informatie:")
    print(f"Voor gebruiker: {code_info['system_admin_username']}")
    print(f"Voor backup: {code_info['backup_name']}")
    print(f"Aangemaakt: {code_info['created_date'][:10]}")
    
    # Confirmation
    confirm = input("Weet je zeker dat je deze code wilt intrekken? (ja/nee): ").strip().lower()
    
    if confirm not in ['ja', 'j', 'yes', 'y']:
        print("Intrekking geannuleerd")
        return False
    
    # Revoke code
    success = revoke_restore_code(code)
    
    if success:
        print("✅ Restore-code succesvol ingetrokken")
        log_event(f"Restore-code ingetrokken", username, f"Code: {code}, Was voor: {code_info['system_admin_username']}")
        return True
    else:
        print("❌ Fout bij intrekken restore-code")
        return False

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def get_validated_input(prompt: str, validator_func, validation_type: str) -> str:
    """
    Get validated input from user with retry on invalid input
    """
    while True:
        value = input(f"{prompt}: ").strip()
        if validator_func(value):
            return value
        else:
            print(get_validation_error_message(validation_type, value))

def show_statistics():
    """
    Show system statistics
    """
    travellers = get_all_travellers()
    scooters = get_all_scooters()
    
    print(f"\n=== Systeem Statistieken ===")
    print(f"Totaal aantal reizigers: {len(travellers)}")
    print(f"Totaal aantal scooters: {len(scooters)}")
    
    if scooters:
        in_service = sum(1 for s in scooters if not s['out_of_service_status'])
        out_of_service = len(scooters) - in_service
        avg_battery = sum(s['state_of_charge'] for s in scooters) / len(scooters)
        
        print(f"Scooters in dienst: {in_service}")
        print(f"Scooters buiten dienst: {out_of_service}")
        print(f"Gemiddelde batterijlading: {avg_battery:.1f}%")
    
    if travellers:
        cities = {}
        for t in travellers:
            cities[t['city']] = cities.get(t['city'], 0) + 1
        
        print("Reizigers per stad:")
        for city, count in sorted(cities.items()):
            print(f"  {city}: {count}")