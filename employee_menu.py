import body


def customer_menu():
    """Find or create customer, then show customer actions."""
    # Ask for customer full name.
    name = input("Enter customer name: ").strip()
    if not name:
        print("Name cannot be empty")
        return

    # Search by name text (supports partial name, not exact match only).
    sql = """
    SELECT user_id, full_name, email
    FROM users
    WHERE full_name LIKE %s AND role = 'customer'
    ORDER BY user_id DESC
    """
    body.db_cursor.execute(sql, (f"%{name}%",))
    matches = body.db_cursor.fetchall()

    # If one or more matches found, pick customer.
    if matches:
        if len(matches) == 1:
            customer_id = matches[0][0]
        else:
            print("Matching customers:")
            for m in matches:
                print(f"ID: {m[0]} | Name: {m[1]} | Email: {m[2]}")
            picked_id = input("Choose customer ID: ").strip()
            if not picked_id.isdigit():
                print("Customer ID must be a number")
                return
            customer_id = int(picked_id)
            sql_check = """
            SELECT user_id
            FROM users
            WHERE user_id = %s AND role = 'customer'
            """
            body.db_cursor.execute(sql_check, (customer_id,))
            if body.db_cursor.fetchone() is None:
                print("Customer not found")
                return
    else:
        # If not found, optionally create a new customer.
        answer = input("Customer not found. Create new customer? (y/n): ").strip().lower()
        if answer != "y":
            return
        first_name = input("Enter first name: ").strip()
        last_name = input("Enter last name: ").strip()
        email = input("Enter email: ").strip()

        if not first_name or not last_name or not email:
            print("All fields are required")
            return
        full_name = f"{first_name} {last_name}"
        customer_id = body.create_customer(full_name, email)
        if customer_id is None:
            print("Could not create customer")
            return
        print("New customer created")

    while True:
        print("\nCustomer Menu")
        print("1 Create complaint")
        print("2 View my complaints")
        print("3 Send message")
        print("4 Update my profile")
        print("Q Back")

        c = input("Choice: ").strip()

        if c == "1":
            # Customer writes a new complaint.
            desc = input("Complaint description: ").strip()
            if not desc:
                print("Description cannot be empty")
                continue

            sql = ("""
            INSERT INTO complaints (customer_id, description)
            VALUES (%s, %s)
            """)
            body.db_cursor.execute(sql, (customer_id, desc))
            body.db.commit()
            print("Complaint created")

        elif c == "2":
            sql = ("""
            SELECT complaint_id, status, description, created_at
            FROM complaints
            WHERE customer_id = %s
            ORDER BY complaint_id DESC
            """)
            body.db_cursor.execute(sql, (customer_id,))
            rows = body.db_cursor.fetchall()
            body.print_rows(rows, "No complaints found")

        elif c == "3":
            # Customer sends message on own complaint only.
            complaint_id = input("Complaint ID: ").strip()
            message = input("Message: ").strip()

            if not complaint_id.isdigit():
                print("Complaint ID must be a number")
                continue
            if not message:
                print("Message cannot be empty")
                continue

            sql = """
            SELECT complaint_id
            FROM complaints
            WHERE complaint_id = %s AND customer_id = %s
            """
            body.db_cursor.execute(sql, (complaint_id, customer_id))
            own_complaint = body.db_cursor.fetchone()

            # Stop if complaint does not belong to this customer.
            if not own_complaint:
                print("You can only send messages on your own complaints")
                continue

            sql = """
            INSERT INTO messages (complaint_id, sender_id, message_type, message_text)
            VALUES (%s, %s, 'customer', %s)
            """
            body.db_cursor.execute(sql, (complaint_id, customer_id, message))
            body.db.commit()
            print("Message sent")

        elif c == "4":
            # Customer updates own profile.
            first_name = input("Enter new first name: ").strip()
            last_name = input("Enter new last name: ").strip()
            email = input("Enter new email: ").strip()

            if not first_name or not last_name or not email:
                print("All fields are required")
                continue

            full_name = f"{first_name} {last_name}"
            status = body.update_customer(customer_id, full_name, email)
            if status == "ok":
                print("Profile updated")
            elif status == "email_exists":
                print("Email already exists")
            else:
                print("Customer not found")

        elif c.lower() == "q":
            break

        else:
            print("Invalid choice")


