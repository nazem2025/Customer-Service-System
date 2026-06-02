import os
import mysql.connector
from flask.cli import load_dotenv

load_dotenv()

# Database connection settings from environment variables.
DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER" )
DB_PASS = os.getenv("DB_PASS")
DB_NAME = os.getenv("DB_NAME")

try:
    db = mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        passwd=DB_PASS,
        database=DB_NAME
    )
except mysql.connector.Error :
    print(f"Database connection failed:")
    raise

db_cursor = db.cursor()
