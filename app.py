"""
Affidavit Manager — Flask Backend
CRUD + generación de Affidavit (Work/NoWork) + Invoice.
Soporta PostgreSQL (DATABASE_URL env) y SQLite (local).
"""

import os
from flask import Flask, request, jsonify, send_file, render_template
from datetime import datetime, timezone

from pdf_filler import generate_pdfs

DATABASE_URL = os.environ.get("DATABASE_URL", "")
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

USE_POSTGRES = bool(DATABASE_URL)

if USE_POSTGRES:
    import psycopg2
    import psycopg2.extras
else:
    import sqlite3

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH  = os.path.join(BASE_DIR, "records.db")

app = Flask(__name__)
app.config["JSON_ENSURE_ASCII"] = False


# ─── DB helpers ───────────────────────────────────────────────────────────────

def get_connection():
    if USE_POSTGRES:
        return psycopg2.connect(DATABASE_URL)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def ph():
    return "%s" if USE_POSTGRES else "?"

def phs(cols):
    return ", ".join([ph()] * len(cols))

def fetchall(cur):
    rows = cur.fetchall()
    if USE_POSTGRES:
        cols = [d[0] for d in cur.description]
        return [dict(zip(cols, r)) for r in rows]
    return [dict(r) for r in rows]

def fetchone(cur):
    row = cur.fetchone()
    if not row:
        return None
    if USE_POSTGRES:
        cols = [d[0] for d in cur.description]
        return dict(zip(cols, row))
    return dict(row)

def serialize(rec):
    """Convierte timestamps a string para JSON."""
    if rec:
        for k in ("created_at", "updated_at"):
            if rec.get(k) and not isinstance(rec[k], str):
                rec[k] = rec[k].isoformat()
    return rec


# ─── Schema ───────────────────────────────────────────────────────────────────

SCHEMA = """
CREATE TABLE IF NOT EXISTS records (
    id                   {pk},
    doc_type             TEXT NOT NULL DEFAULT 'work',
    status               TEXT NOT NULL DEFAULT 'pending',

    -- Campos comunes
    omo_number           TEXT,
    county               TEXT,
    building_address     TEXT,
    date_directed        TEXT,

    -- WORK PERFORMED
    work_type            TEXT,
    work_start_date      TEXT,
    work_end_date        TEXT,
    partial_reason       TEXT,
    partial_amount       TEXT,
    interrupted_amount   TEXT,
    prevented_name       TEXT,
    prevented_rel        TEXT,
    prevented_desc       TEXT,

    -- NO WORK PERFORMED
    service_charge       TEXT,
    nowork_reason        TEXT,
    inacc_reason         TEXT,
    attempt_date1        TEXT,
    attempt_date2        TEXT,
    phone_date1          TEXT,
    phone_date2          TEXT,
    arrival_date         TEXT,
    contractor_name      TEXT,
    individual_name      TEXT,
    individual_rel       TEXT,
    individual_desc      TEXT,
    individual_phone     TEXT,

    -- INVOICE
    invoice_number       TEXT,
    invoice_date         TEXT,
    trade                TEXT,
    borough              TEXT,
    work_location_apt    TEXT,
    rc_number            TEXT,
    inv_desc1            TEXT,
    inv_desc2            TEXT,
    inv_desc3            TEXT,
    inv_desc4            TEXT,
    inv_desc5            TEXT,
    inv_desc6            TEXT,
    inv_mat1             TEXT,
    inv_mat2             TEXT,
    inv_mat3             TEXT,
    inv_mat4             TEXT,
    inv_mat5             TEXT,
    inv_mat6             TEXT,
    inv_qty1             TEXT,
    inv_qty2             TEXT,
    inv_qty3             TEXT,
    inv_qty4             TEXT,
    inv_qty5             TEXT,
    inv_qty6             TEXT,
    bid_amount           TEXT,
    total_charge         TEXT,

    -- Notario
    sworn_day            TEXT,
    sworn_month          TEXT,
    sworn_year           TEXT,

    created_at           {ts_default},
    updated_at           {ts_default}
)
"""

