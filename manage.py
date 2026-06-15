import database

database.init_db()      # 開機整張 table(如果未有)

def show_users():
    users = database.list_users()
    if not users:
        print("  (there are no user)")
        return
    print("  ID  | Namw               | Email")
    print("  ----+------------------+--------------------------")
    for u in users:
        print(f"  {u['id']:<3} | {u['name']:<16} | {u['email']}")

def menu():
    print("\n========== User Manager ==========")
    print(" 1. Read all the user      (Read)")
    print(" 2. Add one user        (Create)")
    print(" 3. Change one user        (Update)")
    print(" 4. Delete one user        (Delete)")
    print(" 5. end program        (Exit)")
    print("==================================")

while True:
    menu()
    choice = input("Choose (1-5): ").strip()

    # ---- READ ----
    if choice == "1":
        show_users()

    # ---- CREATE ----
    elif choice == "2":
        name = input("Name: ").strip()
        email = input("Email: ").strip()
        if name and email:
            user = database.create_user(name, email)
            print(f"  ✓ added #{user['id']}: {user['name']}")
        else:
            print("  ✗ repeatedly, name and email cannot be empty")

    # ---- UPDATE ----
    elif choice == "3":
        show_users()
        try:
            uid = int(input("change which ID: ").strip())
        except ValueError:
            print("  ✗ Please enter a number")
            continue
        if not database.get_user(uid):
            print(f"  ✗ can't find #{uid}")
            continue
        name = input("New name: ").strip()
        email = input("New email: ").strip()
        user = database.update_user(uid, name, email)
        print(f"  ✓ changed #{user['id']}: {user['name']} <{user['email']}>")

    # ---- DELETE ----
    elif choice == "4":
        show_users()
        try:
            uid = int(input("delete which ID: ").strip())
        except ValueError:
            print("  ✗ please input a number")
            continue
        user = database.delete_user(uid)
        if user:
            print(f"  ✓ deleted #{user['id']}: {user['name']}")
        else:
            print(f"  ✗ can't find #{uid}")

    # ---- EXIT ----
    elif choice == "5":
        print("👋")
        break

    else:
        print("  ✗ choose from 1-5 only")