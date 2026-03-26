files = {}

def create_file():
    name = input("Enter the file name: ").strip()
    if name == "":
        print("Error: File name cannot be empty.")
        return
    if name in files:
        print("Error: A file with that name already exists.")
        return
    content = input("Enter the file content: ").strip()
    files[name] = content
    print("File created successfully:", name)

def view_file():
    name = input("Enter the file name to view: ").strip()
    if name in files:
        print("File:", name)
        print("Content:", files[name])
    else:
        print("Error: No file found with that name.")

def list_files():
    if len(files) == 0:
        print("No files stored yet.")
        return
    print("\n--- Stored Files ---")
    for i, name in enumerate(files, 1):
        print(str(i) + ".", name)

def delete_file():
    name = input("Enter the file name to delete: ").strip()
    if name in files:
        del files[name]
        print("File deleted successfully:", name)
    else:
        print("Error: No file found with that name.")

def rename_file():
    old_name = input("Enter the current file name: ").strip()
    if old_name not in files:
        print("Error: No file found with that name.")
        return
    new_name = input("Enter the new file name: ").strip()
    if new_name == "":
        print("Error: New file name cannot be empty.")
        return
    if new_name in files:
        print("Error: A file with that name already exists.")
        return
    files[new_name] = files.pop(old_name)
    print("File renamed from", old_name, "to", new_name)

def show_menu():
    while True:
        print("\n--- File Manager Menu ---")
        print("1. Create a new file")
        print("2. View a file")
        print("3. List all files")
        print("4. Delete a file")
        print("5. Rename a file")
        print("6. Show how many files are stored")
        print("7. Exit")
        choice = input("Enter your choice (1-7): ").strip()
        if choice == "1":
            create_file()
        elif choice == "2":
            view_file()
        elif choice == "3":
            list_files()
        elif choice == "4":
            delete_file()
        elif choice == "5":
            rename_file()
        elif choice == "6":
            count = len(files)
            print("You currently have", count, "file(s) stored.")
        elif choice == "7":
            import random
            goodbye_messages = [
                "Exiting File Manager... No files were harmed in the making of this session.",
                "Goodbye! May your filesystem always stay organized. 📁",
                "Connection closed. Keep your data safe!"
            ]
            print(random.choice(goodbye_messages))
            break
        else:
            print("Invalid choice. Please enter a number from 1 to 7.")

if __name__ == "__main__":
    show_menu()
