import mysql.connector
from db import db, db_cursor

def print_rows (rows,empty_massage ):
    """"
    prints query results line by line
     or prints a fallback message if there are no rows.
     """
    if rows is None:
      print(empty_massage)
      return
    # Print each row as one line.
    for row in rows:
      print(row)


def create_customer(full_name, email):
    """Create customer with procedure and return customer_id (or None)"""
    try:
        # Call stored procedure from DB schema.
        db_cursor.callproc("sp_create_customer", (full_name, email))
        db.commit()
    except mysql.connector.IntegrityError:
        # Duplicate email (UNIQUE constraint)
        db.rollback()
        print("Email already exists.")
        return None
        # Other database errors
    except mysql.connector.Error:
        db.rollback()
        return None

    # Read back created customer id by unique email.
    sql = (
        "SELECT user_id FROM users "
        "WHERE email = %s AND role = 'customer'"
    )
    db_cursor.execute(sql, (email,))
    result = db_cursor.fetchone()

    if not result:
        return None
    return result[0]

def update_customer(customer_id, full_name, email):
    """Update customer profile and return status string."""
    # First check if this customer exists.
    sql =(
        "SELECT user_id FROM users"
         " WHERE user_id = %s AND role = 'customer'"
    )
    db_cursor.execute(sql, (customer_id,))
    row = db_cursor.fetchone()
    if not row:
        return "not_found"

    # If another customer already has this email, block update.
    sql_email = """
    SELECT user_id
    FROM users
    WHERE email = %s
      AND role = 'customer'
      AND user_id <> %s
    """
    db_cursor.execute(sql_email, (email, customer_id))
    if db_cursor.fetchone():
        return "email_exists"

    # Update using stored procedure.
    try:
        db_cursor.callproc("sp_update_customer", (int(customer_id), full_name, email))
        db.commit()
    except mysql.connector.Error:
        db.rollback()
        return "error"

    return "ok"

def is_my_complaint(complaint_id, user_id):
    """Return True if complaint belongs to logged-in employee."""
    # Security check used before message/receipt actions.
    sql = (
        "SELECT complaint_id FROM complaints "
           "WHERE complaint_id = %s AND assigned_employee_id = %s"
           )
    db_cursor.execute(sql, (complaint_id, user_id))
    return db_cursor.fetchone() is not None


def view_my_complaints(user_id):
    """Show complaints assigned to logged-in employee."""
    # Join complaints + users to show customer name.
    sql = ("""
    SELECT c.complaint_id,
           u.full_name,
           c.status,
           c.description,
           c.created_at
    FROM complaints c
    JOIN users u
      ON c.customer_id = u.user_id
    WHERE c.assigned_employee_id = %s
    ORDER BY c.complaint_id DESC
    """)
    db_cursor.execute(sql, (user_id,))
    rows = db_cursor.fetchall()
    print_rows(rows, "No complaints assigned to you")


def take_complaint(user_id):
    """Show new complaints, then let employee take one safely."""
    # Show only open complaints that are still unassigned.
    sql_new = """
    SELECT c.complaint_id,
           u.full_name,
           c.status,
           c.description,
           c.created_at
    FROM complaints c
    JOIN users u ON c.customer_id = u.user_id
    WHERE c.assigned_employee_id IS NULL
      AND c.status = 'open'
    ORDER BY c.complaint_id DESC
    """
    db_cursor.execute(sql_new)
    new_rows = db_cursor.fetchall()
    print_rows(new_rows, "No new complaints found")
    if not new_rows:
        return

    # Allow user to go back without taking a complaint.
    complaint_id = input("Enter complaint ID to take or q to go back: ").strip()
    if complaint_id.lower() == "q" :
        return
    if not complaint_id.isdigit():
        print("Invalid ID. Please enter numbers only.")
        return

    sql_check = """
    SELECT complaint_id
    FROM complaints
    WHERE complaint_id = %s
      AND assigned_employee_id IS NULL
      AND status = 'open'
    """
    db_cursor.execute(sql_check, (complaint_id,))
    if db_cursor.fetchone() is None:
        print("Complaint not available or wrong ID")
        return

    try:
        # Stored procedure assigns the complaint if still available.
        db_cursor.callproc("sp_take_complaint", (int(complaint_id), int(user_id)))
        db.commit()
    except mysql.connector.Error:
        db.rollback()
        print("Something went wrong in the database.")
        return

    sql_verify = ("""
    SELECT assigned_employee_id, status
    FROM complaints
    WHERE complaint_id = %s
    """)
    db_cursor.execute(sql_verify, (complaint_id,))
    row = db_cursor.fetchone()

    if row and str(row[0]) == str(user_id) and row[1] == "on_progress":
        print("Complaint assigned to you")
    else:
        print("Complaint not available")


def update_status(user_id, role="employee"):
    """Update complaint status. Manager can update all; employee only own."""
    complaint_id = input("Complaint ID: ").strip()
    new_status = input("New status: ").strip()

    if role == "manager":
        sql = """
        UPDATE complaints
        SET status = %s
        WHERE complaint_id = %s
        """
        db_cursor.execute(sql, (new_status, complaint_id))
    else:
        # Employee can update only own assigned complaint.
        sql = """
        UPDATE complaints
        SET status = %s
        WHERE complaint_id = %s
          AND assigned_employee_id = %s
        """
        db_cursor.execute(sql, (new_status, complaint_id, user_id))
    db.commit()

    if db_cursor.rowcount > 0:
        print("Status updated")
    else:
        if role == "manager":
            print("Complaint not found")
        else:
            print("You can only update your own complaints")


