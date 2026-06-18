import crud
from crud import DatabaseError, validate_user_input, FIELD_NAMES, FIELDS

try:
    crud.init_db()
except DatabaseError as error:
    print(f"x {error}")
    raise SystemExit(1)


def show_users():
    users = crud.list_users()
    if not users:
        print("  (there are no users yet)")
        return
    header = "  ID  | " + " | ".join(f"{name.capitalize():<16}" for name in FIELD_NAMES)
    print(header)
    print("  " + "-" * (len(header) - 2))
    for u in users:
        row = f"  {u['id']:<3} | " + " | ".join(f"{str(u[name]):<16}" for name in FIELD_NAMES)
        print(row)

def menu():
    """Print the main menu options."""
    print("\n========== User Manager ==========")
    print(" 1. Read all users      (Read)")
    print(" 2. Add a user          (Create)")
    print(" 3. Change a user       (Update)")
    print(" 4. Delete a user       (Delete)")
    print(" 5. Exit")
    print("==================================")


def ask_id(prompt):
    raw = input(prompt).strip()
    if not raw.isdigit():
        print("  x Please enter a number.")
        return None
    return int(raw)


def prompt_user_details(defaults=None):
    """
    Keep asking for name + email + phone until the format is valid, then
    return a dict of the values. Type 'q' at any point to cancel -> None.
    Existing values (passed in via `defaults`) are shown and kept on Enter.
    """
    defaults = defaults or {}
    while True:
        data = {}
        cancelled = False
        for name in FIELD_NAMES:                       # ask input for each field
            old = defaults.get(name)
            if old:
                prompt = f"{name.capitalize()} [{old}]: "
            else:
                prompt = f"{name.capitalize()} (or 'q' to cancel): "
 
            value = input(prompt).strip()
            if value.lower() == "q":
                cancelled = True
                break
            if not value and old:                      # press Enter to keep the old value
                value = old
            data[name] = value
 
        if cancelled:
            return None
 
        try:
            validate_user_input(data)
            return data
        except ValueError as error:
            print(f"  x {error}  Please try again.\n")

def main():
    while True:
        menu()
        choice = input("Choose (1-5): ").strip()

        try:
            # ---- READ ----
            if choice == "1":
                show_users()

            # ---- CREATE ----
            elif choice == "2":
                data = prompt_user_details()
                if data is None: # if there is no input, meaning the user typed 'q' to cancel
                    print("  (cancelled)")
                    continue  
                user = crud.create_user(data)
                print(f"  + added #{user['id']}: {user['name']}")

            # ---- UPDATE ----
            elif choice == "3":
                show_users()
                uid = ask_id("Change which ID: ")
                if uid is None:  # if the user input is not a number
                    continue        #back to the main menu
                existing = crud.get_user(uid) # chek if the regard row exist 
                if not existing:   # chek if the regard row exist 
                    print(f"  x can't find #{uid}")
                    continue
                # original values become defaults: press Enter to keep them
                data = prompt_user_details(existing)   # send the dict to as defaults
                if data is None:
                    print("  (cancelled)")
                    continue
                user = crud.update_user(uid, data)
                print(f"  + changed #{user['id']}: {user['name']}")

            # ---- DELETE ----
            elif choice == "4":
                show_users()
                uid = ask_id("Delete which ID: ")
                if uid is None:  #not a number
                    continue
                user = crud.delete_user(uid)
                if user:
                    print(f"  + deleted #{user['id']}: {user['name']}")
                else:
                    print(f"  x can't find #{uid}")

            # ---- EXIT ----
            elif choice == "5":
                print("Bye!")
                break

            else:
                print("  x choose from 1-5 only")

        except DatabaseError as error:
            print(f"  x {error}")


if __name__ == "__main__":
    main()