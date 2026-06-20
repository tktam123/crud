import crud
from crud import DatabaseError
from models import FIELD_NAMES

try:
    crud.init_db()  # create the database and table if they don't exist yet
except DatabaseError as error:
    print(f"x {error}")
    raise SystemExit(1)

def show_users():
    users = crud.list_users()  # show all users in the database
    if not users:           # when no users exist
        print("  (there are no users yet)")
        return

    # Build the header row
    header_cells = []
    for name in FIELD_NAMES:
        header_cells.append(f"{name.capitalize():<16}")
    header = "  ID  | " + " | ".join(header_cells)
    print(header)

    # Print a line of dashes under the header
    print("  " + "-" * (len(header) - 2))

    # Print each user as a row
    for u in users:
        row = f"  {u.id:<3} | "

        cells = []
        for name in FIELD_NAMES:
            value = getattr(u, name)   # attribute access instead of u[name]
            text = str(value)          # convert to string
            padded = f"{text:<16}"     # left-align in 16 characters
            cells.append(padded)

        row = row + " | ".join(cells)
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
    Keep asking for name + email + phone + address until the format is
    valid, then return a dict of the values. Type 'q' at any point to
    cancel -> None. Existing values (passed in via `defaults`, a User
    object) are shown and kept on Enter.
    """
    while True:
        data = {}
        cancelled = False
        for name in FIELD_NAMES:                       # ask input for each field
            old = getattr(defaults, name, None) if defaults else None
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

        # Validation now happens inside create_user/update_user, via the
        # User model's @validates methods — if a value is bad, those
        # functions raise ValueError, which we catch here and loop again.
        try:
            _dry_run_validate(data)
            return data
        except ValueError as error:
            print(f"  x {error}  Please try again.\n")


def _dry_run_validate(data):
    """Check the values are valid before committing to the DB, by
    building a throwaway User object — its @validates methods raise
    ValueError on bad input, same as the old validate_user_input()."""
    from models import User
    User(**data)


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
                if data is None:  # if there is no input, meaning the user typed 'q' to cancel
                    print("  (cancelled)")
                    continue
                user = crud.create_user(data)
                print(f"  + added #{user.id}: {user.name}")

            # ---- UPDATE ----
            elif choice == "3":
                show_users()
                uid = ask_id("Change which ID: ")
                if uid is None:  # if the user input is not a number
                    continue        # back to the main menu
                existing = crud.get_user(uid)  # check if the relevant row exists
                if not existing:   # check if the relevant row exists
                    print(f"  x can't find #{uid}")
                    continue
                # original values become defaults: press Enter to keep them
                data = prompt_user_details(existing)   # send the User object as defaults
                if data is None:
                    print("  (cancelled)")
                    continue
                user = crud.update_user(uid, data)
                print(f"  + changed #{user.id}: {user.name}")

            # ---- DELETE ----
            elif choice == "4":
                show_users()
                uid = ask_id("Delete which ID: ")
                if uid is None:  # not a number
                    continue
                user = crud.delete_user(uid)
                if user:
                    print(f"  + deleted #{user.id}: {user.name}")
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
        except ValueError as error:
            print(f"  x {error}")


if __name__ == "__main__":
    main()