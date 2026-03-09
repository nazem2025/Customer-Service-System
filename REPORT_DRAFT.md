# Final Project Report

**Student:** Nazem Alakkad  
**Course:** Database  
**Project:** Complaint Management System

## 1. Project Idea

For this project, I designed and implemented a **Complaint Management System**.

### Problem
Many businesses receive customer complaints, but handling them in a simple and organized way is difficult. Messages, complaint status, and employee assignment can become unclear without a structured system.

### Main Users
The system has three user roles:

1. **Customer**  
   Creates complaints, views own complaints, sends messages, and updates profile.
2. **Employee**  
   Views and takes new complaints, updates complaint status, sends messages, and handles receipts.
3. **Manager**  
   Can view all complaints/messages, see status history, and view statistics.

### Why this idea is suitable
This idea is a good fit for a database project because it needs:

1. Multiple related entities (users, complaints, messages, receipts, history).
2. Role-based access and constraints.
3. Real database logic (joins, grouping, procedures, triggers).

### Data Source
The project uses **synthetic/generated data** created for testing.  
The data is provided in `test_data.sql`.

---

## 2. Schema Design

The system is built around these tables:

1. `users`  
   Stores manager, employee, and customer accounts.
2. `complaints`  
   Stores each complaint, status, customer, and assigned employee.
3. `messages`  
   Stores customer/employee/manager messages linked to a complaint.
4. `receipts`  
   Stores receipt information.
5. `complaint_receipt`  
   Connects complaints and receipts (many-to-many relation).
6. `status_history`  
   Stores all complaint status changes.

### Important relationships

1. One customer can create many complaints (`users -> complaints`).
2. One employee can be assigned to many complaints (`users -> complaints`).
3. One complaint can have many messages (`complaints -> messages`).
4. One complaint can have many status changes (`complaints -> status_history`).
5. Complaints and receipts are linked through `complaint_receipt`.

### Design motivation

1. Roles are in the `users` table to keep user management simple.
2. Complaint status is controlled by ENUM values to avoid invalid status text.
3. `status_history` gives traceability for manager review.
4. `email` is unique to avoid duplicate customer emails.

---

## 3. SQL Schema Implementation

The schema is implemented in:

1. `first_time_setup.sql` (database, tables, keys, indexes, view, triggers, procedures)
2. `test_data.sql` (test data)

### Database features used

1. **Foreign keys** for data integrity.
2. **Indexes** for common search columns.
3. **View** `v_complaints_with_customer` for manager list/search.
4. **Procedures**
   - `sp_create_customer`
   - `sp_update_customer`
   - `sp_take_complaint`
5. **Triggers**
   - `trg_complaint_auto_on_progress` (open -> on_progress when employee takes complaint)
   - `trg_complaint_status_history` (logs status changes)

---

## 4. SQL Queries (Important Examples)

Below are five important queries used by the application.

### Q1. Show all complaints with customer name (JOIN)
```sql
SELECT complaint_id, customer_name, status, description, created_at
FROM v_complaints_with_customer
ORDER BY complaint_id DESC;
```
**Why:** Manager overview of all complaints. This is a multirelation query through a view built with JOIN.

### Q2. Search complaints by customer name (JOIN)
```sql
SELECT complaint_id, customer_name, status, description, created_at
FROM v_complaints_with_customer
WHERE customer_name LIKE ?
ORDER BY complaint_id DESC;
```
**Why:** Manager can quickly find complaints by customer name. Uses JOIN through the view.

### Q3. Complaints per status (Aggregation + GROUP BY)
```sql
SELECT status, COUNT(*) AS total
FROM complaints
GROUP BY status
ORDER BY total DESC;
```
**Why:** Manager gets a quick statistical summary of workload by status.

### Q4. Procedure to assign complaint
```sql
CALL sp_take_complaint(?, ?);
```
**Why:** Centralizes assignment logic in database and avoids duplicate update logic in Python.

### Q5. Status history view
```sql
SELECT history_id, complaint_id, user_id, old_status, new_status, changed_at
FROM status_history
ORDER BY history_id DESC;
```
**Why:** Lets manager audit what status changed, when it changed, and for which complaint.

### Trigger usage (requirement support)
When complaint assignment happens, the trigger can automatically set status from `open` to `on_progress`.  
Another trigger writes all status changes into `status_history`.

---

## 5. Implementation

The application is implemented in Python with explicit SQL (no ORM):

1. `main.py`  
   Main entry menu and role routing.
2. `employee_menu.py`  
   Staff menus (complaints, messages, receipts, customer tools, manager reports) and customer menu flow.
3. `body.py`  
   Shared database operations and SQL execution.
4. `db.py`  
   Database connection configuration.

### Notes

1. Parameterized queries (`%s`) are used for safety.
2. Input validation is used in many places (`isdigit`, empty checks).
3. Errors like duplicate email are handled in Python with `try/except`.

---

## 6. Discussion and Resources

### Discussion

1. A main challenge was role permissions (manager vs employee) and making sure users only access allowed data.
2. Another challenge was handling duplicate emails safely during create/update.
3. I also improved the menu flow by combining related actions into submenus.

### Resources

1. Project source code: **[Add your Git/GitLab link here]**
2. Database dump: **`complaint_system_dump.sql`**
3. Setup files:
   - `first_time_setup.sql`
   - `test_data.sql`

---

## Appendix: Changelog

| Person | Task | Date |
|---|---|---|
| Nazem Alakkad | Designed schema (tables, keys, relationships, view, triggers, procedures) | 2026-03-08 |
| Nazem Alakkad | Implemented Python menus and SQL operations (no ORM) | 2026-03-08 |
| Nazem Alakkad | Added generated test data and query documentation | 2026-03-08 |
| Nazem Alakkad | Refactored menus, validation, and error handling | 2026-03-08 |
