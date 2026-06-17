import crud
from crud import DatabaseError, validate_user_input

try:
    crud.init_db()
except DatabaseError as e:
    print(f"x {e}")
    raise SystemExit(1)


def show_users():
    """Print all users as a small table."""
    users = crud.list_users()
    if not users:
        print("  (there are no users yet)")
        return
    print("  ID  | Name             | Email                     | Phone")
    print("  ----+------------------+---------------------------+----------------")
    for u in users:
        print(f"  {u['id']:<3} | {u['name']:<16} | {u['email']:<25} | {u['phone']}")


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
    """
    Ask for an ID and check it's a number.
    Shared by Update and Delete (DRY). Returns int, or None if invalid.
    """
    raw = input(prompt).strip()
    if not raw.isdigit():
        print("  x Please enter a number.")
        return None
    return int(raw)


def prompt_user_details(default_name=None, default_email=None, default_phone=None):
    """
    Keep asking for name + email + phone until the format is valid, then
    return (name, email, phone). Type 'q' at any point to cancel -> None.

    """
    while True:
        # ── name ──
        if default_name:
            prompt = f"Name [{default_name}]: "
        else:
            prompt = "Name (or 'q' to cancel): "
 
        name = input(prompt).strip()
 
        if name.lower() == "q":
            return None
        if not name and default_name:        # pressed Enter -> keep original
            name = default_name
 
        # ── email ──
        if default_email:
            prompt = f"Email [{default_email}]: "
        else:
            prompt = "Email (or 'q' to cancel): "
 
        email = input(prompt).strip()
 
        if email.lower() == "q":
            return None
        if not email and default_email:
            email = default_email
 
        # ── phone ──
        if default_phone:
            prompt = f"Phone [{default_phone}]: "
        else:
            prompt = "Phone (or 'q' to cancel): "
 
        phone = input(prompt).strip()
 
        if phone.lower() == "q":
            return None
        if not phone and default_phone:
            phone = default_phone
 
        # ── validate: return if good, otherwise show error and loop again ──
        try:
            validate_user_input(name, email, phone)
            return name, email, phone
        except ValueError as e:
            print(f"  x {e}  Please try again.\n")

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
                details = prompt_user_details()
                if details is None:
                    print("  (cancelled)")
                    continue
                name, email, phone = details
                user = crud.create_user(name, email, phone)
                print(f"  + added #{user['id']}: {user['name']}")

            # ---- UPDATE ----
            elif choice == "3":
                show_users()
                uid = ask_id("Change which ID: ")
                if uid is None:
                    continue
                existing = crud.get_user(uid)
                if not existing:
                    print(f"  x can't find #{uid}")
                    continue
                # original values become defaults: press Enter to keep them
                details = prompt_user_details(existing["name"], existing["email"], existing["phone"])
                if details is None:
                    print("  (cancelled)")
                    continue
                name, email, phone = details
                user = crud.update_user(uid, name, email, phone)
                print(f"  + changed #{user['id']}: {user['name']} <{user['email']}> {user['phone']}")

            # ---- DELETE ----
            elif choice == "4":
                show_users()
                uid = ask_id("Delete which ID: ")
                if uid is None:
                    continue
                user = crud.delete_user(uid)
                if user:
                    print(f"  + deleted #{user['id']}: {user['name']} <{user['email']}> {user['phone']}")
                else:
                    print(f"  x can't find #{uid}")

            # ---- EXIT ----
            elif choice == "5":
                print("Bye!")
                break

            else:
                print("  x choose from 1-5 only")

        except DatabaseError as e:
            print(f"  x {e}")


if __name__ == "__main__":
    main()