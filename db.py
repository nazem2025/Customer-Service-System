import os
import mysql.connector

# Database connection settings from environment variables.
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_USER = os.getenv("DB_USER", "root")
DB_PASS = os.getenv("DB_PASS", "5419421@Nn")
DB_NAME = os.getenv("DB_NAME", "complaint_system")

try:
    db = mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        passwd=DB_PASS,
        database=DB_NAME
    )
except mysql.connector.Error as e:
    print(f"Database connection failed: {e}")
    raise

db_cursor = db.cursor()