def view_and_send_messages(user_id):
    """Show allowed complaints, view messages, then optionally send a new one."""
    # Show complaint list employee is allowed to message.
    sql_list = """
    SELECT c.complaint_id,
           u.full_name,
           c.status
    FROM complaints c
    JOIN users u ON c.customer_id = u.user_id
    WHERE c.assigned_employee_id = %s
    ORDER BY c.complaint_id DESC
    """
    db_cursor.execute(sql_list, (user_id,))
    complaint_rows = db_cursor.fetchall()
    print_rows(complaint_rows, "No complaints assigned to you")
    if not complaint_rows:
        return

    # User can only open and send messages for own assigned complaints.
    complaint_id = input("Choose complaint ID: ").strip()
    if not complaint_id.isdigit():
        print("Complaint ID must be a number")
        return
    if not is_my_complaint(complaint_id, user_id):
        print("You can only use your own complaints")
        return

    sql_messages = """
    SELECT u.full_name,
           m.message_type,
           m.message_text,
           m.sent_at
    FROM messages m
    JOIN users u ON m.sender_id = u.user_id
    WHERE m.complaint_id = %s
    ORDER BY m.sent_at ASC
    """
    db_cursor.execute(sql_messages, (complaint_id,))
    message_rows = db_cursor.fetchall()
    print_rows(message_rows, "No messages found")

    # Empty input means: view only, do not send a new message.
    message_text = input("Write message (Enter = skip): ").strip()
    if not message_text:
        return

    sql_send = """
    INSERT INTO messages (complaint_id, sender_id, message_type, message_text)
    VALUES (%s, %s, 'employee', %s)
    """
    db_cursor.execute(sql_send, (complaint_id, user_id, message_text))
    db.commit()
    print("Message sent")


def add_receipt(user_id):
    """Add receipt for a complaint assigned to logged-in employee."""
    # Prevent adding receipt to someone else's complaint.
    complaint_id = input("Complaint ID: ").strip()

    if not is_my_complaint(complaint_id, user_id):
        print("You can only add receipts to your own complaints")
        return

    receipt_number = input("Receipt number: ").strip()
    amount = input("Amount: ").strip()
    store_name = input("Store name: ").strip()
    note = input("Note (optional): ").strip()

    sql = """
    INSERT INTO receipts (receipt_number, amount, store_name, note)
    VALUES (%s, %s, %s, %s)
    """
    db_cursor.execute(sql, (receipt_number, amount, store_name, note))
    db.commit()

    receipt_id = db_cursor.lastrowid

    # Link receipt row to complaint row (many-to-many table).
    sql = """
    INSERT INTO complaint_receipt (complaint_id, receipt_id)
    VALUES (%s, %s)
    """
    db_cursor.execute(sql, (complaint_id, receipt_id))
    db.commit()

    print("Receipt added")


def view_receipts(user_id):
    """Show receipts for a complaint assigned to logged-in employee."""
    # Show only receipts from complaints assigned to this employee.
    complaint_id = input("Complaint ID: ").strip()

    sql = """
    SELECT r.receipt_number,
           r.amount,
           r.store_name,
           r.note
    FROM receipts r
    JOIN complaint_receipt cr
      ON r.receipt_id = cr.receipt_id
    JOIN complaints c
      ON c.complaint_id = cr.complaint_id
    WHERE cr.complaint_id = %s
      AND c.assigned_employee_id = %s
    """
    db_cursor.execute(sql, (complaint_id, user_id))
    rows = db_cursor.fetchall()
    print_rows(rows, "No receipts found")


def view_all_complaints():
    """Manager: show all complaints."""
    # Uses view with customer name included.
    sql = """
    SELECT complaint_id, customer_name, status, description, created_at
    FROM v_complaints_with_customer
    ORDER BY complaint_id DESC
    """
    db_cursor.execute(sql)
    rows = db_cursor.fetchall()
    print_rows(rows, "No complaints found")


def view_all_messages():
    """Manager: show all messages."""
    # Manager overview of message log.
    sql = """
    SELECT message_id, complaint_id, sender_id, message_type, message_text, sent_at
    FROM messages
    ORDER BY message_id DESC
    """
    db_cursor.execute(sql)
    rows = db_cursor.fetchall()
    print_rows(rows, "No messages found")


def view_status_history():
    """Manager: show status history."""
    # Read trigger-generated status history table.
    sql = """
    SELECT history_id, complaint_id, user_id, old_status, new_status, changed_at
    FROM status_history
    ORDER BY history_id DESC
    """
    db_cursor.execute(sql)
    rows = db_cursor.fetchall()
    print_rows(rows, "No status history found")


def view_statistics():
    """Manager: show simple statistics."""
    # Simple report query.
    print("\nStatistics")
    print("1 Complaints per status")
    choice = input("Choice: ").strip()

    if choice == "1":
        sql = """
        SELECT status, COUNT(*) AS total
        FROM complaints
        GROUP BY status
        ORDER BY total DESC
        """
        db_cursor.execute(sql)
        rows = db_cursor.fetchall()
        print_rows(rows, "No statistics found")
    else:
        print("Invalid choice")


print("db connected")
