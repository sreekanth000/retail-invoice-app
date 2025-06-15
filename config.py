"""
Configuration for the Retail Invoice Management System.

Contains application and database settings.
"""


class Config:
    """Application configuration settings."""

    # MySQL Database Configuration
    # IMPORTANT: Replace with your actual MySQL credentials
    DB_HOST = "tafeprivatecallcenter.cjbmyqbvrjhw.ap-south-1.rds.amazonaws.com"
    DB_USER = "root"  # e.g., 'root'
    DB_PASSWORD = "MPCTafeMF2024_06_21_KSC"  # e.g., 'mypassword'
    DB_NAME = "retail_invoice_db"

    # Flask Secret Key for session management (IMPORTANT for production)
    SECRET_KEY = "MPCTafeMF2024_06_21_KSC"  # In production, use a strong, randomly generated key
