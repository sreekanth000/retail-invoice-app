"""
Configuration for the Retail Invoice Management System.

Contains application and database settings.
"""


class Config:
    """Application configuration settings."""

    # MySQL Database Configuration
    # IMPORTANT: Replace with your actual MySQL credentials
    DB_HOST = "xxxxxxxxxxxxxx"
    DB_USER = "xxxxxxxxxxxx"  # e.g., 'root'
    DB_PASSWORD = "xxxxxxxxxxxxxxxxx"  # e.g., 'mypassword'
    DB_NAME = "xxxxxxxxxx"

    # Flask Secret Key for session management (IMPORTANT for production)
    SECRET_KEY = "xxxxxxxxxxxxxxxx"  # In production, use a strong, randomly generated key
