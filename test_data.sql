-- Test data for complaint_system
-- Run after first_time_setup.sql

USE complaint_system;

SET FOREIGN_KEY_CHECKS = 0;
TRUNCATE TABLE complaint_receipt;
TRUNCATE TABLE receipts;
TRUNCATE TABLE messages;
TRUNCATE TABLE status_history;
TRUNCATE TABLE complaints;
TRUNCATE TABLE users;
SET FOREIGN_KEY_CHECKS = 1;

-- Users
-- IDs are fixed for easier testing in menus.
INSERT INTO users (user_id, full_name, email, role) VALUES
(1, 'Main Manager', 'manager@local.test', 'manager'),
(2, 'First Employee', 'employee1@local.test', 'employee'),
(3, 'Second Employee', 'employee2@local.test', 'employee'),
(4, 'Sara Ali', 'sara@local.test', 'customer'),
(5, 'Omar Hassan', 'omar@local.test', 'customer'),
(6, 'Lina Noor', 'lina@local.test', 'customer');

-- Complaints
-- Include open/unassigned + assigned + resolved/closed for full menu testing.
INSERT INTO complaints
    (complaint_id, customer_id, assigned_employee_id, status, description, created_at)
VALUES
    (1, 4, NULL, 'open', 'Phone battery drains very fast after update.', '2026-03-01'),
    (2, 5, 2, 'on_progress', 'Delivery arrived damaged, screen cracked.', '2026-03-02'),
    (3, 6, 3, 'resolved', 'Payment was charged twice.', '2026-03-03'),
    (4, 4, 2, 'closed', 'Warranty claim took too long.', '2026-03-04'),
    (5, 5, NULL, 'open', 'Received wrong item in package.', '2026-03-05'),
    (6, 6, 2, 'on_progress', 'Refund not received yet.', '2026-03-06');

-- Messages
INSERT INTO messages
    (message_id, complaint_id, sender_id, message_type, message_text, sent_at)
VALUES
    (1, 2, 5, 'customer', 'Please help, the item is unusable.', '2026-03-02 11:20:00'),
    (2, 2, 2, 'employee', 'We are checking this with the supplier.', '2026-03-02 12:00:00'),
    (3, 3, 6, 'customer', 'I can share payment screenshots.', '2026-03-03 15:00:00'),
    (4, 3, 3, 'employee', 'Thanks, issue is now fixed and refunded.', '2026-03-03 16:30:00'),
    (5, 4, 1, 'manager', 'Case reviewed and closed.', '2026-03-04 09:00:00'),
    (6, 6, 6, 'customer', 'Any update on my refund?', '2026-03-06 10:30:00');

-- Receipts
INSERT INTO receipts
    (receipt_id, receipt_number, amount, store_name, note, created_at)
VALUES
    (1, 'RCPT-1001', 1299.00, 'TechStore', 'Screen replacement estimate', '2026-03-02'),
    (2, 'RCPT-1002', 450.00, 'OnlineShop', 'Shipping compensation', '2026-03-04');

INSERT INTO complaint_receipt (complaint_id, receipt_id) VALUES
    (2, 1),
    (4, 2);

-- Status history (manager view)
INSERT INTO status_history
    (history_id, complaint_id, user_id, old_status, new_status, changed_at)
VALUES
    (1, 2, 2, 'open', 'on_progress', '2026-03-02 11:40:00'),
    (2, 3, 3, 'open', 'on_progress', '2026-03-03 15:20:00'),
    (3, 3, 3, 'on_progress', 'resolved', '2026-03-03 16:25:00'),
    (4, 4, 2, 'on_progress', 'closed', '2026-03-04 08:50:00');

-- After explicit IDs, set next AUTO_INCREMENT values safely.
ALTER TABLE users AUTO_INCREMENT = 7;
ALTER TABLE complaints AUTO_INCREMENT = 7;
ALTER TABLE messages AUTO_INCREMENT = 7;
ALTER TABLE receipts AUTO_INCREMENT = 3;
ALTER TABLE status_history AUTO_INCREMENT = 5;

-- Quick testing accounts:
-- manager  -> user_id 1
-- employee -> user_id 2 or 3
-- customer names: Sara Ali / Omar Hassan / Lina Noor
