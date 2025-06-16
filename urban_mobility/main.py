import sys
import os
from datetime import datetime

# Import all modules
from auth import (login, register_user, reset_password, change_own_password, 
                 validate_role_action, has_permission)
from db import (init_db, get_all_users, update_user, delete_user, log_event,
               add_traveller, get_all_travellers, search_travellers, update_traveller, delete_traveller,
               add_scooter, get_all_scooters, search_scooters, update_scooter, delete_scooter,
               get_logs, get_suspicious_logs, add_restore_code, get_restore_code, 
               use_restore_code, revoke_restore_code)
from backup import create_backup, restore_backup, list_backups
from input_validation import *
import uuid
import secrets

def clear_screen():
    """Clear terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def pause():
    """Wait for user input"""
    input("\nDruk Enter om door te gaan...")

def show_header(title: str):
    """Show formatted header"""
    print("=" * 70)
    print(f"  {title}")
    print("=" * 70)

def show_suspicious_alerts(username: str, role: str):
    """Show alerts for suspicious activities"""
    if role in ['super_admin', 'system_admin']:
        try:
            suspicious = get_suspicious_logs()
            if suspicious:
                print(f"\n⚠️  WAARSCHUWING: {len(suspicious)} verdachte activiteiten gedetecteerd!")
                print("   Bekijk de logs voor meer details.")
        except:
            pass  # Skip if logs not available

def get_role_menu(role: str) -> list:
    """Get menu options for user role"""
    menus = {
        'super_admin': [
            ("Gebruikersbeheer", "user_management"),
            ("Reiziger beheer", "traveller_management"), 
            ("Scooter beheer", "scooter_management"),
            ("Systeem logs bekijken", "view_logs"),
            ("Backup beheer", "backup_management"),
            ("Restore-code beheer", "restore_code_management"),
            ("Wachtwoord wijzigen", "change_password"),
            ("Systeem statistieken", "show_statistics"),
            ("Uitloggen", "logout")
        ],
        'system_admin': [
            ("Service Engineer beheer", "service_engineer_management"),
            ("Reiziger beheer", "traveller_management"),
            ("Scooter beheer", "scooter_management"), 
            ("Systeem logs bekijken", "view_logs"),
            ("Backup beheer", "backup_management"),
            ("Wachtwoord wijzigen", "change_password"),
            ("Systeem statistieken", "show_statistics"),
            ("Uitloggen", "logout")
        ],
        'service_engineer': [
            ("Scooter informatie zoeken", "search_scooters"),
            ("Scooter informatie bijwerken", "update_scooter_info"),
            ("Reiziger informatie zoeken", "search_travellers"),
            ("Wachtwoord wijzigen", "change_password"),
            ("Uitloggen", "logout")
        ]
    }
    return menus.get(role, [])

def show_main_menu(username: str, role: str):
    """Display main menu and get user choice"""
    clear_screen()
    show_header(f"Urban Mobility Backend - Welkom {username} ({role})")
    
    # Show suspicious activity alerts
    show_suspicious_alerts(username, role)
    
    menu_items = get_role_menu(role)
    print("\nBeschikbare opties:")
    for i, (desc, _) in enumerate(menu_items, 1):
        print(f"  {i}. {desc}")
    
    print(f"  {len(menu_items) + 1}. Afsluiten")
    
    while True:
        try:
            choice = input(f"\nKies een optie (1-{len(menu_items) + 1}): ")
            choice_num = int(choice)
            if 1 <= choice_num <= len(menu_items):
                return menu_items[choice_num - 1][1]
            elif choice_num == len(menu_items) + 1:
                return "exit"
            else:
                print("Ongeldige keuze, probeer opnieuw.")
        except ValueError:
            print("Voer een geldig nummer in.")

# ============================================================================
# USER MANAGEMENT FUNCTIONS
# ============================================================================

def user_management_menu(username: str, role: str):
    """User management submenu"""
    while True:
        clear_screen()
        show_header("Gebruikersbeheer")
        
        print("1. Alle gebruikers bekijken")
        print("2. Nieuwe gebruiker aanmaken")
        print("3. Gebruiker bijwerken") 
        print("4. Gebruiker verwijderen")
        print("5. Wachtwoord resetten")
        print("6. Terug naar hoofdmenu")
        
        choice = input("\nKies een optie (1-6): ")
        
        if choice == "1":
            view_all_users()
        elif choice == "2":
            create_new_user(username, role)
        elif choice == "3":
            update_existing_user(username, role)
        elif choice == "4":
            delete_existing_user(username, role)
        elif choice == "5":
            reset_user_password_interactive(username, role)
        elif choice == "6":
            break
        else:
            print("Ongeldige keuze.")
            pause()

def view_all_users():
    """Display all users"""
    clear_screen()
    show_header("Alle Gebruikers")
    
    try:
        users = get_all_users()
        if not users:
            print("Geen gebruikers gevonden.")
        else:
            print(f"{'Gebruikersnaam':<15} {'Rol':<20} {'Naam':<25} {'Registratie':<20}")
            print("-" * 80)
            for user in users:
                name = f"{user['first_name']} {user['last_name']}"
                reg_date = user['registration_date'][:10] if user['registration_date'] else "Onbekend"
                print(f"{user['username']:<15} {user['role']:<20} {name:<25} {reg_date:<20}")
    except Exception as e:
        print(f"Fout bij ophalen gebruikers: {e}")
    
    pause()

def create_new_user(current_username: str, current_role: str):
    """Create new user"""
    clear_screen()
    show_header("Nieuwe Gebruiker Aanmaken")
    
    try:
        # Get user details
        while True:
            username = input("Gebruikersnaam (8-10 tekens): ").strip()
            if validate_username(username):
                break
            print(get_validation_error_message('username', username))
        
        while True:
            password = input("Wachtwoord (12-30 tekens, complex): ")
            if validate_password(password):
                break
            print(get_validation_error_message('password', password))
        
        # Role selection based on permissions
        available_roles = []
        if current_role == 'super_admin':
            available_roles = ['super_admin', 'system_admin', 'service_engineer']
        elif current_role == 'system_admin':
            available_roles = ['service_engineer']
        
        if not available_roles:
            print("Je hebt geen rechten om gebruikers aan te maken.")
            pause()
            return
        
        print(f"\nBeschikbare rollen: {', '.join(available_roles)}")
        while True:
            role = input("Rol: ").strip()
            if role in available_roles:
                break
            print(f"Ongeldige rol. Kies uit: {', '.join(available_roles)}")
        
        while True:
            first_name = input("Voornaam: ").strip()
            if validate_name(first_name):
                break
            print(get_validation_error_message('name', first_name))
        
        while True:
            last_name = input("Achternaam: ").strip()
            if validate_name(last_name):
                break
            print(get_validation_error_message('name', last_name))
        
        # Create user
        success, message = register_user(username, password, role, first_name, last_name, current_role)
        print(f"\n{message}")
    except Exception as e:
        print(f"Fout bij aanmaken gebruiker: {e}")
    
    pause()

def update_existing_user(current_username: str, current_role: str):
    """Update existing user"""
    clear_screen()
    show_header("Gebruiker Bijwerken")
    
    username = input("Gebruikersnaam om bij te werken: ").strip()
    
    if not username:
        print("Gebruikersnaam is verplicht")
        pause()
        return
    
    try:
        # Get current user info
        users = get_all_users()
        user_to_update = None
        
        for u in users:
            if u['username'].lower() == username.lower():
                user_to_update = u
                break
        
        if not user_to_update:
            print(f"Gebruiker {username} niet gevonden")
            pause()
            return
        
        print(f"\nHuidige gegevens:")
        print(f"Naam: {user_to_update['first_name']} {user_to_update['last_name']}")
        print(f"Rol: {user_to_update['role']}")
        
        print("\nVoer nieuwe waarden in (laat leeg om ongewijzigd te laten):")
        
        new_first_name = input(f"Voornaam ({user_to_update['first_name']}): ").strip()
        new_last_name = input(f"Achternaam ({user_to_update['last_name']}): ").strip()
        
        # Validate new names if provided
        if new_first_name and not validate_name(new_first_name):
            print("Ongeldige voornaam")
            pause()
            return
        
        if new_last_name and not validate_name(new_last_name):
            print("Ongeldige achternaam")
            pause()
            return
        
        # Update user
        success = update_user(
            username,
            new_first_name if new_first_name else None,
            new_last_name if new_last_name else None
        )
        
        if success:
            print("✅ Gebruiker succesvol bijgewerkt")
            log_event(f"Gebruiker bijgewerkt", current_username, f"Gebruiker: {username}")
        else:
            print("❌ Fout bij bijwerken gebruiker")
    except Exception as e:
        print(f"Fout bij bijwerken gebruiker: {e}")
    
    pause()

def delete_existing_user(current_username: str, current_role: str):
    """Delete existing user"""
    clear_screen()
    show_header("Gebruiker Verwijderen")
    
    username = input("Gebruikersnaam om te verwijderen: ").strip()
    
    if not username:
        print("Gebruikersnaam is verplicht")
        pause()
        return
    
    if username.lower() == current_username.lower():
        print("Je kunt jezelf niet verwijderen")
        pause()
        return
    
    try:
        # Get user info
        users = get_all_users()
        user_to_delete = None
        
        for u in users:
            if u['username'].lower() == username.lower():
                user_to_delete = u
                break
        
        if not user_to_delete:
            print(f"Gebruiker {username} niet gevonden")
            pause()
            return
        
        # Confirmation
        name = f"{user_to_delete['first_name']} {user_to_delete['last_name']}"
        confirm = input(f"Weet je zeker dat je gebruiker {name} ({username}) wilt verwijderen? (ja/nee): ").strip().lower()
        
        if confirm not in ['ja', 'j', 'yes', 'y']:
            print("Verwijdering geannuleerd")
            pause()
            return
        
        # Delete user
        success = delete_user(username)
        
        if success:
            print("✅ Gebruiker succesvol verwijderd")
            log_event(f"Gebruiker verwijderd", current_username, f"Verwijderde gebruiker: {username}")
        else:
            print("❌ Fout bij verwijderen gebruiker")
    except Exception as e:
        print(f"Fout bij verwijderen gebruiker: {e}")
    
    pause()

def reset_user_password_interactive(current_username: str, current_role: str):
    """Reset user password interactively"""
    clear_screen()
    show_header("Wachtwoord Resetten")
    
    username = input("Gebruikersnaam voor wachtwoord reset: ").strip()
    
    if not username:
        print("Gebruikersnaam is verplicht")
        pause()
        return
    
    try:
        success, result = reset_password(username, current_role)
        
        if success:
            print(f"✅ Wachtwoord succesvol gereset voor {username}")
            print(f"Tijdelijk wachtwoord: {result}")
            print("Gebruiker moet dit wachtwoord bij eerste login wijzigen")
        else:
            print(f"❌ Fout bij resetten wachtwoord: {result}")
    except Exception as e:
        print(f"Fout bij resetten wachtwoord: {e}")
    
    pause()

# ============================================================================
# TRAVELLER MANAGEMENT FUNCTIONS
# ============================================================================

def traveller_management_menu(username: str, role: str):
    """Traveller management submenu"""
    while True:
        clear_screen()
        show_header("Reiziger Beheer")
        
        print("1. Alle reizigers bekijken")
        print("2. Reiziger zoeken")
        print("3. Nieuwe reiziger toevoegen")
        print("4. Reiziger bijwerken")
        print("5. Reiziger verwijderen") 
        print("6. Terug naar hoofdmenu")
        
        choice = input("\nKies een optie (1-6): ")
        
        if choice == "1":
            view_all_travellers_menu()
        elif choice == "2":
            search_travellers_menu()
        elif choice == "3":
            create_traveller_menu(username)
        elif choice == "4":
            update_traveller_menu(username)
        elif choice == "5":
            delete_traveller_menu(username)
        elif choice == "6":
            break
        else:
            print("Ongeldige keuze.")
            pause()

def view_all_travellers_menu():
    """Display all travellers"""
    clear_screen()
    show_header("Alle Reizigers")
    
    try:
        travellers = get_all_travellers()
        if not travellers:
            print("Geen reizigers gevonden.")
        else:
            print(f"{'ID':<12} {'Naam':<25} {'Email':<30} {'Telefoon':<15} {'Stad':<12}")
            print("-" * 95)
            
            for t in travellers:
                name = f"{t['first_name']} {t['last_name']}"
                phone = f"+31-6-{t['mobile_phone']}"
                print(f"{t['customer_id']:<12} {name:<25} {t['email_address']:<30} {phone:<15} {t['city']:<12}")
    except Exception as e:
        print(f"Fout bij ophalen reizigers: {e}")
    
    pause()

def search_travellers_menu():
    """Search travellers"""
    clear_screen()
    show_header("Reiziger Zoeken")
    
    try:
        while True:
            search_term = input("Zoekterm (naam, email, customer ID): ").strip()
            if validate_search_term(search_term):
                break
            print(get_validation_error_message('search_term', search_term))
        
        results = search_travellers(search_term)
        
        if not results:
            print("Geen reizigers gevonden.")
        else:
            print(f"\n{len(results)} resultaten gevonden:")
            print(f"{'ID':<12} {'Naam':<25} {'Email':<30} {'Telefoon':<15}")
            print("-" * 85)
            for t in results:
                name = f"{t['first_name']} {t['last_name']}"
                phone = f"+31-6-{t['mobile_phone']}"
                print(f"{t['customer_id']:<12} {name:<25} {t['email_address']:<30} {phone:<15}")
    except Exception as e:
        print(f"Fout bij zoeken reizigers: {e}")
    
    pause()

def create_traveller_menu(username: str):
    """Add new traveller"""
    clear_screen()
    show_header("Nieuwe Reiziger Toevoegen")
    
    try:
        # Collect all required information
        while True:
            first_name = input("Voornaam: ").strip()
            if validate_name(first_name):
                break
            print(get_validation_error_message('name', first_name))
        
        while True:
            last_name = input("Achternaam: ").strip()
            if validate_name(last_name):
                break
            print(get_validation_error_message('name', last_name))
        
        while True:
            birthday = input("Geboortedatum (YYYY-MM-DD): ").strip()
            if validate_birthday(birthday):
                break
            print(get_validation_error_message('birthday', birthday))
        
        while True:
            gender = input("Geslacht (male/female): ").strip().lower()
            if validate_gender(gender):
                gender = 'male' if gender in ['male', 'm', 'man'] else 'female'
                break
            print(get_validation_error_message('gender', gender))
        
        while True:
            street_name = input("Straatnaam: ").strip()
            if validate_street_name(street_name):
                break
            print(get_validation_error_message('name', street_name))
        
        while True:
            house_number = input("Huisnummer: ").strip()
            if validate_house_number(house_number):
                break
            print("Huisnummer moet geldig zijn (cijfers, evt. gevolgd door letter)")
        
        while True:
            zip_code = input("Postcode (1234AB): ").strip().upper()
            if validate_zip_code(zip_code):
                break
            print(get_validation_error_message('zip_code', zip_code))
        
        print(f"\nBeschikbare steden: {', '.join(get_valid_cities())}")
        while True:
            city = input("Stad: ").strip()
            if validate_city(city):
                break
            print(get_validation_error_message('city', city))
        
        while True:
            email = input("Email adres: ").strip()
            if validate_email(email):
                break
            print(get_validation_error_message('email', email))
        
        while True:
            mobile_phone = input("Mobiel nummer (8 cijfers, +31-6- wordt automatisch toegevoegd): ").strip()
            if validate_mobile_phone(mobile_phone):
                break
            print(get_validation_error_message('mobile_phone', mobile_phone))
        
        while True:
            license_number = input("Rijbewijsnummer (XXDDDDDDD of XDDDDDDDD): ").strip().upper()
            if validate_driving_license(license_number):
                break
            print(get_validation_error_message('driving_license', license_number))
        
        # Add traveller
        customer_id = add_traveller(first_name, last_name, birthday, gender, street_name, 
                                   house_number, zip_code, city, email, mobile_phone, license_number)
        
        if customer_id:
            print(f"\n✅ Reiziger succesvol toegevoegd met ID: {customer_id}")
            log_event(f"Nieuwe reiziger toegevoegd", username, f"Customer ID: {customer_id}, Naam: {first_name} {last_name}")
        else:
            print("\n❌ Fout bij toevoegen reiziger.")
    except Exception as e:
        print(f"Fout bij toevoegen reiziger: {e}")
    
    pause()

def update_traveller_menu(username: str):
    """Update traveller"""
    clear_screen()
    show_header("Reiziger Bijwerken")
    
    customer_id = input("Customer ID van reiziger om bij te werken: ").strip()
    
    if not customer_id:
        print("Customer ID is verplicht")
        pause()
        return
    
    try:
        # Get current traveller info
        travellers = get_all_travellers()
        current_traveller = None
        
        for t in travellers:
            if t['customer_id'] == customer_id:
                current_traveller = t
                break
        
        if not current_traveller:
            print(f"Reiziger met ID {customer_id} niet gevonden")
            pause()
            return
        
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
        
        if not updates:
            print("Geen wijzigingen opgegeven")
            pause()
            return
        
        # Apply updates
        success = update_traveller(customer_id, **updates)
        
        if success:
            print("✅ Reiziger succesvol bijgewerkt")
            log_event(f"Reiziger bijgewerkt", username, f"ID: {customer_id}, Velden: {list(updates.keys())}")
        else:
            print("❌ Fout bij bijwerken reiziger")
    except Exception as e:
        print(f"Fout bij bijwerken reiziger: {e}")
    
    pause()

def delete_traveller_menu(username: str):
    """Delete traveller"""
    clear_screen()
    show_header("Reiziger Verwijderen")
    
    customer_id = input("Customer ID van reiziger om te verwijderen: ").strip()
    
    if not customer_id:
        print("Customer ID is verplicht")
        pause()
        return
    
    try:
        # Get traveller info for confirmation
        travellers = get_all_travellers()
        traveller_to_delete = None
        
        for t in travellers:
            if t['customer_id'] == customer_id:
                traveller_to_delete = t
                break
        
        if not traveller_to_delete:
            print(f"Reiziger met ID {customer_id} niet gevonden")
            pause()
            return
        
        # Confirmation
        name = f"{traveller_to_delete['first_name']} {traveller_to_delete['last_name']}"
        confirm = input(f"Weet je zeker dat je reiziger {name} (ID: {customer_id}) wilt verwijderen? (ja/nee): ").strip().lower()
        
        if confirm not in ['ja', 'j', 'yes', 'y']:
            print("Verwijdering geannuleerd")
            pause()
            return
        
        # Delete traveller
        success = delete_traveller(customer_id)
        
        if success:
            print("✅ Reiziger succesvol verwijderd")
            log_event(f"Reiziger verwijderd", username, f"ID: {customer_id}, Naam: {name}")
        else:
            print("❌ Fout bij verwijderen reiziger")
    except Exception as e:
        print(f"Fout bij verwijderen reiziger: {e}")
    
    pause()

# ============================================================================
# SCOOTER MANAGEMENT FUNCTIONS  
# ============================================================================

def scooter_management_menu(username: str, role: str):
    """Scooter management submenu"""
    while True:
        clear_screen()
        show_header("Scooter Beheer")
        
        options = ["Alle scooters bekijken", "Scooter zoeken"]
        
        if role in ['super_admin', 'system_admin']:
            options.extend(["Nieuwe scooter toevoegen", "Scooter bijwerken", "Scooter verwijderen"])
        elif role == 'service_engineer':
            options.append("Scooter status bijwerken")
        
        options.append("Terug naar hoofdmenu")
        
        for i, option in enumerate(options, 1):
            print(f"{i}. {option}")
        
        choice = input(f"\nKies een optie (1-{len(options)}): ")
        
        try:
            choice_num = int(choice)
            if choice_num == 1:
                view_all_scooters_menu()
            elif choice_num == 2:
                search_scooters_menu()
            elif choice_num == 3 and role in ['super_admin', 'system_admin']:
                create_scooter_menu(username)
            elif choice_num == 4 and role in ['super_admin', 'system_admin']:
                update_scooter_menu(username, role)
            elif choice_num == 3 and role == 'service_engineer':
                update_scooter_menu(username, role)
            elif choice_num == 5 and role in ['super_admin', 'system_admin']:
                delete_scooter_menu(username)
            elif choice_num == len(options):
                break
            else:
                print("Ongeldige keuze.")
                pause()
        except ValueError:
            print("Voer een geldig nummer in.")
            pause()

def view_all_scooters_menu():
    """Display all scooters"""
    clear_screen()
    show_header("Alle Scooters")
    
    try:
        scooters = get_all_scooters()
        if not scooters:
            print("Geen scooters gevonden.")
        else:
            print(f"{'Serienummer':<15} {'Merk':<12} {'Model':<15} {'Batterij %':<10} {'Locatie':<20} {'Status':<10}")
            print("-" * 90)
            for s in scooters:
                status = "Buiten dienst" if s['out_of_service_status'] else "In dienst"
                location = s['location'][:18] + "..." if len(s['location']) > 20 else s['location']
                print(f"{s['serial_number']:<15} {s['brand']:<12} {s['model']:<15} {s['state_of_charge']:<10} {location:<20} {status:<10}")
    except Exception as e:
        print(f"Fout bij ophalen scooters: {e}")
    
    pause()

def search_scooters_menu():
    """Search scooters"""
    clear_screen()
    show_header("Scooter Zoeken")
    
    try:
        while True:
            search_term = input("Zoekterm (merk, model, serienummer): ").strip()
            if validate_search_term(search_term):
                break
            print(get_validation_error_message('search_term', search_term))
        
        results = search_scooters(search_term)
        
        if not results:
            print("Geen scooters gevonden.")
        else:
            print(f"\n{len(results)} resultaten gevonden:")
            print(f"{'Serienummer':<15} {'Merk':<12} {'Model':<15} {'Batterij %':<10} {'Status':<10}")
            print("-" * 70)
            for s in results:
                status = "Buiten dienst" if s['out_of_service_status'] else "In dienst"
                print(f"{s['serial_number']:<15} {s['brand']:<12} {s['model']:<15} {s['state_of_charge']:<10} {status:<10}")
    except Exception as e:
        print(f"Fout bij zoeken scooters: {e}")
    
    pause()

def create_scooter_menu(username: str):
    """Add new scooter"""
    clear_screen()
    show_header("Nieuwe Scooter Toevoegen")
    
    try:
        while True:
            brand = input("Merk: ").strip()
            if validate_brand_model(brand):
                break
            print("Merknaam mag alleen letters, cijfers, spaties en - _ . bevatten")
        
        while True:
            model = input("Model: ").strip()
            if validate_brand_model(model):
                break
            print("Modelnaam mag alleen letters, cijfers, spaties en - _ . bevatten")
        
        while True:
            serial_number = input("Serienummer (10-17 tekens): ").strip()
            if validate_serial_number(serial_number):
                break
            print(get_validation_error_message('serial_number', serial_number))
        
        while True:
            top_speed = input("Topsnelheid (km/h): ").strip()
            if validate_positive_integer(top_speed):
                break
            print("Topsnelheid moet een positief getal zijn")
        
        while True:
            battery_capacity = input("Batterijcapaciteit (Wh): ").strip()
            if validate_positive_integer(battery_capacity):
                break
            print("Batterijcapaciteit moet een positief getal zijn")
        
        while True:
            state_of_charge = input("Huidige batterijlading (0-100%): ").strip()
            if validate_percentage(state_of_charge):
                break
            print(get_validation_error_message('percentage', state_of_charge))
        
        while True:
            min_soc = input("Minimum batterijniveau (%): ").strip()
            max_soc = input("Maximum batterijniveau (%): ").strip()
            if validate_soc_range(min_soc, max_soc):
                target_range_soc = f"{min_soc}-{max_soc}%"
                break
            print("Ongeldige batterijbereik (min moet kleiner zijn dan max, beide 0-100)")
        
        print("GPS locatie (Rotterdam gebied, 5 decimalen nauwkeurig)")
        while True:
            latitude = input("Latitude (bijv. 51.92250): ").strip()
            longitude = input("Longitude (bijv. 4.47917): ").strip()
            if validate_gps_coordinates(latitude, longitude):
                location = f"{latitude},{longitude}"
                break
            print(get_validation_error_message('gps', f"{latitude},{longitude}"))
        
        maintenance_date = input("Laatste onderhoudsdatum (YYYY-MM-DD, optioneel): ").strip()
        if maintenance_date and not validate_date_iso(maintenance_date):
            print("Ongeldige datum, wordt leeg gelaten")
            maintenance_date = None
        
        # Add scooter
        success = add_scooter(brand, model, serial_number, int(top_speed), int(battery_capacity),
                             int(state_of_charge), target_range_soc, location, maintenance_date)
        
        if success:
            print(f"\n✅ Scooter succesvol toegevoegd: {serial_number}")
            log_event(f"Nieuwe scooter toegevoegd", username, f"Serienummer: {serial_number}, Merk: {brand} {model}")
        else:
            print("\n❌ Fout bij toevoegen scooter.")
    except Exception as e:
        print(f"Fout bij toevoegen scooter: {e}")
    
    pause()

def update_scooter_menu(username: str, role: str):
    """Update scooter"""
    clear_screen()
    show_header("Scooter Bijwerken")
    
    serial_number = input("Serienummer van scooter om bij te werken: ").strip()
    
    if not serial_number:
        print("Serienummer is verplicht")
        pause()
        return
    
    try:
        # Get current scooter info
        scooters = get_all_scooters()
        current_scooter = None
        
        for s in scooters:
            if s['serial_number'] == serial_number:
                current_scooter = s
                break
        
        if not current_scooter:
            print(f"Scooter met serienummer {serial_number} niet gevonden")
            pause()
            return
        
        print(f"\nHuidige gegevens van {current_scooter['brand']} {current_scooter['model']}:")
        print(f"Batterij: {current_scooter['state_of_charge']}%")
        print(f"Locatie: {current_scooter['location']}")
        print(f"Status: {'Buiten dienst' if current_scooter['out_of_service_status'] else 'In dienst'}")
        
        # Collect updates
        updates = {}
        
        print("\nVoer nieuwe waarden in (laat leeg om ongewijzigd te laten):")
        
        new_soc = input(f"Batterijlading ({current_scooter['state_of_charge']}%): ").strip()
        if new_soc and validate_percentage(new_soc):
            updates['state_of_charge'] = int(new_soc)
        elif new_soc:
            print("Ongeldige batterijlading")
        
        if not updates:
            print("Geen wijzigingen opgegeven")
            pause()
            return
        
        # Apply updates
        success = update_scooter(serial_number, role, **updates)
        
        if success:
            print("✅ Scooter succesvol bijgewerkt")
            log_event(f"Scooter bijgewerkt", username, f"Serienummer: {serial_number}, Velden: {list(updates.keys())}")
        else:
            print("❌ Fout bij bijwerken scooter")
    except Exception as e:
        print(f"Fout bij bijwerken scooter: {e}")
    
    pause()

def delete_scooter_menu(username: str):
    """Delete scooter"""
    clear_screen()
    show_header("Scooter Verwijderen")
    
    serial_number = input("Serienummer van scooter om te verwijderen: ").strip()
    
    if not serial_number:
        print("Serienummer is verplicht")
        pause()
        return
    
    try:
        # Get scooter info for confirmation
        scooters = get_all_scooters()
        scooter_to_delete = None
        
        for s in scooters:
            if s['serial_number'] == serial_number:
                scooter_to_delete = s
                break
        
        if not scooter_to_delete:
            print(f"Scooter met serienummer {serial_number} niet gevonden")
            pause()
            return
        
        # Confirmation
        brand_model = f"{scooter_to_delete['brand']} {scooter_to_delete['model']}"
        confirm = input(f"Weet je zeker dat je scooter {brand_model} (serienummer: {serial_number}) wilt verwijderen? (ja/nee): ").strip().lower()
        
        if confirm not in ['ja', 'j', 'yes', 'y']:
            print("Verwijdering geannuleerd")
            pause()
            return
        
        # Delete scooter
        success = delete_scooter(serial_number)
        
        if success:
            print("✅ Scooter succesvol verwijderd")
            log_event(f"Scooter verwijderd", username, f"Serienummer: {serial_number}, Merk: {brand_model}")
        else:
            print("❌ Fout bij verwijderen scooter")
    except Exception as e:
        print(f"Fout bij verwijderen scooter: {e}")
    
    pause()

# ============================================================================
# BACKUP MANAGEMENT FUNCTIONS
# ============================================================================

def backup_management_menu(username: str, role: str):
    """Backup management submenu"""
    while True:
        clear_screen()
        show_header("Backup Beheer")
        
        print("1. Backup maken")
        print("2. Beschikbare backups bekijken")
        print("3. Backup herstellen")
        if role == 'super_admin':
            print("4. Backup verwijderen")
        print("0. Terug naar hoofdmenu")
        
        choice = input("\nKies een optie: ")
        
        if choice == "1":
            create_new_backup(username)
        elif choice == "2":
            view_available_backups()
        elif choice == "3":
            restore_from_backup_interactive(username, role)
        elif choice == "4" and role == 'super_admin':
            delete_backup_interactive(username)
        elif choice == "0":
            break
        else:
            print("Ongeldige keuze.")
            pause()

def create_new_backup(username: str):
    """Create new backup"""
    clear_screen()
    show_header("Backup Maken")
    
    try:
        backup_name = create_backup(username)
        print(f"✅ Backup succesvol gemaakt: {backup_name}")
        log_event(f"Backup gemaakt", username, f"Backup: {backup_name}")
    except Exception as e:
        print(f"❌ Fout bij maken backup: {e}")
    
    pause()

def view_available_backups():
    """View available backups"""
    clear_screen()
    show_header("Beschikbare Backups")
    
    try:
        backups = list_backups()
        
        if not backups:
            print("Geen backups gevonden.")
        else:
            print(f"{'Bestandsnaam':<25} {'Aangemaakt':<20} {'Grootte (MB)':<12} {'Door':<15}")
            print("-" * 75)
            
            for backup in backups:
                size_mb = round(backup['size'] / (1024 * 1024), 2)
                created_date = backup['created'].strftime('%Y-%m-%d %H:%M')
                print(f"{backup['filename']:<25} {created_date:<20} {size_mb:<12} {backup['creator']:<15}")
    except Exception as e:
        print(f"Fout bij ophalen backups: {e}")
    
    pause()

def restore_from_backup_interactive(username: str, role: str):
    """Restore from backup interactively"""
    clear_screen()
    show_header("Backup Herstellen")
    
    try:
        # Show available backups
        backups = list_backups()
        
        if not backups:
            print("Geen backups beschikbaar.")
            pause()
            return
        
        print("Beschikbare backups:")
        for i, backup in enumerate(backups, 1):
            created_date = backup['created'].strftime('%Y-%m-%d %H:%M')
            print(f"{i}. {backup['filename']} (aangemaakt: {created_date})")
        
        choice = int(input(f"\nKies backup (1-{len(backups)}): ")) - 1
        if choice < 0 or choice >= len(backups):
            print("Ongeldige keuze.")
            pause()
            return
        
        selected_backup = backups[choice]['filename']
        
        # Check if restore code is needed
        restore_code = None
        if role != 'super_admin':
            restore_code = input("Voer restore-code in: ").strip()
            if not restore_code:
                print("Restore-code is verplicht voor System Administrators.")
                pause()
                return
        
        # Confirm restore
        confirm = input(f"Weet je zeker dat je backup {selected_backup} wilt herstellen? Dit overschrijft de huidige data! (ja/nee): ").strip().lower()
        
        if confirm not in ['ja', 'j', 'yes', 'y']:
            print("Restore geannuleerd.")
            pause()
            return
        
        # Perform restore
        success = restore_backup(selected_backup, username, restore_code, role == 'super_admin')
        
        if success:
            print("✅ Backup succesvol hersteld!")
        else:
            print("❌ Backup herstellen mislukt.")
    except Exception as e:
        print(f"Fout bij herstellen backup: {e}")
    
    pause()

def delete_backup_interactive(username: str):
    """Delete backup interactively (super admin only)"""
    clear_screen()
    show_header("Backup Verwijderen")
    
    try:
        backups = list_backups()
        
        if not backups:
            print("Geen backups beschikbaar.")
            pause()
            return
        
        print("Beschikbare backups:")
        for i, backup in enumerate(backups, 1):
            created_date = backup['created'].strftime('%Y-%m-%d %H:%M')
            print(f"{i}. {backup['filename']} (aangemaakt: {created_date})")
        
        choice = int(input(f"\nKies backup om te verwijderen (1-{len(backups)}): ")) - 1
        if choice < 0 or choice >= len(backups):
            print("Ongeldige keuze.")
            pause()
            return
        
        selected_backup = backups[choice]['filename']
        
        # Confirm deletion
        confirm = input(f"Weet je zeker dat je backup {selected_backup} wilt verwijderen? (ja/nee): ").strip().lower()
        
        if confirm not in ['ja', 'j', 'yes', 'y']:
            print("Verwijdering geannuleerd.")
            pause()
            return
        
        # Delete backup
        backup_path = os.path.join('backups', selected_backup)
        if os.path.exists(backup_path):
            os.remove(backup_path)
            print("✅ Backup succesvol verwijderd!")
            log_event(f"Backup verwijderd", username, f"Backup: {selected_backup}")
        else:
            print("❌ Backup bestand niet gevonden.")
    except Exception as e:
        print(f"Fout bij verwijderen backup: {e}")
    
    pause()

# ============================================================================
# RESTORE CODE MANAGEMENT
# ============================================================================

def restore_code_management_menu(username: str, role: str):
    """Restore code management (super admin only)"""
    while True:
        clear_screen()
        show_header("Restore-Code Beheer")
        
        print("1. Restore-code genereren")
        print("2. Restore-code intrekken")
        print("3. Terug naar hoofdmenu")
        
        choice = input("\nKies een optie (1-3): ")
        
        if choice == "1":
            generate_restore_code_interactive(username)
        elif choice == "2":
            revoke_restore_code_interactive_menu(username)
        elif choice == "3":
            break
        else:
            print("Ongeldige keuze.")
            pause()

def generate_restore_code_interactive(username: str):
    """Generate restore code interactively"""
    clear_screen()
    show_header("Restore-Code Genereren")
    
    try:
        # Show available backups
        backups = list_backups()
        
        if not backups:
            print("Geen backups beschikbaar.")
            pause()
            return
        
        # Show system admins
        users = get_all_users()
        system_admins = [u for u in users if u['role'] == 'system_admin']
        
        if not system_admins:
            print("Geen System Administrators gevonden.")
            pause()
            return
        
        print("System Administrators:")
        for i, admin in enumerate(system_admins, 1):
            print(f"{i}. {admin['username']} ({admin['first_name']} {admin['last_name']})")
        
        admin_choice = int(input(f"\nKies System Administrator (1-{len(system_admins)}): ")) - 1
        if admin_choice < 0 or admin_choice >= len(system_admins):
            print("Ongeldige keuze.")
            pause()
            return
        
        selected_admin = system_admins[admin_choice]['username']
        
        print("\nBeschikbare backups:")
        for i, backup in enumerate(backups, 1):
            created_date = backup['created'].strftime('%Y-%m-%d %H:%M')
            print(f"{i}. {backup['filename']} (aangemaakt: {created_date})")
        
        backup_choice = int(input(f"\nKies backup (1-{len(backups)}): ")) - 1
        if backup_choice < 0 or backup_choice >= len(backups):
            print("Ongeldige keuze.")
            pause()
            return
        
        selected_backup = backups[backup_choice]['filename']
        
        # Generate code
        code = ''.join(secrets.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789') for _ in range(12))
        success = add_restore_code(code, selected_admin, selected_backup)
        
        if success:
            print(f"\n✅ Restore-code gegenereerd!")
            print(f"Code: {code}")
            print(f"Voor: {selected_admin}")
            print(f"Backup: {selected_backup}")
            print("\nDeze code is eenmalig bruikbaar!")
            log_event(f"Restore-code gegenereerd", username, f"Code voor {selected_admin}, Backup: {selected_backup}")
        else:
            print("❌ Fout bij genereren restore-code.")
    except Exception as e:
        print(f"Fout bij genereren restore-code: {e}")
    
    pause()

def revoke_restore_code_interactive_menu(username: str):
    """Revoke restore code"""
    clear_screen()
    show_header("Restore-Code Intrekken")
    
    code = input("Restore-code om in te trekken: ").strip().upper()
    
    if not code:
        print("Restore-code is verplicht")
        pause()
        return
    
    try:
        # Check if code exists
        code_info = get_restore_code(code)
        if not code_info:
            print("Restore-code niet gevonden of al gebruikt")
            pause()
            return
        
        # Show code info
        print(f"Code informatie:")
        print(f"Voor gebruiker: {code_info['system_admin_username']}")
        print(f"Voor backup: {code_info['backup_name']}")
        print(f"Aangemaakt: {code_info['created_date'][:10]}")
        
        # Confirmation
        confirm = input("Weet je zeker dat je deze code wilt intrekken? (ja/nee): ").strip().lower()
        
        if confirm not in ['ja', 'j', 'yes', 'y']:
            print("Intrekking geannuleerd")
            pause()
            return
        
        # Revoke code
        success = revoke_restore_code(code)
        
        if success:
            print("✅ Restore-code succesvol ingetrokken")
            log_event(f"Restore-code ingetrokken", username, f"Code: {code}, Was voor: {code_info['system_admin_username']}")
        else:
            print("❌ Fout bij intrekken restore-code")
    except Exception as e:
        print(f"Fout bij intrekken restore-code: {e}")
    
    pause()

# ============================================================================
# LOGGING FUNCTIONS
# ============================================================================

def view_logs_menu(username: str, role: str):
    """View system logs"""
    clear_screen()
    show_header("Systeem Logs")
    
    try:
        logs = get_logs()
        if not logs:
            print("Geen logs gevonden.")
        else:
            print(f"{'#':<5} {'Datum/Tijd':<20} {'Gebruiker':<15} {'Beschrijving':<40} {'Verdacht':<8}")
            print("-" * 95)
            
            # Show last 25 logs
            for i, log in enumerate(logs[:25], 1):
                timestamp = log['timestamp'][:19].replace('T', ' ')
                username_short = log['username'][:13] + "..." if len(log['username']) > 15 else log['username']
                desc_short = log['description'][:38] + "..." if len(log['description']) > 40 else log['description']
                suspicious = "⚠️ JA" if log['suspicious'] else "NEE"
                
                print(f"{i:<5} {timestamp:<20} {username_short:<15} {desc_short:<40} {suspicious:<8}")
            
            if len(logs) > 25:
                print(f"\n... en {len(logs) - 25} meer logs")
            
            # Show suspicious activity summary
            suspicious_logs = [log for log in logs if log['suspicious']]
            if suspicious_logs:
                print(f"\n⚠️  Verdachte activiteiten: {len(suspicious_logs)}")
    except Exception as e:
        print(f"Fout bij ophalen logs: {e}")
    
    pause()

# ============================================================================
# PASSWORD CHANGE FUNCTION
# ============================================================================

def change_password_menu(username: str, role: str):
    """Change user password"""
    clear_screen()
    show_header("Wachtwoord Wijzigen")
    
    if username == 'super_admin':
        print("Super admin wachtwoord kan niet gewijzigd worden.")
        pause()
        return
    
    try:
        old_password = input("Huidig wachtwoord: ")
        
        while True:
            new_password = input("Nieuw wachtwoord: ")
            if validate_password(new_password):
                break
            print(get_validation_error_message('password', new_password))
        
        confirm_password = input("Bevestig nieuw wachtwoord: ")
        
        if new_password != confirm_password:
            print("Wachtwoorden komen niet overeen.")
            pause()
            return
        
        success, message = change_own_password(username, old_password, new_password)
        print(f"\n{message}")
    except Exception as e:
        print(f"Fout bij wijzigen wachtwoord: {e}")
    
    pause()

# ============================================================================
# STATISTICS FUNCTION
# ============================================================================

def show_statistics_menu():
    """Show system statistics"""
    clear_screen()
    show_header("Systeem Statistieken")
    
    try:
        travellers = get_all_travellers()
        scooters = get_all_scooters()
        users = get_all_users()
        
        print(f"Totaal aantal gebruikers: {len(users)}")
        print(f"Totaal aantal reizigers: {len(travellers)}")
        print(f"Totaal aantal scooters: {len(scooters)}")
        
        if scooters:
            in_service = sum(1 for s in scooters if not s['out_of_service_status'])
            out_of_service = len(scooters) - in_service
            avg_battery = sum(s['state_of_charge'] for s in scooters) / len(scooters)
            
            print(f"\nScooter statistieken:")
            print(f"  Scooters in dienst: {in_service}")
            print(f"  Scooters buiten dienst: {out_of_service}")
            print(f"  Gemiddelde batterijlading: {avg_battery:.1f}%")
        
        if travellers:
            cities = {}
            for t in travellers:
                cities[t['city']] = cities.get(t['city'], 0) + 1
            
            print(f"\nReizigers per stad:")
            for city, count in sorted(cities.items()):
                print(f"  {city}: {count}")
        
        # User role distribution
        if users:
            roles = {}
            for u in users:
                roles[u['role']] = roles.get(u['role'], 0) + 1
            
            print(f"\nGebruikers per rol:")
            for role, count in sorted(roles.items()):
                print(f"  {role}: {count}")
    except Exception as e:
        print(f"Fout bij ophalen statistieken: {e}")
    
    pause()

# ============================================================================
# MAIN APPLICATION LOOP
# ============================================================================

def main():
    """Main application function"""
    # Initialize database
    print("🚀 Urban Mobility Backend System wordt gestart...")
    
    try:
        init_db()
        print("✅ Database geïnitialiseerd")
    except Exception as e:
        print(f"❌ Fout bij database initialisatie: {e}")
        sys.exit(1)
    
    while True:
        clear_screen()
        show_header("Urban Mobility Backend System - Login")
        
        print("Voor demonstratie doeleinden:")
        print("Username: super_admin")
        print("Password: Admin_123?")
        print()
        print("1. Inloggen")
        print("2. Afsluiten")
        
        choice = input("\nKies een optie (1-2): ")
        
        if choice == "1":
            username = input("Gebruikersnaam: ").strip()
            password = input("Wachtwoord: ")
            
            result = login(username, password)
            if result:
                role, actual_username = result
                print(f"\n✅ Welkom {actual_username}!")
                
                # Main menu loop
                while True:
                    action = show_main_menu(actual_username, role)
                    
                    if action == "logout":
                        log_event(f"Uitgelogd", actual_username)
                        print("Tot ziens!")
                        break
                    elif action == "exit":
                        print("Tot ziens!")
                        sys.exit(0)
                    elif action == "user_management":
                        user_management_menu(actual_username, role)
                    elif action == "service_engineer_management":
                        user_management_menu(actual_username, role)  # Same menu, different permissions
                    elif action == "traveller_management":
                        traveller_management_menu(actual_username, role)
                    elif action == "scooter_management":
                        scooter_management_menu(actual_username, role)
                    elif action == "search_scooters":
                        search_scooters_menu()
                    elif action == "search_travellers":
                        search_travellers_menu()
                    elif action == "update_scooter_info":
                        update_scooter_menu(actual_username, role)
                    elif action == "view_logs":
                        view_logs_menu(actual_username, role)
                    elif action == "backup_management":
                        backup_management_menu(actual_username, role)
                    elif action == "restore_code_management":
                        restore_code_management_menu(actual_username, role)
                    elif action == "change_password":
                        change_password_menu(actual_username, role)
                    elif action == "show_statistics":
                        show_statistics_menu()
                    else:
                        print(f"Functie '{action}' nog niet geïmplementeerd.")
                        pause()
            else:
                print("\n❌ Login mislukt. Controleer gebruikersnaam en wachtwoord.")
                pause()
        
        elif choice == "2":
            print("Tot ziens!")
            sys.exit(0)
        else:
            print("Ongeldige keuze.")
            pause()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nProgramma beëindigd door gebruiker.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Onverwachte fout: {e}")
        print("Controleer of alle bestanden correct zijn en dependencies geïnstalleerd zijn.")
        print("Run: pip install bcrypt cryptography")
        sys.exit(1)