"""
Business logic and database operations for the Retail Invoice Management System.

Defines Product and Invoice classes for interacting with the database.
"""

from database import get_db_connection, close_db_connection
from datetime import datetime
import mysql.connector


class Product:
    """Manage operations related to the 'products' table."""

    def __init__(
        self,
        product_id=None,
        product_name=None,
        quantity_available=0.0,
        unit_price=0.0,
        last_updated=None,
        is_active=1,
    ):
        """Initialize a Product instance."""
        self.product_id = product_id
        self.product_name = product_name
        self.quantity_available = float(quantity_available)
        self.unit_price = float(unit_price)
        self.last_updated = last_updated if last_updated else datetime.now()
        self.is_active = is_active

    def save(self):
        """
        Add a new product to the database.

        Return True on success, False otherwise.
        """
        conn = get_db_connection()
        if not conn:
            return False
        cursor = conn.cursor()
        try:
            cursor.execute(
                "SELECT product_id FROM products WHERE product_name = %s",
                (self.product_name,),
            )
            if cursor.fetchone():
                print(f"Error: Product '{self.product_name}' already exists.")
                return False
            sql = (
                "INSERT INTO products (product_name, quantity_available, "
                "unit_price, last_updated, is_active) VALUES (%s, %s, %s, %s, %s)"
            )
            cursor.execute(
                sql,
                (
                    self.product_name,
                    self.quantity_available,
                    self.unit_price,
                    self.last_updated,
                    self.is_active,
                ),
            )
            conn.commit()
            self.product_id = cursor.lastrowid
            print(
                f"Product '{self.product_name}' added successfully with ID " f"{self.product_id}!"
            )
            return True
        except mysql.connector.Error as e:
            print(f"Error saving product: {e}")
            conn.rollback()
            return False
        finally:
            close_db_connection(conn, cursor)

    def update(self):
        """
        Update an existing product in the database.

        Return True on success, False otherwise.
        """
        if not self.product_id:
            print("Error: Cannot update product without product_id.")
            return False
        conn = get_db_connection()
        if not conn:
            return False
        cursor = conn.cursor()
        try:
            sql = (
                "UPDATE products SET product_name = %s, quantity_available = %s, "
                "unit_price = %s, last_updated = %s, is_active = %s "
                "WHERE product_id = %s"
            )
            cursor.execute(
                sql,
                (
                    self.product_name,
                    self.quantity_available,
                    self.unit_price,
                    datetime.now(),
                    self.is_active,
                    self.product_id,
                ),
            )
            conn.commit()
            print(f"Product '{self.product_name}' (ID: {self.product_id}) updated " "successfully!")
            return True
        except mysql.connector.Error as e:
            print(f"Error updating product: {e}")
            conn.rollback()
            return False
        finally:
            close_db_connection(conn, cursor)

    @staticmethod
    def inactivate(product_id):
        """
        Perform a soft delete on a product by setting is_active to 0.

        Return True on success, False otherwise.
        """
        conn = get_db_connection()
        if not conn:
            return False
        cursor = conn.cursor()
        try:
            sql = "UPDATE products SET is_active = 0, last_updated = %s " "WHERE product_id = %s"
            cursor.execute(sql, (datetime.now(), product_id))
            conn.commit()
            print(f"Product with ID {product_id} inactivated successfully " "(soft deleted)!")
            return True
        except mysql.connector.Error as e:
            print(f"Error inactivating product: {e}")
            conn.rollback()
            return False
        finally:
            close_db_connection(conn, cursor)

    @staticmethod
    def activate(product_id):
        """
        Activate a product by setting is_active to 1.

        Return True on success, False otherwise.
        """
        conn = get_db_connection()
        if not conn:
            return False
        cursor = conn.cursor()
        try:
            sql = "UPDATE products SET is_active = 1, last_updated = %s " "WHERE product_id = %s"
            cursor.execute(sql, (datetime.now(), product_id))
            conn.commit()
            print(f"Product with ID {product_id} activated successfully!")
            return True
        except mysql.connector.Error as e:
            print(f"Error activating product: {e}")
            conn.rollback()
            return False
        finally:
            close_db_connection(conn, cursor)

    @staticmethod
    def get_all():
        """
        Fetch all products from the database (both active and inactive).

        Return a list of dictionaries, each representing a product.
        """
        conn = get_db_connection()
        if not conn:
            return []
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(
                "SELECT product_id, product_name, quantity_available, unit_price, "
                "last_updated, is_active FROM products ORDER BY product_name ASC"
            )
            products = cursor.fetchall()
            return products
        except mysql.connector.Error as e:
            print(f"Error fetching products: {e}")
            return []
        finally:
            close_db_connection(conn, cursor)

    @staticmethod
    def get_by_id(product_id):
        """
        Fetch a single product by its ID.

        Return a dictionary if found, None otherwise.
        """
        conn = get_db_connection()
        if not conn:
            return None
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(
                "SELECT product_id, product_name, quantity_available, unit_price, "
                "last_updated, is_active FROM products WHERE product_id = %s",
                (product_id,),
            )
            product = cursor.fetchone()
            return product
        except mysql.connector.Error as e:
            print(f"Error fetching product by ID: {e}")
            return None
        finally:
            close_db_connection(conn, cursor)

    @staticmethod
    def get_by_name_like(search_term, include_inactive=False):
        """
        Search for products by name (case-insensitive, partial match).

        By default, only return active products. Set include_inactive=True to get
        all. Return a list of dictionaries.
        """
        conn = get_db_connection()
        if not conn:
            return []
        cursor = conn.cursor(dictionary=True)
        try:
            sql = (
                "SELECT product_id, product_name, quantity_available, unit_price, "
                "last_updated, is_active FROM products WHERE product_name LIKE %s"
            )
            params = [f"%{search_term}%"]
            if not include_inactive:
                sql += " AND is_active = 1"
            sql += " ORDER BY product_name ASC"
            cursor.execute(sql, tuple(params))
            products = cursor.fetchall()
            return products
        except mysql.connector.Error as e:
            print(f"Error searching products by name: {e}")
            return []
        finally:
            close_db_connection(conn, cursor)

    @staticmethod
    def update_quantity(product_id, quantity_change):
        """
        Update the quantity_available for a product.

        quantity_change can be positive (add stock) or negative (deduct stock).
        Return True on success, False otherwise.
        """
        conn = get_db_connection()
        if not conn:
            return False
        cursor = conn.cursor()
        try:
            sql = (
                "UPDATE products SET quantity_available = quantity_available + %s, "
                "last_updated = %s WHERE product_id = %s"
            )
            cursor.execute(sql, (float(quantity_change), datetime.now(), product_id))
            conn.commit()
            return True
        except mysql.connector.Error as e:
            print(f"Error updating product quantity: {e}")
            conn.rollback()
            return False
        finally:
            close_db_connection(conn, cursor)


