import sys
from auth import login, register_user
from um_members import add_scooter, view_travellers, update_traveller
from db import log_event
from backup import create_backup, restore_backup

ROLE_MENUS = {
    'super_admin': [
        ('Voeg scooter toe', 'add_scooter'),
        ('Bekijk reizigers', 'view_travellers'),
        ('Log uit', 'logout'),
        ('Genereer restore-code', 'generate_restore_code'),
        ('Restore backup', 'restore_backup'),
        ('Verwijder gebruiker', 'delete_user'),
        ('Update gebruiker', 'update_user'),
    ],
    'system_admin': [
        ('Voeg scooter toe', 'add_scooter'),
        ('Bekijk reizigers', 'view_travellers'),
        ('Log uit', 'logout'),
        ('Restore backup', 'restore_backup'),
        ('Verwijder gebruiker', 'delete_user'),
        ('Update gebruiker', 'update_user'),
    ],
    'service_engineer': [
        ('Bekijk reizigers', 'view_travellers'),
        ('Update reiziger', 'update_traveller'),
        ('Log uit', 'logout'),
    ]
}

def show_menu(role, username):
    print(f"\nWelkom {username}. Kies een actie:")
    menu = ROLE_MENUS[role]
    for idx, (desc, _) in enumerate(menu, 1):
        print(f"[{idx}] {desc}")
    choice = input("Maak een keuze: ")
    try:
        idx = int(choice) - 1
        if 0 <= idx < len(menu):
            return menu[idx][1]
    except ValueError:
        pass
    print("Ongeldige keuze.")
    return None

def handle_action(action, username, role=None):
    if action == 'add_scooter':
        scooter_id = input('Scooter ID: ')
        location = input('Locatie: ')
        add_scooter(scooter_id, location)
        log_event(f"Scooter toegevoegd door {username}: {scooter_id} op {location}")
        print('Scooter toegevoegd!')
    elif action == 'view_travellers':
        travellers = view_travellers()
        print('Reizigers:')
        for t in travellers:
            print(t)
    elif action == 'update_traveller':
        traveller_id = input('Reiziger ID: ')
        new_name = input('Nieuwe naam: ')
        update_traveller(traveller_id, new_name)
        log_event(f"Reiziger bijgewerkt door {username}: {traveller_id} -> {new_name}")
        print('Reiziger bijgewerkt!')
    elif action == 'generate_restore_code':
        # Placeholder: actual restore code logic should be implemented
        print('Restore-code gegenereerd (dummy).')
        log_event(f"Restore-code gegenereerd door {username}")
    elif action == 'restore_backup':
        backup_zip = input('Pad naar backup zip: ')
        is_super_admin = (role == 'super_admin')
        restore_code = None
        if not is_super_admin:
            restore_code = input('Voer restore-code in: ')
        if restore_backup(backup_zip, username, restore_code, is_super_admin):
            print('Backup succesvol hersteld!')
        else:
            print('Backup herstellen mislukt of niet toegestaan.')
    elif action == 'delete_user':
        user_id = input('Gebruikersnaam om te verwijderen: ')
        # Placeholder: actual delete logic for users
        print(f'Gebruiker {user_id} verwijderd (dummy).')
        log_event(f"Gebruiker verwijderd door {username}: {user_id}")
    elif action == 'update_user':
        user_id = input('Gebruikersnaam om te updaten: ')
        new_name = input('Nieuwe naam: ')
        # Placeholder: actual update logic for users
        print(f'Gebruiker {user_id} bijgewerkt naar {new_name} (dummy).')
        log_event(f"Gebruiker bijgewerkt door {username}: {user_id} -> {new_name}")
    else:
        print(f"Actie '{action}' is nog niet geïmplementeerd.")

def main():
    print("Urban Mobility Backend System")
    while True:
        print("\n1. Login\n2. Registreer\n3. Afsluiten")
        action = input("Kies een optie: ")
        if action == '1':
            username = input("Gebruikersnaam: ")
            password = input("Wachtwoord: ")
            role = login(username, password)
            if role:
                while True:
                    action = show_menu(role, username)
                    if action == 'logout':
                        break
                    handle_action(action, username, role)
            else:
                print("Login mislukt.")
        elif action == '2':
            username = input("Gebruikersnaam: ")
            password = input("Wachtwoord: ")
            role = input("Rol (super_admin/system_admin/service_engineer): ")
            first_name = input("Voornaam: ")
            last_name = input("Achternaam: ")
            if register_user(username, password, role, first_name, last_name):
                print("Gebruiker succesvol geregistreerd.")
            else:
                print("Registratie mislukt.")
        elif action == '3':
            print("Tot ziens!")
            sys.exit(0)
        else:
            print("Ongeldige optie.")

if __name__ == '__main__':
    main()
