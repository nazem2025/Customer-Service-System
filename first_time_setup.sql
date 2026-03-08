-- First-time setup for complaint_system
-- Run this file once before starting the Python program.

DROP DATABASE IF EXISTS complaint_system;
CREATE DATABASE complaint_system
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE complaint_system;

-- Users: manager, employee, customer
CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(120) NOT NULL,
    email VARCHAR(190) NOT NULL UNIQUE,
    role ENUM('manager', 'employee', 'customer') NOT NULL,
    created_at DATE NOT NULL DEFAULT (CURRENT_DATE)
);

-- Main complaint table
CREATE TABLE complaints (
    complaint_id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT NOT NULL,
    assigned_employee_id INT NULL,
    status ENUM('open', 'on_progress', 'resolved', 'closed') NOT NULL DEFAULT 'open',
    description TEXT NOT NULL,
    created_at DATE NOT NULL DEFAULT (CURRENT_DATE),
    CONSTRAINT fk_complaint_customer
      FOREIGN KEY (customer_id) REFERENCES users(user_id),
    CONSTRAINT fk_complaint_employee
      FOREIGN KEY (assigned_employee_id) REFERENCES users(user_id)
);

-- Keep status values strict and default to open.
ALTER TABLE complaints
MODIFY status ENUM('open', 'on_progress', 'resolved', 'closed') NOT NULL DEFAULT 'open';

-- Messages on complaints
CREATE TABLE messages (
    message_id INT AUTO_INCREMENT PRIMARY KEY,
    complaint_id INT NOT NULL,
    sender_id INT NOT NULL,
    message_type ENUM('customer', 'employee', 'manager') NOT NULL,
    message_text TEXT NOT NULL,
    sent_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_message_complaint
      FOREIGN KEY (complaint_id) REFERENCES complaints(complaint_id),
    CONSTRAINT fk_message_sender
      FOREIGN KEY (sender_id) REFERENCES users(user_id)
);

-- Optional receipt support
CREATE TABLE receipts (
    receipt_id INT AUTO_INCREMENT PRIMARY KEY,
    receipt_number VARCHAR(100) NOT NULL UNIQUE,
    amount DECIMAL(10,2) NOT NULL,
    store_name VARCHAR(120) NOT NULL,
    note TEXT NULL,
    created_at DATE NOT NULL DEFAULT (CURRENT_DATE)
);

CREATE TABLE complaint_receipt (
    complaint_id INT NOT NULL,
    receipt_id INT NOT NULL,
    PRIMARY KEY (complaint_id, receipt_id),
    CONSTRAINT fk_cr_complaint
      FOREIGN KEY (complaint_id) REFERENCES complaints(complaint_id),
    CONSTRAINT fk_cr_receipt
      FOREIGN KEY (receipt_id) REFERENCES receipts(receipt_id)
);

-- Status history used by manager menu
CREATE TABLE status_history (
    history_id INT AUTO_INCREMENT PRIMARY KEY,
    complaint_id INT NOT NULL,
    user_id INT NULL,
    old_status ENUM('open', 'on_progress', 'resolved', 'closed') NOT NULL,
    new_status ENUM('open', 'on_progress', 'resolved', 'closed') NOT NULL,
    changed_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_history_complaint
      FOREIGN KEY (complaint_id) REFERENCES complaints(complaint_id),
    CONSTRAINT fk_history_user
      FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- Indexes
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_complaints_customer_id ON complaints(customer_id);
CREATE INDEX idx_complaints_assigned_employee_id ON complaints(assigned_employee_id);
CREATE INDEX idx_complaints_status ON complaints(status);
CREATE INDEX idx_messages_complaint_id ON messages(complaint_id);
CREATE INDEX idx_messages_sender_id ON messages(sender_id);

-- View for easier manager reads/search
CREATE VIEW v_complaints_with_customer AS
SELECT
    c.complaint_id,
    c.customer_id,
    u.full_name AS customer_name,
    c.assigned_employee_id,
    c.status,
    c.description,
    c.created_at
FROM complaints c
JOIN users u ON u.user_id = c.customer_id;

-- Trigger: employee starts complaint => auto move open -> on_progress
DELIMITER //
CREATE TRIGGER trg_complaint_auto_on_progress
BEFORE UPDATE ON complaints
FOR EACH ROW
BEGIN
    IF OLD.assigned_employee_id IS NULL
       AND NEW.assigned_employee_id IS NOT NULL
       AND OLD.status = 'open' THEN
        SET NEW.status = 'on_progress';
    END IF;
END //
DELIMITER ;

-- Trigger: log all status changes
DELIMITER //
CREATE TRIGGER trg_complaint_status_history
AFTER UPDATE ON complaints
FOR EACH ROW
BEGIN
    IF OLD.status <> NEW.status THEN
        INSERT INTO status_history (complaint_id, user_id, old_status, new_status)
        VALUES (NEW.complaint_id, NEW.assigned_employee_id, OLD.status, NEW.status);
    END IF;
END //
DELIMITER ;

-- Stored procedure used by employee.py when taking a complaint
DELIMITER //
CREATE PROCEDURE sp_take_complaint(IN p_complaint_id INT, IN p_employee_id INT)
BEGIN
    UPDATE complaints
    SET assigned_employee_id = p_employee_id
    WHERE complaint_id = p_complaint_id
      AND assigned_employee_id IS NULL
      AND status = 'open';
END //
DELIMITER ;

-- Stored procedure: create customer
DELIMITER //
CREATE PROCEDURE sp_create_customer(
    IN p_full_name VARCHAR(120),
    IN p_email VARCHAR(190)
)
BEGIN
    INSERT INTO users (full_name, email, role)
    VALUES (p_full_name, p_email, 'customer');
END //
DELIMITER ;

-- Stored procedure: update customer profile
DELIMITER //
CREATE PROCEDURE sp_update_customer(
    IN p_customer_id INT,
    IN p_full_name VARCHAR(120),
    IN p_email VARCHAR(190)
)
BEGIN
    UPDATE users
    SET full_name = p_full_name,
        email = p_email
    WHERE user_id = p_customer_id
      AND role = 'customer';
END //
DELIMITER ;

-- Optional starter accounts
INSERT INTO users (full_name, email, role)
VALUES
('Main Manager', 'manager@local.test', 'manager'),
('First Employee', 'employee@local.test', 'employee');
