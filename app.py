from flask import Flask, jsonify, request, render_template, Response
from flask_cors import CORS
from app.db import init_db, get_db
from app.services import (
    create_session, stop_session, list_sessions, dashboard,
    list_products, create_product, update_product, create_sale,
    list_sales, add_expense, list_expenses, list_customers,
    station_config, update_station_rate, seed_database
)
import csv
import io

app = Flask(__name__, template_folder="app/templates", static_folder="app/static")
CORS(app)
app.config["JSON_SORT_KEYS"] = False

with app.app_context():
    init_db()
    seed_database()

@app.get("/")
def index():
    return render_template("index.html")

@app.get("/api/dashboard")
def api_dashboard():
    return jsonify(dashboard())

@app.get("/api/stations")
def api_stations():
    return jsonify(station_config())

@app.patch("/api/stations/<station_id>")
def api_station_rate(station_id):
    data = request.get_json(force=True) or {}
    return jsonify(update_station_rate(station_id, data))

@app.get("/api/sessions")
def api_sessions():
    return jsonify(list_sessions())

@app.post("/api/sessions")
def api_start_session():
    data = request.get_json(force=True) or {}
    try:
        return jsonify(create_session(data)), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

@app.post("/api/sessions/<int:session_id>/stop")
def api_stop_session(session_id):
    data = request.get_json(silent=True) or {}
    try:
        return jsonify(stop_session(session_id, data))
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

@app.get("/api/products")
def api_products():
    return jsonify(list_products())

@app.post("/api/products")
def api_create_product():
    data = request.get_json(force=True) or {}
    try:
        return jsonify(create_product(data)), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

@app.patch("/api/products/<int:product_id>")
def api_update_product(product_id):
    try:
        return jsonify(update_product(product_id, request.get_json(force=True) or {}))
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

@app.get("/api/sales")
def api_sales():
    return jsonify(list_sales())

@app.post("/api/sales")
def api_create_sale():
    try:
        return jsonify(create_sale(request.get_json(force=True) or {})), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

@app.get("/api/customers")
def api_customers():
    return jsonify(list_customers())

@app.get("/api/expenses")
def api_expenses():
    return jsonify(list_expenses())

@app.post("/api/expenses")
def api_create_expense():
    try:
        return jsonify(add_expense(request.get_json(force=True) or {})), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

@app.get("/api/export/transactions.csv")
def export_transactions():
    sessions = list_sessions()
    sales = list_sales()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Type","Date","Customer","Phone","Station","Duration","Amount","Payment"])
    for s in sessions:
        writer.writerow(["SESSION", s["ended_at"] or s["started_at"], s["customer_name"], s["phone"] or "",
                         s["station_id"], s["duration_minutes"], s["total"], s["payment_method"] or ""])
    for sale in sales:
        writer.writerow(["PRODUCT SALE", sale["created_at"], sale["customer_name"] or "", sale["phone"] or "",
                         "POS", "", sale["total"], sale["payment_method"]])
    return Response(output.getvalue(), mimetype="text/csv",
                    headers={"Content-Disposition": "attachment; filename=gamingstation_transactions.csv"})

@app.post("/api/reset-demo")
def reset_demo():
    db = get_db()
    for table in ["sessions","sales","sale_items","expenses","customers","products"]:
        db.execute(f"DELETE FROM {table}")
    db.commit()
    seed_database(force=True)
    return jsonify({"ok": True})

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