def complaints_menu(user_id, role):
    """Single complaints menu: my complaints, all complaints (manager), and search."""
    while True:
        # One place for complaint list + search.
        print("\nComplaints")
        print("1 View my complaints")
        if role == "manager":
            print("2 View all complaints")
        print("3 Search complaint")
        print("Q Back")

        choice = input("Choice: ").strip()

        if choice == "1":
            body.view_my_complaints(user_id)
        elif choice == "2" and role == "manager":
            # Manager can see all complaints.
            body.view_all_complaints()
        elif choice == "3":
            search_value = input("Complaint ID or customer name: ").strip()
            if not search_value:
                print("Search value is required")
                continue

            # If input is a number, search by complaint ID.
            if search_value.isdigit():
                if role == "manager":
                    sql = """
                    SELECT complaint_id, customer_name, status, description, created_at
                    FROM v_complaints_with_customer
                    WHERE complaint_id = %s
                    """
                    body.db_cursor.execute(sql, (search_value,))
                else:
                    sql = """
                    SELECT c.complaint_id,
                           u.full_name,
                           c.status,
                           c.description,
                           c.created_at
                    FROM complaints c
                    JOIN users u ON c.customer_id = u.user_id
                    WHERE c.assigned_employee_id = %s
                      AND c.complaint_id = %s
                    """
                    body.db_cursor.execute(sql, (user_id, search_value))
            else:
                # If input is text, search by customer name.
                if role == "manager":
                    sql = """
                    SELECT complaint_id, customer_name, status, description, created_at
                    FROM v_complaints_with_customer
                    WHERE customer_name LIKE %s
                    ORDER BY complaint_id DESC
                    """
                    body.db_cursor.execute(sql, (f"%{search_value}%",))
                else:
                    sql = """
                    SELECT c.complaint_id,
                           u.full_name,
                           c.status,
                           c.description,
                           c.created_at
                    FROM complaints c
                    JOIN users u ON c.customer_id = u.user_id
                    WHERE c.assigned_employee_id = %s
                      AND u.full_name LIKE %s
                    ORDER BY c.complaint_id DESC
                    """
                    body.db_cursor.execute(sql, (user_id, f"%{search_value}%"))

            rows = body.db_cursor.fetchall()
            body.print_rows(rows, "No complaints found")
        elif choice.lower() == "q":
            break
        else:
            print("Invalid choice")


def messages_menu(user_id, role):
    """Single messages menu: my messages, all messages (manager), back."""
    while True:
        # Keep message actions in one submenu.
        print("\nMessages")
        print("1 View and send my messages")
        if role == "manager":
            print("2 View all messages")
        print("Q Back")

        choice = input("Choice: ").strip()
        if choice == "1":
            body.view_and_send_messages(user_id)
        elif choice == "2" and role == "manager":
            body.view_all_messages()
        elif choice.lower() == "q":
            break
        else:
            print("Invalid choice")


def manager_reports_menu():
    """Single manager menu for status history and statistics."""
    while True:
        # Reports used by manager only.
        print("\nManager Reports")
        print("1 View status history")
        print("2 View statistics")
        print("Q Back")

        choice = input("Choice: ").strip()
        if choice == "1":
            body.view_status_history()
        elif choice == "2":
            body.view_statistics()
        elif choice.lower() == "q":
            break
        else:
            print("Invalid choice")


def receipts_menu(user_id):
    """Single receipt menu: add, view, back."""
    while True:
        # Receipt actions for employee's complaints.
        print("\nReceipts")
        print("1 Add receipt")
        print("2 View receipts")
        print("Q Back")

        choice = input("Choice: ").strip()
        if choice == "1":
            body.add_receipt(user_id)
        elif choice == "2":
            body.view_receipts(user_id)
        elif choice.lower() == "q":
            break
        else:
            print("Invalid choice")


def customers_menu():
    """Single customer menu for staff: create, update, back."""
    while True:
        # Staff can create or update customer profiles.
        print("\nCustomers")
        print("1 Create customer")
        print("2 Update customer")
        print("Q Back")

        choice = input("Choice: ").strip()
        if choice == "1":
            first_name = input("Customer first name: ").strip()
            last_name = input("Customer last name: ").strip()
            email = input("Customer email: ").strip()

            # Stop if any required field is empty.
            if not first_name or not last_name or not email:
                print("All fields are required")
                continue

            full_name = f"{first_name} {last_name}"
            customer_id = body.create_customer(full_name, email)
            if customer_id is None:
                print("Could not create customer")
            else:
                print("Customer created")
        elif choice == "2":
            current_email = input("Current customer email: ").strip()
            first_name = input("New first name: ").strip()
            last_name = input("New last name: ").strip()
            email = input("New email: ").strip()

            if not current_email or not first_name or not last_name or not email:
                print("All fields are required")
                continue

            sql = """
            SELECT user_id
            FROM users
            WHERE email = %s AND role = 'customer'
            """
            body.db_cursor.execute(sql, (current_email,))
            row = body.db_cursor.fetchone()
            if not row:
                print("Customer not found")
                continue

            full_name = f"{first_name} {last_name}"
            status = body.update_customer(int(row[0]), full_name, email)
            if status == "ok":
                print("Customer updated")
            elif status == "email_exists":
                print("Email already exists")
            else:
                print("Customer not found")
        elif choice.lower() == "q":
            break
        else:
            print("Invalid choice")


def manu(user_id, role="employee"):
    """One simple staff menu for both employee and manager."""
    while True:
        # Main staff menu.
        print("\nStaff Menu")
        print("1 Complaints (my/all/search)")
        print("2 View and Take complaint")
        print("3 Messages (my/all)")
        print("4 Update status (my complaints)")
        print("5 Receipts (add/view)")
        print("6 Customers (create/update)")
        print("7 Manager reports (history/statistics)")
        print("Q Back")

        choice = input("Choice: ").strip()

        if choice == "1":
            complaints_menu(user_id, role)
        elif choice == "2":
            body.take_complaint(user_id)
        elif choice == "3":
            messages_menu(user_id, role)
        elif choice == "4":
            body.update_status(user_id, role)
        elif choice == "5":
            receipts_menu(user_id)
        elif choice == "6":
            customers_menu()
        elif choice == "7":
            # Manager-only submenu.
            if role != "manager":
                print("Only manager can use this option")
            else:
                manager_reports_menu()
        elif choice.lower() == "q":
            break
        else:
            print("Invalid choice")
