"""
Database connection management for the Retail Invoice Management System.

Provide functions to connect to and close the MySQL database.
"""

# retail_invoice_app/database.py

import mysql.connector
from config import Config  # Import configuration from config.py


def get_db_connection():
    """
    Establish and return a connection to the MySQL database.

    Handle connection errors gracefully.
    """
    try:
        conn = mysql.connector.connect(
            host=Config.DB_HOST,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            database=Config.DB_NAME,
        )
        if conn.is_connected():
            print("Successfully connected to the database!")
            return conn
    except mysql.connector.Error as e:
        print(f"Error connecting to MySQL database: {e}")
        return None


def close_db_connection(conn, cursor):
    """
    Close the database cursor and connection.

    Ensure resources are properly released.
    """
    if cursor:
        cursor.close()
    if conn and conn.is_connected():
        conn.close()
        print("Database connection closed.")
