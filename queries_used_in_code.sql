-- All SQL used in current Python codebase
-- Source files: main.py, employee_menu.py, body.py
USE complaint_system;

-- 1) Login / role check
SELECT role FROM users WHERE user_id = ?;

-- 2) Find customer by full name
SELECT user_id
FROM users
WHERE full_name = ? AND role = 'customer';

-- 3) Procedure call: create customer
CALL sp_create_customer(?, ?);

-- 4) Get customer id by email after create
SELECT user_id FROM users WHERE email = ? AND role = 'customer';

-- 5) Check customer exists before update
SELECT user_id FROM users WHERE user_id = ? AND role = 'customer';

-- 6) Procedure call: update customer profile
CALL sp_update_customer(?, ?, ?);

-- 7) Employee: check complaint belongs to logged-in employee
SELECT complaint_id FROM complaints
WHERE complaint_id = ? AND assigned_employee_id = ?;

-- 8) Employee: view my assigned complaints
SELECT c.complaint_id,
       u.full_name,
       c.status,
       c.description,
       c.created_at
FROM complaints c
JOIN users u ON c.customer_id = u.user_id
WHERE c.assigned_employee_id = ?
ORDER BY c.complaint_id DESC;

-- 9) Employee: view new open complaints (for take)
SELECT c.complaint_id,
       u.full_name,
       c.status,
       c.description,
       c.created_at
FROM complaints c
JOIN users u ON c.customer_id = u.user_id
WHERE c.assigned_employee_id IS NULL
  AND c.status = 'open'
ORDER BY c.complaint_id DESC;

-- 10) Employee: verify complaint is still available to take
SELECT complaint_id
FROM complaints
WHERE complaint_id = ?
  AND assigned_employee_id IS NULL
  AND status = 'open';

-- 11) Procedure call: take complaint
CALL sp_take_complaint(?, ?);

-- 12) Employee: verify take result
SELECT assigned_employee_id, status
FROM complaints
WHERE complaint_id = ?;

-- 13) Employee: update status (only own complaints)
UPDATE complaints
SET status = ?
WHERE complaint_id = ?
  AND assigned_employee_id = ?;

-- 14) Employee: list complaints available for message flow
SELECT c.complaint_id,
       u.full_name,
       c.status
FROM complaints c
JOIN users u ON c.customer_id = u.user_id
WHERE c.assigned_employee_id = ?
ORDER BY c.complaint_id DESC;

-- 15) Employee: view messages in one complaint
SELECT u.full_name,
       m.message_type,
       m.message_text,
       m.sent_at
FROM messages m
JOIN users u ON m.sender_id = u.user_id
WHERE m.complaint_id = ?
ORDER BY m.sent_at ASC;

-- 16) Employee: send message
INSERT INTO messages (complaint_id, sender_id, message_type, message_text)
VALUES (?, ?, 'employee', ?);

-- 17) Employee: add receipt
INSERT INTO receipts (receipt_number, amount, store_name, note)
VALUES (?, ?, ?, ?);

-- 18) Employee: link receipt to complaint
INSERT INTO complaint_receipt (complaint_id, receipt_id)
VALUES (?, ?);

-- 19) Employee: view receipts for own complaint
SELECT r.receipt_number,
       r.amount,
       r.store_name,
       r.note
FROM receipts r
JOIN complaint_receipt cr ON r.receipt_id = cr.receipt_id
JOIN complaints c ON c.complaint_id = cr.complaint_id
WHERE cr.complaint_id = ?
  AND c.assigned_employee_id = ?;

-- 20) Manager: view all complaints
SELECT complaint_id, customer_name, status, description, created_at
FROM v_complaints_with_customer
ORDER BY complaint_id DESC;

-- 21) Manager: view all messages
SELECT message_id, complaint_id, sender_id, message_type, message_text, sent_at
FROM messages
ORDER BY message_id DESC;

-- 22) Manager: view status history
SELECT history_id, complaint_id, user_id, old_status, new_status, changed_at
FROM status_history
ORDER BY history_id DESC;

-- 23) Manager: statistics - complaints per status
SELECT status, COUNT(*) AS total
FROM complaints
GROUP BY status
ORDER BY total DESC;

-- 25) Complaints search (manager) by complaint ID
SELECT complaint_id, customer_name, status, description, created_at
FROM v_complaints_with_customer
WHERE complaint_id = ?;

-- 26) Complaints search (employee) by complaint ID (own only)
SELECT c.complaint_id,
       u.full_name,
       c.status,
       c.description,
       c.created_at
FROM complaints c
JOIN users u ON c.customer_id = u.user_id
WHERE c.assigned_employee_id = ?
  AND c.complaint_id = ?;

-- 27) Complaints search (manager) by customer name
SELECT complaint_id, customer_name, status, description, created_at
FROM v_complaints_with_customer
WHERE customer_name LIKE ?
ORDER BY complaint_id DESC;

-- 28) Complaints search (employee) by customer name (own only)
SELECT c.complaint_id,
       u.full_name,
       c.status,
       c.description,
       c.created_at
FROM complaints c
JOIN users u ON c.customer_id = u.user_id
WHERE c.assigned_employee_id = ?
  AND u.full_name LIKE ?
ORDER BY c.complaint_id DESC;

-- 29) Customer: create complaint
INSERT INTO complaints (customer_id, description)
VALUES (?, ?);

-- 30) Customer: view own complaints
SELECT complaint_id, status, description, created_at
FROM complaints
WHERE customer_id = ?
ORDER BY complaint_id DESC;

-- 31) Customer: verify complaint ownership before sending message
SELECT complaint_id
FROM complaints
WHERE complaint_id = ? AND customer_id = ?;

-- 32) Customer: send message
INSERT INTO messages (complaint_id, sender_id, message_type, message_text)
VALUES (?, ?, 'customer', ?);
