# Retail Management System

## Project Overview
This Retail Management System is a simple Flask-based web application designed to help small retail stores manage their products and sales invoices. It provides functionalities for adding new products, tracking available quantity, generating sales invoices, and viewing past transactions with filtering capabilities. The system also includes a **soft delete** mechanism for products, allowing historical data to be preserved while marking products as inactive.

## Features
### Product Management
- Add new products with name, quantity, and unit price.
- View a list of all products (active and inactive).
- Search products by name.
- Edit existing product details.
- Soft delete (deactivate) products, marking them as inactive rather than permanently removing them (useful for retaining historical sales data).
- Activate previously deactivated products.
- Track the last updated timestamp for each product.
- Display product names in camel case (title case).

### Invoice Management
- Create new sales invoices by adding products to a cart.
- Automatic calculation of grand total.
- View a list of all past invoices.
- View detailed information for each invoice, including items sold.
- Filter invoices by date range (start date, end date) and customer name.
- Print invoices in a compact, thermal printer-friendly receipt format (57mm width, continuous height).

## Technologies Used
- **Backend:** Flask (Python Web Framework)
- **Database:** MySQL
- **Frontend:** HTML, Tailwind CSS, JavaScript (for product search suggestions)
- **Database Connector:** mysql-connector-python
- **Templating:** Jinja2

## Setup Instructions

### Prerequisites
Before you begin, ensure you have the following installed:
- Python 3.8+
- MySQL Server (e.g., MySQL Community Server, XAMPP, WAMP, Docker)
- pip (Python package installer)

### 1. Database Setup
First, you need to create the database and tables, and then update them as per the features.

#### Create the Database and Initial Tables
Connect to your MySQL server (e.g., via MySQL Workbench, command line, or phpMyAdmin) and execute the following SQL commands:

```sql
-- Create the database
CREATE DATABASE IF NOT EXISTS retail_invoice_db;
USE retail_invoice_db;

-- Create the products table
CREATE TABLE IF NOT EXISTS products (
    product_id INT AUTO_INCREMENT PRIMARY KEY,
    product_name VARCHAR(255) NOT NULL UNIQUE,
    quantity_available DECIMAL(10, 3) NOT NULL DEFAULT 0.000, -- e.g., for kgs
    unit_price DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP, -- Added for tracking updates
    is_active TINYINT(1) DEFAULT 1 -- Added for soft delete (1=active, 0=inactive)
);

-- Create the invoices table
CREATE TABLE IF NOT EXISTS invoices (
    invoice_id INT AUTO_INCREMENT PRIMARY KEY,
    customer_name VARCHAR(255) NOT NULL,
    grand_total DECIMAL(10, 2) NOT NULL,
    invoice_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create the invoice_items table (junction table)
CREATE TABLE IF NOT EXISTS invoice_items (
    item_id INT AUTO_INCREMENT PRIMARY KEY,
    invoice_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity_sold DECIMAL(10, 3) NOT NULL,
    unit_price DECIMAL(10, 2) NOT NULL, -- Price at the time of sale
    item_total DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (invoice_id) REFERENCES invoices(invoice_id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(product_id) -- No CASCADE DELETE for products to allow soft delete
);
```

#### Update Existing Tables (if you are upgrading from an older version)
If you have an existing products table without `last_updated` or `is_active`, or an invoices table that previously had `sub_total` or `sales_tax`, run these ALTER TABLE commands:

```sql
USE retail_invoice_db;

-- Add is_active column to products (if not already present)
ALTER TABLE products
ADD COLUMN is_active TINYINT(1) DEFAULT 1;

-- Add last_updated column to products (if not already present)
ALTER TABLE products
ADD COLUMN last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP;

-- Remove sub_total and sales_tax columns from invoices (if they were added previously)
-- ONLY run these if you have these columns and want to remove them!
ALTER TABLE invoices
DROP COLUMN IF EXISTS sales_tax,
DROP COLUMN IF EXISTS sub_total;
```

### 2. Application Installation

#### Clone the Repository (or set up your project directory)
If you have a Git repository, clone it:

```sh
git clone <your-repo-url>
cd retail_management_system
```

Otherwise, create a directory and put all your Flask application files (`app.py`, `config.py`, `models.py`, `database.py`, and the `templates` and `static` folders) inside it.

#### Create a Python Virtual Environment
It's highly recommended to use a virtual environment to manage dependencies.

```sh
python -m venv venv
```

#### Activate the Virtual Environment
- **On Windows:**
  ```sh
  .\venv\Scripts\activate
  ```
- **On macOS/Linux:**
  ```sh
  source venv/bin/activate
  ```

#### Install Dependencies
Install the required Python packages using pip:

```sh
pip install Flask mysql-connector-python
```

#### Configure Database Connection
Open `retail_invoice_app/config.py` and update the `DB_USER`, `DB_PASSWORD`, and `DB_NAME` (if different from `retail_invoice_db`) with your MySQL credentials.

```python
# retail_invoice_app/config.py
class Config:
    DB_HOST = 'localhost'
    DB_USER = 'your_mysql_user'      # e.g., 'root'
    DB_PASSWORD = 'your_mysql_password' # e.g., 'mypassword'
    DB_NAME = 'retail_invoice_db'
    SECRET_KEY = 'supersecretkey_for_dev' # CHANGE THIS IN PRODUCTION!
```

> **Security Note:** For production environments, `SECRET_KEY` should be a strong, randomly generated value stored securely (e.g., in an environment variable), not directly in the code.

## Running the Application
1. Ensure your MySQL server is running.
2. Navigate to your project's root directory (where `app.py` is located) in your activated virtual environment.
3. Run the Flask application:

```sh
flask run
```

If you're in development, `debug=True` is set in `app.py`, so changes will auto-reload.

You should see output similar to:

```
 * Serving Flask app 'app'
 * Debug mode: on
 ...
 * Running on http://127.0.0.1:5000
```

Open your web browser and go to [http://127.0.0.1:5000](http://127.0.0.1:5000) (or the address shown in your terminal).

## Usage
- **Dashboard (`/`)**: Overview of the system.
- **Products (`/products`)**:
  - Add new products using the form.
  - View all products in the table.
  - Use the search bar to filter products by name.
  - Click "Edit" to modify a product's details.
  - Click "Deactivate" to soft-delete a product (it will become inactive and won't appear in invoice creation search, but its history remains).
  - Click "Activate" to make an inactive product available for sale again.
- **Create Invoice (`/invoice/create`)**:
  - Search for products using the autocomplete search bar. Only active products will appear in suggestions.
  - Add desired quantity of products to the cart.
  - Remove items from the cart if needed.
  - Enter customer name and click "Complete Sale" to create the invoice.
- **View Invoices (`/invoices`)**:
  - See a list of all sales invoices.
  - Use the "Filter Invoices" section to narrow down results by date range and customer name.
  - Click "View Details" to see the items included in a specific invoice.
  - From the invoice detail page, you can print a compact receipt suitable for thermal printers.