SCHEMA_SQLITE  = SCHEMA.format(
    pk="INTEGER PRIMARY KEY AUTOINCREMENT",
    ts_default="TEXT DEFAULT (datetime('now'))"
)
SCHEMA_POSTGRES = SCHEMA.format(
    pk="SERIAL PRIMARY KEY",
    ts_default="TIMESTAMP DEFAULT NOW()"
)

# Migración: columnas nuevas para DBs existentes
MIGRATION_COLS = [
    ("status", "TEXT DEFAULT 'pending'"),
    ("invoice_number", "TEXT"), ("invoice_date", "TEXT"), ("trade", "TEXT"),
    ("borough", "TEXT"), ("work_location_apt", "TEXT"), ("rc_number", "TEXT"),
    ("inv_desc1", "TEXT"), ("inv_desc2", "TEXT"), ("inv_desc3", "TEXT"),
    ("inv_desc4", "TEXT"), ("inv_desc5", "TEXT"), ("inv_desc6", "TEXT"),
    ("inv_mat1", "TEXT"), ("inv_mat2", "TEXT"), ("inv_mat3", "TEXT"),
    ("inv_mat4", "TEXT"), ("inv_mat5", "TEXT"), ("inv_mat6", "TEXT"),
    ("inv_qty1", "TEXT"), ("inv_qty2", "TEXT"), ("inv_qty3", "TEXT"),
    ("inv_qty4", "TEXT"), ("inv_qty5", "TEXT"), ("inv_qty6", "TEXT"),
    ("bid_amount", "TEXT"), ("total_charge", "TEXT"),
]

def init_db():
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(SCHEMA_POSTGRES if USE_POSTGRES else SCHEMA_SQLITE)
        # Agregar columnas nuevas si ya existía la tabla (migración)
        for col, typ in MIGRATION_COLS:
            try:
                cur.execute(f"ALTER TABLE records ADD COLUMN {col} {typ}")
            except Exception:
                pass  # Ya existe
        conn.commit()
    finally:
        conn.close()


COLUMNS = [
    "doc_type", "status", "omo_number", "county", "building_address", "date_directed",
    "work_type", "work_start_date", "work_end_date", "partial_reason",
    "partial_amount", "interrupted_amount", "prevented_name", "prevented_rel",
    "prevented_desc", "service_charge", "nowork_reason", "inacc_reason",
    "attempt_date1", "attempt_date2", "phone_date1", "phone_date2",
    "arrival_date", "contractor_name", "individual_name", "individual_rel",
    "individual_desc", "individual_phone",
    "invoice_number", "invoice_date", "trade", "borough", "work_location_apt",
    "rc_number",
    "inv_desc1", "inv_desc2", "inv_desc3", "inv_desc4", "inv_desc5", "inv_desc6",
    "inv_mat1", "inv_mat2", "inv_mat3", "inv_mat4", "inv_mat5", "inv_mat6",
    "inv_qty1", "inv_qty2", "inv_qty3", "inv_qty4", "inv_qty5", "inv_qty6",
    "bid_amount", "total_charge",
    "sworn_day", "sworn_month", "sworn_year",
]


# ─── Routes ───────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/records", methods=["GET"])
def list_records():
    q = request.args.get("q", "").strip().lower()
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM records ORDER BY id DESC")
        records = [serialize(r) for r in fetchall(cur)]
    finally:
        conn.close()

    if q:
        records = [
            r for r in records
            if q in " ".join(str(v).lower() for v in r.values() if v)
        ]
    return jsonify(records)


@app.route("/api/records", methods=["POST"])
def create_record():
    data = request.get_json(force=True) or {}
    conn = get_connection()
    try:
        cur  = conn.cursor()
        cols = [c for c in COLUMNS if c in data]
        vals = [data[c] for c in cols]

        if USE_POSTGRES:
            cur.execute(
                f"INSERT INTO records ({', '.join(cols)}) VALUES ({phs(cols)}) RETURNING id",
                vals,
            )
            new_id = cur.fetchone()[0]
        else:
            cur.execute(f"INSERT INTO records ({', '.join(cols)}) VALUES ({phs(cols)})", vals)
            new_id = cur.lastrowid

        conn.commit()
        cur.execute(f"SELECT * FROM records WHERE id = {ph()}", (new_id,))
        row = serialize(fetchone(cur))
    finally:
        conn.close()
    return jsonify(row), 201