class Invoice:
    """Manage operations related to the 'invoices' and 'invoice_items' tables."""

    def __init__(
        self,
        invoice_id=None,
        customer_name=None,
        grand_total=0.0,
        invoice_date=None,
        items=None,
    ):
        """Initialize an Invoice instance."""
        self.invoice_id = invoice_id
        self.customer_name = customer_name
        self.grand_total = float(grand_total)
        self.invoice_date = invoice_date if invoice_date else datetime.now()
        self.items = items if items is not None else []

    def save(self):
        """
        Save a new invoice and its items to the database.

        Handle transactions to ensure atomicity and update product quantities.
        Return the new invoice_id on success, None otherwise.
        """
        conn = get_db_connection()
        if not conn:
            return None
        cursor = conn.cursor()
        try:
            conn.start_transaction()
            sql_invoice = (
                "INSERT INTO invoices (customer_name, grand_total, invoice_date) "
                "VALUES (%s, %s, %s)"
            )
            cursor.execute(
                sql_invoice,
                (self.customer_name, self.grand_total, self.invoice_date),
            )
            self.invoice_id = cursor.lastrowid
            sql_item = (
                "INSERT INTO invoice_items (invoice_id, product_id, quantity_sold, "
                "unit_price, item_total) VALUES (%s, %s, %s, %s, %s)"
            )
            sql_update_qty = (
                "UPDATE products SET quantity_available = quantity_available - %s, "
                "last_updated = %s WHERE product_id = %s"
            )
            for item in self.items:
                quantity_sold = float(item["quantity_sold"])
                unit_price = float(item["unit_price"])
                item_total = float(item["item_total"])
                product_in_db = Product.get_by_id(item["product_id"])
                if (
                    not product_in_db
                    or product_in_db["is_active"] == 0
                    or float(product_in_db["quantity_available"]) < quantity_sold
                ):
                    product_name_for_error = (
                        product_in_db["product_name"] if product_in_db else "Unknown Product"
                    )
                    if not product_in_db:
                        raise ValueError(f"Product '{product_name_for_error}' not found.")
                    elif product_in_db["is_active"] == 0:
                        raise ValueError(
                            f"Product '{product_name_for_error}' is currently "
                            "inactive and cannot be sold."
                        )
                    else:
                        raise ValueError(
                            f"Insufficient stock for product: "
                            f"{product_name_for_error}. Only "
                            f"{product_in_db['quantity_available']:.3f} kgs "
                            f"available, tried to sell {quantity_sold:.3f} kgs."
                        )
                cursor.execute(
                    sql_item,
                    (
                        self.invoice_id,
                        item["product_id"],
                        quantity_sold,
                        unit_price,
                        item_total,
                    ),
                )
                cursor.execute(
                    sql_update_qty,
                    (quantity_sold, datetime.now(), item["product_id"]),
                )
            conn.commit()
            print(
                f"Invoice {self.invoice_id} saved successfully! Grand Total: "
                f"{self.grand_total:.2f}"
            )
            return self.invoice_id
        except ValueError as ve:
            print(f"Stock/Product status error: {ve}")
            conn.rollback()
            return None
        except mysql.connector.Error as e:
            print(f"Error saving invoice: {e}")
            conn.rollback()
            return None
        except Exception as e:
            print(f"An unexpected error occurred during invoice saving: {e}")
            conn.rollback()
            return None
        finally:
            close_db_connection(conn, cursor)

    @staticmethod
    def get_all(start_date=None, end_date=None, customer_name=None):
        """
        Fetch invoices from the database, with optional filtering by date range and customer name.

        Return a list of dictionaries.
        """
        conn = get_db_connection()
        if not conn:
            return []
        cursor = conn.cursor(dictionary=True)
        try:
            sql = "SELECT invoice_id, invoice_date, customer_name, grand_total " "FROM invoices"
            conditions = []
            params = []
            if start_date:
                conditions.append("invoice_date >= %s")
                params.append(start_date)
            if end_date:
                conditions.append("invoice_date <= %s")
                params.append(end_date)
            if customer_name:
                conditions.append("customer_name LIKE %s")
                params.append(f"%{customer_name}%")
            if conditions:
                sql += " WHERE " + " AND ".join(conditions)
            sql += " ORDER BY invoice_date DESC"
            cursor.execute(sql, tuple(params))
            invoices = cursor.fetchall()
            return invoices
        except mysql.connector.Error as e:
            print(f"Error fetching invoices: {e}")
            return []
        finally:
            close_db_connection(conn, cursor)

    @staticmethod
    def get_by_id(invoice_id):
        """
        Fetch a single invoice and its items by invoice_id.

        Return a dictionary containing invoice details and a list of item
        dictionaries.
        """
        conn = get_db_connection()
        if not conn:
            return None
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(
                "SELECT invoice_id, invoice_date, customer_name, grand_total "
                "FROM invoices WHERE invoice_id = %s",
                (invoice_id,),
            )
            invoice_header = cursor.fetchone()
            if not invoice_header:
                return None
            sql_items = (
                "SELECT ii.item_id, ii.product_id, ii.quantity_sold, ii.unit_price, "
                "ii.item_total, p.product_name FROM invoice_items ii "
                "JOIN products p ON ii.product_id = p.product_id "
                "WHERE ii.invoice_id = %s"
            )
            cursor.execute(sql_items, (invoice_id,))
            invoice_items = cursor.fetchall()
            invoice_header["items"] = invoice_items
            return invoice_header
        except mysql.connector.Error as e:
            print(f"Error fetching invoice details: {e}")
            return None
        finally:
            close_db_connection(conn, cursor)
