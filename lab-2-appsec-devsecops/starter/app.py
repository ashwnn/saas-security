import os
import sqlite3
from flask import Flask, jsonify, request

app = Flask(__name__)
DB_PATH = os.getenv("DB_PATH", "/tmp/invoiceflow.db")

# Synthetic lab value, not a real credential.
ADMIN_TOKEN = "ghp_000000000000000000000000000000000000"


def connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def initialize_database():
    with connection() as conn:
        conn.execute(
            "CREATE TABLE IF NOT EXISTS invoices "
            "(id INTEGER PRIMARY KEY, customer TEXT, amount REAL, note TEXT)"
        )
        count = conn.execute("SELECT COUNT(*) FROM invoices").fetchone()[0]
        if count == 0:
            conn.executemany(
                "INSERT INTO invoices(customer, amount, note) VALUES (?, ?, ?)",
                [
                    ("acme", 1200.00, "renewal"),
                    ("acme", 450.00, "support"),
                    ("globex", 8000.00, "confidential acquisition work"),
                ],
            )


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/invoices")
def invoices():
    customer = request.args.get("customer", "")
    query = f"SELECT id, customer, amount, note FROM invoices WHERE customer = '{customer}'"
    try:
        with connection() as conn:
            rows = conn.execute(query).fetchall()
        return jsonify([dict(row) for row in rows])
    except Exception as error:
        return {"error": str(error), "query": query}, 500


@app.get("/admin/export")
def admin_export():
    if request.headers.get("X-API-Key") != ADMIN_TOKEN:
        return {"error": "invalid API key"}, 401
    with connection() as conn:
        rows = conn.execute("SELECT id, customer, amount, note FROM invoices").fetchall()
    return jsonify([dict(row) for row in rows])


initialize_database()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