@app.route("/api/records/<int:rec_id>", methods=["GET"])
def get_record(rec_id):
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(f"SELECT * FROM records WHERE id = {ph()}", (rec_id,))
        row = serialize(fetchone(cur))
    finally:
        conn.close()
    return (jsonify(row) if row else jsonify({"error": "Not found"})), (200 if row else 404)


@app.route("/api/records/<int:rec_id>", methods=["PUT"])
def update_record(rec_id):
    data = request.get_json(force=True) or {}
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(f"SELECT id FROM records WHERE id = {ph()}", (rec_id,))
        if not cur.fetchone():
            return jsonify({"error": "Not found"}), 404

        updates = {c: data[c] for c in COLUMNS if c in data}
        updates["updated_at"] = datetime.now(timezone.utc).isoformat()
        set_clause = ", ".join(f"{k} = {ph()}" for k in updates)
        vals = list(updates.values()) + [rec_id]

        cur.execute(f"UPDATE records SET {set_clause} WHERE id = {ph()}", vals)
        conn.commit()
        cur.execute(f"SELECT * FROM records WHERE id = {ph()}", (rec_id,))
        row = serialize(fetchone(cur))
    finally:
        conn.close()
    return jsonify(row)


@app.route("/api/records/<int:rec_id>", methods=["DELETE"])
def delete_record(rec_id):
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(f"DELETE FROM records WHERE id = {ph()}", (rec_id,))
        conn.commit()
    finally:
        conn.close()
    return jsonify({"ok": True})


@app.route("/api/records/<int:rec_id>/status", methods=["PATCH"])
def update_status(rec_id):
    """
    Transitions de estado del servicio.
    Allowed: pending → work_performed | no_work_performed → submitted → paid
    """
    data   = request.get_json(force=True) or {}
    new_st = data.get("status", "")
    valid  = {"pending", "work_performed", "no_work_performed", "submitted", "paid"}
    if new_st not in valid:
        return jsonify({"error": f"Invalid status. Must be one of: {', '.join(valid)}"}), 400

    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(f"SELECT id FROM records WHERE id = {ph()}", (rec_id,))
        if not cur.fetchone():
            return jsonify({"error": "Not found"}), 404
        cur.execute(
            f"UPDATE records SET status = {ph()}, updated_at = {ph()} WHERE id = {ph()}",
            (new_st, datetime.now(timezone.utc).isoformat(), rec_id),
        )
        conn.commit()
        cur.execute(f"SELECT * FROM records WHERE id = {ph()}", (rec_id,))
        row = serialize(fetchone(cur))
    finally:
        conn.close()
    return jsonify(row)


@app.route("/api/records/<int:rec_id>/pdf/<doc>")
def download_pdf(rec_id, doc):
    """doc = 'affidavit' | 'invoice' | 'zip'"""
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(f"SELECT * FROM records WHERE id = {ph()}", (rec_id,))
        row = fetchone(cur)
    finally:
        conn.close()

    if not row:
        return jsonify({"error": "Not found"}), 404

    paths = generate_pdfs(row)
    path  = paths.get(doc)
    if not path or not os.path.exists(path):
        return jsonify({"error": "Doc not found"}), 404

    mime = "application/zip" if doc == "zip" else "application/pdf"
    return send_file(path, as_attachment=True,
                     download_name=os.path.basename(path), mimetype=mime)


# ─── Inicio ───────────────────────────────────────────────────────────────────

with app.app_context():
    init_db()

if __name__ == "__main__":
    print("=" * 50)
    print("  Affidavit Manager → http://localhost:8080")
    print("=" * 50)
    app.run(debug=True, port=8080)
