import body
from employee_menu import customer_menu, manu

def check_user_role():
    """Check user role by user ID and open the correct menu."""
    # Ask user for ID from users table.
    u_id = input("Enter User ID: ").strip()

    # Use user_id to decide which menu this login can access.
    sql = "SELECT role FROM users WHERE user_id = %s"
    body.db_cursor.execute(sql, (u_id,))
    result = body.db_cursor.fetchone()
    # No row means wrong ID.
    if result is None:
        print("User not found")
        return
    # Read role and open staff menu only for manager/employee.
    role = result[0]
    if role in ("manager", "employee"):
        if role == "manager":
            print("This user is MANAGER")
        else:
            print("This user is EMPLOYEE (not manager)")
        manu(u_id, role)
    else:
        # Customer uses separate customer menu from main screen.
        print("This login is only for manager/employee")

def main():
    """Show main menu and send user to the selected area."""
    while True:
        # Main app options.
        print("\nWelcome")
        print("1 Manager / Employee")
        print("2 Customer")
        print("Q Quit")

        choice = input("Enter your choice: ").strip().lower()
        if choice == "1":
            check_user_role()
        elif choice == "2":
            customer_menu()
        elif choice == "q":
            break
        else:
            print("Invalid option")


if __name__ == "__main__":
    main()
