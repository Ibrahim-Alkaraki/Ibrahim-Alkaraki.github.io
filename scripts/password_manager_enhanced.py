passwords = {}

def check_strength(password):
    """
    Check a very simple 'strength' of the password based on length
    and print a message.
    """
    length = len(password)
    if length < 6:
        print("Password strength: weak (try making it longer).")
    elif length < 10:
        print("Password strength: medium (pretty good, but can be stronger).")
    else:
        print("Password strength: strong (nice job!).")


def has_number(password):

    # Return True if the password contains at least one digit (0-9),
    # Otherwise return False.
    for ch in password:
        if ch.isdigit():
            return True
    return False


def add_password():
    """
    Add a new service with its username and password to the password manager.
    Enforcing a rule: password must contain at least one number.
    """
    service = input("Enter the service name (e.g., email, bank): ").strip()
    username = input("Enter the username for this service: ").strip()
    password = input("Enter the password for this service: ").strip()

    if service == "" or username == "" or password == "":
        print("Error: Service, username, and password cannot be empty.")
        return

    if not has_number(password):
        print("Error: Password must contain at least one number (0-9).")
        return

    passwords[service] = (username, password)
    print("Password added successfully for service:", service)
    check_strength(password)


def retrieve_password():

    # Retrieve and display the username and password for a given service.

    service = input("Enter the service name to retrieve: ").strip()

    if service in passwords:
        username, password = passwords[service]
        print("Service:", service)
        print("Username:", username)
        print("Password:", password)
    else:
        print("Error: No password found for that service.")


def validate_credentials():

    #Validate if the given service, username, and password match a stored entry.

    service = input("Enter the service name to validate: ").strip()
    username = input("Enter the username: ").strip()
    password = input("Enter the password: ").strip()

    if service not in passwords:
        print("Credentials are incorrect (service not found).")
        return

    stored_username, stored_password = passwords[service]

    if username == stored_username and password == stored_password:
        print("Credentials are correct.")
    else:
        print("Credentials are incorrect.")


def show_menu():

    #Show the main menu and handle user choices in a loop.

    while True:
        print("\n--- Password Manager Menu ---")
        print("Note: Passwords must include at least one number (0-9).")
        print("1. Add a new password")
        print("2. Retrieve a stored password")
        print("3. Validate username and password")
        print("4. Show how many services are saved")
        print("5. Exit")

        choice = input("Enter your choice (1-5): ").strip()

        if choice == "1":
            add_password()
        elif choice == "2":
            retrieve_password()
        elif choice == "3":
            validate_credentials()
        elif choice == "4":
            count = len(passwords)
            print("You currently have", count, "service(s) stored.")
        elif choice == "5":
            import random
            goodbye_messages = [
                "Exiting... Your passwords are as safe as they'll ever be. Goodbye!",
                "Until next time! No passwords were harmed in the making of this session.",
                "Connection closed. May your credentials always be strong! 🔐"
            ]
            print(random.choice(goodbye_messages))
            break
        else:
            print("Invalid choice. Please enter a number from 1 to 5.")


# Start the program by showing the menu
if __name__ == "__main__":
    show_menu()
