import hmac
import logging
import os
import sqlite3
from flask import Flask, jsonify, request

app = Flask(__name__)
DB_PATH = os.getenv("DB_PATH", "/tmp/invoiceflow.db")
logger = logging.getLogger("invoiceflow.security")


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
    try:
        with connection() as conn:
            rows = conn.execute(
                "SELECT id, customer, amount, note FROM invoices WHERE customer = ?",
                (customer,),
            ).fetchall()
        return jsonify([dict(row) for row in rows])
    except sqlite3.Error:
        logger.exception("database query failed", extra={"event": "invoice_query_failed"})
        return {"error": "request could not be completed"}, 500


@app.get("/admin/export")
def admin_export():
    expected = os.getenv("ADMIN_TOKEN")
    supplied = request.headers.get("X-API-Key", "")
    if not expected or not hmac.compare_digest(supplied, expected):
        logger.warning("admin export denied", extra={"event": "admin_export_denied"})
        return {"error": "unauthorized"}, 401
    with connection() as conn:
        rows = conn.execute("SELECT id, customer, amount, note FROM invoices").fetchall()
    logger.info("admin export completed", extra={"event": "admin_export_completed"})
    return jsonify([dict(row) for row in rows])


initialize_database()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)

