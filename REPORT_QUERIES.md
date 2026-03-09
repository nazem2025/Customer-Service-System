# SQL Queries for Report

Use these 5 queries in section "SQL Queries" of your report.

## Q1. Show all complaints with customer name (JOIN)
```sql
SELECT complaint_id, customer_name, status, description, created_at
FROM v_complaints_with_customer
ORDER BY complaint_id DESC;
```
Why: Multirelation query with JOIN (through view), used by manager to list complaints.

## Q2. Search complaints by customer name (JOIN)
```sql
SELECT complaint_id, customer_name, status, description, created_at
FROM v_complaints_with_customer
WHERE customer_name LIKE ?
ORDER BY complaint_id DESC;
```
Why: Multirelation query with JOIN, supports manager search feature.

## Q3. Complaints per status (Aggregation + GROUP BY)
```sql
SELECT status, COUNT(*) AS total
FROM complaints
GROUP BY status
ORDER BY total DESC;
```
Why: Required aggregation/grouping query, used in manager statistics.

## Q4. Stored procedure to assign complaint
```sql
CALL sp_take_complaint(?, ?);
```
Why: Demonstrates PROCEDURE use and keeps business logic in DB.

## Q5. Show status history
```sql
SELECT history_id, complaint_id, user_id, old_status, new_status, changed_at
FROM status_history
ORDER BY history_id DESC;
```
Why: Important manager feature to audit complaint status changes over time.

## Trigger (additional requirement support)
Trigger `trg_complaint_auto_on_progress` automatically updates status from `open` to `on_progress`
when an employee starts a complaint.
