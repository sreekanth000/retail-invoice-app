"""
Main Flask application for the Retail Invoice Management System.

Handles routing, request processing, and rendering templates.
"""

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session,
    jsonify,
)
from config import Config
from models import Product, Invoice
from datetime import datetime

app = Flask(__name__)
app.config.from_object(Config)


@app.context_processor
def inject_now():
    """Inject the current datetime for use in templates."""
    return {"now": datetime.now}


@app.route("/")
def index():
    """Render the home page/dashboard."""
    return render_template("index.html", title="Dashboard")


# --- Product Routes ---
@app.route("/products", methods=["GET", "POST"])
def products():
    """Handle adding and displaying products, and product search."""
    if request.method == "POST":
        product_name = request.form["product_name"].strip()
        quantity_available_str = request.form["quantity_available"].strip()
        unit_price_str = request.form["unit_price"].strip()

        if not product_name or not quantity_available_str or not unit_price_str:
            flash("All fields are required!", "danger")
            return redirect(url_for("products"))

        try:
            quantity_available = float(quantity_available_str)
            unit_price = float(unit_price_str)

            if quantity_available < 0 or unit_price <= 0:
                flash(
                    "Quantity must be non-negative, Unit Price must be positive!",
                    "danger",
                )
                return redirect(url_for("products"))

            new_product = Product(
                product_name=product_name,
                quantity_available=quantity_available,
                unit_price=unit_price,
                is_active=1,
            )
            if new_product.save():
                flash(
                    f'Product "{product_name}" added successfully!',
                    "success",
                )
            else:
                flash(
                    f'Failed to add product "{product_name}". It might already ' f"exist.",
                    "danger",
                )
        except ValueError:
            flash(
                "Invalid quantity or price format. Please enter numbers.",
                "danger",
            )
        except Exception as e:
            flash(f"An unexpected error occurred: {e}", "danger")

        return redirect(url_for("products"))

    search_query = request.args.get("search_query", "").strip()
    if search_query:
        all_products = Product.get_by_name_like(search_query, include_inactive=True)
    else:
        all_products = Product.get_all()

    return render_template(
        "products.html",
        products=all_products,
        title="Products",
        search_query=search_query,
    )


@app.route("/products/edit/<int:product_id>", methods=["GET", "POST"])
def edit_product(product_id):
    """Edit an existing product."""
    product = Product.get_by_id(product_id)
    if not product:
        flash("Product not found.", "danger")
        return redirect(url_for("products"))

    if request.method == "POST":
        product_name = request.form["product_name"].strip()
        quantity_available_str = request.form["quantity_available"].strip()
        unit_price_str = request.form["unit_price"].strip()

        if not product_name or not quantity_available_str or not unit_price_str:
            flash("All fields are required!", "danger")
            return redirect(url_for("edit_product", product_id=product_id))

        try:
            quantity_available = float(quantity_available_str)
            unit_price = float(unit_price_str)

            if quantity_available < 0 or unit_price <= 0:
                flash(
                    "Quantity must be non-negative, Unit Price must be positive!",
                    "danger",
                )
                return redirect(url_for("edit_product", product_id=product_id))

            updated_product = Product(
                product_id=product_id,
                product_name=product_name,
                quantity_available=quantity_available,
                unit_price=unit_price,
                is_active=product["is_active"],
            )
            if updated_product.update():
                flash(
                    f'Product "{product_name}" updated successfully!',
                    "success",
                )
                return redirect(url_for("products"))
            else:
                flash(
                    f'Failed to update product "{product_name}".',
                    "danger",
                )
        except ValueError:
            flash(
                "Invalid quantity or price format. Please enter numbers.",
                "danger",
            )
        except Exception as e:
            flash(f"An unexpected error occurred: {e}", "danger")

    return render_template(
        "edit_product.html",
        product=product,
        title=f'Edit Product: {product["product_name"]}',
    )


@app.route("/products/deactivate/<int:product_id>", methods=["POST"])
def deactivate_product(product_id):
    """Deactivate (soft delete) a product."""
    product = Product.get_by_id(product_id)
    if not product:
        flash("Product not found.", "danger")
        return redirect(url_for("products"))

    if Product.inactivate(product_id):
        flash(
            f'Product "{product["product_name"]}" marked as inactive.',
            "success",
        )
    else:
        flash(
            f'Failed to deactivate product "{product["product_name"]}".',
            "danger",
        )

    return redirect(url_for("products"))


@app.route("/products/activate/<int:product_id>", methods=["POST"])
def activate_product(product_id):
    """Activate a previously deactivated product."""
    product = Product.get_by_id(product_id)
    if not product:
        flash("Product not found.", "danger")
        return redirect(url_for("products"))

    if Product.activate(product_id):
        flash(
            f'Product "{product["product_name"]}" marked as active.',
            "success",
        )
    else:
        flash(
            f'Failed to activate product "{product["product_name"]}".',
            "danger",
        )

    return redirect(url_for("products"))


@app.route("/api/products/search")
def api_product_search():
    """Return product name suggestions for autocomplete (JSON)."""
    query = request.args.get("query", "").strip()
    if len(query) < 3:
        return jsonify([])

    products = Product.get_by_name_like(query, include_inactive=False)
    suggestions = [{"product_name": p["product_name"]} for p in products]
    return jsonify(suggestions)


# --- Invoice Routes ---
@app.route("/invoice/create", methods=["GET", "POST"])
def create_invoice():
    """Create a new invoice and manage the cart in session."""
    if "cart" not in session:
        session["cart"] = []

    if request.method == "POST":
        action = request.form.get("action")

        if action == "add_to_cart":
            product_search_term = request.form["product_search"].strip()
            quantity_str = request.form["quantity_to_sell"].strip()

            if not product_search_term or not quantity_str:
                flash(
                    "Product search term and quantity are required to add to cart.",
                    "danger",
                )
                return redirect(url_for("create_invoice"))

            try:
                quantity_to_sell = float(quantity_str)
                if quantity_to_sell <= 0:
                    flash("Quantity must be positive.", "danger")
                    return redirect(url_for("create_invoice"))

                found_products = Product.get_by_name_like(
                    product_search_term, include_inactive=False
                )
                product = next(
                    (p for p in found_products if p["product_name"] == product_search_term),
                    None,
                )

                if not product:
                    flash(
                        f'Product "{product_search_term}" not found, is inactive, or '
                        "exact match not selected. Please select from suggestions or "
                        "type full name carefully.",
                        "warning",
                    )
                    return redirect(url_for("create_invoice"))

                if quantity_to_sell > float(product["quantity_available"]):
                    flash(
                        f"Insufficient stock for {product['product_name']}. Only "
                        f"{product['quantity_available']:.3f} kgs available.",
                        "danger",
                    )
                    return redirect(url_for("create_invoice"))

                cart_item = {
                    "product_id": product["product_id"],
                    "product_name": product["product_name"],
                    "unit_price": float(product["unit_price"]),
                    "quantity_sold": quantity_to_sell,
                    "item_total": quantity_to_sell * float(product["unit_price"]),
                }
                session["cart"].append(cart_item)
                session.modified = True
                flash(
                    f"Added {quantity_to_sell:.3f} kgs x {product['product_name']} to cart.",
                    "info",
                )

            except ValueError as e:
                flash(f"Invalid quantity or product status: {e}", "danger")
            except Exception as e:
                flash(f"An error occurred: {e}", "danger")

            return redirect(url_for("create_invoice"))

        elif action == "remove_item":
            item_index = int(request.form["item_index"])
            if 0 <= item_index < len(session["cart"]):
                removed_item = session["cart"].pop(item_index)
                session.modified = True
                flash(
                    f"Removed {removed_item['product_name']} from cart.",
                    "warning",
                )
            return redirect(url_for("create_invoice"))

        elif action == "checkout":
            customer_name = request.form["customer_name"].strip()
            if not customer_name:
                flash("Customer name is required for checkout.", "danger")
                return redirect(url_for("create_invoice"))

            if not session.get("cart"):
                flash("Cannot checkout with an empty cart.", "warning")
                return redirect(url_for("create_invoice"))

            grand_total = sum(item["item_total"] for item in session["cart"])

            new_invoice = Invoice(
                customer_name=customer_name,
                grand_total=grand_total,
                items=session["cart"],
            )

            invoice_id = new_invoice.save()
            if invoice_id:
                flash(
                    f"Invoice {invoice_id} created successfully! Total: " f"9{grand_total:.2f}",
                    "success",
                )
                session.pop("cart", None)
                session.modified = True
                return redirect(url_for("invoice_detail", invoice_id=invoice_id))
            else:
                flash(
                    "Failed to create invoice. Please check logs for details "
                    "(e.g., insufficient stock).",
                    "danger",
                )
            return redirect(url_for("create_invoice"))

    grand_total_display = sum(item["item_total"] for item in session.get("cart", []))

    return render_template(
        "create_invoice.html",
        cart_items=session.get("cart", []),
        grand_total=grand_total_display,
        title="Create Invoice",
    )


@app.route("/invoices")
def invoices():
    """Display all past invoices with filtering options."""
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")
    customer_name = request.args.get("customer_name", "").strip()

    all_invoices = Invoice.get_all(
        start_date=start_date,
        end_date=end_date,
        customer_name=customer_name,
    )
    return render_template(
        "invoices.html",
        invoices=all_invoices,
        title="All Invoices",
        start_date=start_date,
        end_date=end_date,
        customer_name=customer_name,
    )


@app.route("/invoice/<int:invoice_id>")
def invoice_detail(invoice_id):
    """Display the details of a specific invoice."""
    invoice = Invoice.get_by_id(invoice_id)
    if not invoice:
        flash("Invoice not found.", "danger")
        return redirect(url_for("invoices"))
    return render_template(
        "invoice_detail.html",
        invoice=invoice,
        title=f"Invoice {invoice_id} Details",
    )


if __name__ == "__main__":
    app.run(debug=True)
