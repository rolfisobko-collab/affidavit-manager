"""
Affidavit Manager — Flask Backend
CRUD completo + generación de PDFs sobre los templates originales.

Base de datos:
  - Producción (Render): PostgreSQL via DATABASE_URL env var
  - Local:               SQLite (records.db)
"""

import os
import json
from flask import Flask, request, jsonify, send_file, render_template
from datetime import datetime, timezone

from pdf_filler import generate_pdf

# ─── Configuración de base de datos ───────────────────────────────────────────

DATABASE_URL = os.environ.get("DATABASE_URL", "")

# Render a veces devuelve "postgres://..." que psycopg2 no acepta — fix:
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


# ─── Abstracción de conexión ──────────────────────────────────────────────────

def get_connection():
    """Devuelve una conexión a PostgreSQL o SQLite según el entorno."""
    if USE_POSTGRES:
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    else:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn


def placeholder(n=1):
    """Placeholder de parámetro correcto según el driver."""
    return "%s" if USE_POSTGRES else "?"


def placeholders(cols):
    """Lista de placeholders para una lista de columnas."""
    p = placeholder()
    return ", ".join([p] * len(cols))


def row_to_dict(row):
    """Convierte una fila de cualquier driver a dict."""
    if row is None:
        return None
    if USE_POSTGRES:
        return dict(row)
    return dict(row)


def fetchall(cursor):
    rows = cursor.fetchall()
    if USE_POSTGRES:
        cols = [d[0] for d in cursor.description]
        return [dict(zip(cols, r)) for r in rows]
    return [dict(r) for r in rows]


def fetchone(cursor):
    row = cursor.fetchone()
    if row is None:
        return None
    if USE_POSTGRES:
        cols = [d[0] for d in cursor.description]
        return dict(zip(cols, row))
    return dict(row)


# ─── Schema ───────────────────────────────────────────────────────────────────

SCHEMA_SQLITE = """
CREATE TABLE IF NOT EXISTS records (
    id                   INTEGER PRIMARY KEY AUTOINCREMENT,
    doc_type             TEXT    NOT NULL DEFAULT 'work',
    omo_number           TEXT,
    county               TEXT,
    building_address     TEXT,
    date_directed        TEXT,
    work_type            TEXT,
    work_start_date      TEXT,
    work_end_date        TEXT,
    partial_reason       TEXT,
    partial_amount       TEXT,
    interrupted_amount   TEXT,
    prevented_name       TEXT,
    prevented_rel        TEXT,
    prevented_desc       TEXT,
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
    sworn_day            TEXT,
    sworn_month          TEXT,
    sworn_year           TEXT,
    created_at           TEXT DEFAULT (datetime('now')),
    updated_at           TEXT DEFAULT (datetime('now'))
)
"""

SCHEMA_POSTGRES = """
CREATE TABLE IF NOT EXISTS records (
    id                   SERIAL PRIMARY KEY,
    doc_type             TEXT    NOT NULL DEFAULT 'work',
    omo_number           TEXT,
    county               TEXT,
    building_address     TEXT,
    date_directed        TEXT,
    work_type            TEXT,
    work_start_date      TEXT,
    work_end_date        TEXT,
    partial_reason       TEXT,
    partial_amount       TEXT,
    interrupted_amount   TEXT,
    prevented_name       TEXT,
    prevented_rel        TEXT,
    prevented_desc       TEXT,
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
    sworn_day            TEXT,
    sworn_month          TEXT,
    sworn_year           TEXT,
    created_at           TIMESTAMP DEFAULT NOW(),
    updated_at           TIMESTAMP DEFAULT NOW()
)
"""


def init_db():
    conn = get_connection()
    try:
        cur = conn.cursor()
        schema = SCHEMA_POSTGRES if USE_POSTGRES else SCHEMA_SQLITE
        cur.execute(schema)
        conn.commit()
    finally:
        conn.close()


COLUMNS = [
    "doc_type", "omo_number", "county", "building_address", "date_directed",
    "work_type", "work_start_date", "work_end_date", "partial_reason",
    "partial_amount", "interrupted_amount", "prevented_name", "prevented_rel",
    "prevented_desc", "service_charge", "nowork_reason", "inacc_reason",
    "attempt_date1", "attempt_date2", "phone_date1", "phone_date2",
    "arrival_date", "contractor_name", "individual_name", "individual_rel",
    "individual_desc", "individual_phone", "sworn_day", "sworn_month", "sworn_year",
]


# ─── Rutas API ────────────────────────────────────────────────────────────────

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
        records = fetchall(cur)
    finally:
        conn.close()

    if q:
        filtered = []
        for rec in records:
            haystack = " ".join(
                str(v).lower() for v in rec.values() if v is not None
            )
            if q in haystack:
                filtered.append(rec)
        records = filtered

    # Convertir timestamps a string para JSON
    for rec in records:
        for k in ("created_at", "updated_at"):
            if rec.get(k) and not isinstance(rec[k], str):
                rec[k] = rec[k].isoformat()

    return jsonify(records)


@app.route("/api/records", methods=["POST"])
def create_record():
    data = request.get_json(force=True) or {}
    conn = get_connection()
    try:
        cur  = conn.cursor()
        cols = [c for c in COLUMNS if c in data]
        vals = [data[c] for c in cols]
        ph   = placeholders(cols)
        col_names = ", ".join(cols)

        if USE_POSTGRES:
            cur.execute(
                f"INSERT INTO records ({col_names}) VALUES ({ph}) RETURNING id",
                vals,
            )
            new_id = cur.fetchone()[0]
        else:
            cur.execute(f"INSERT INTO records ({col_names}) VALUES ({ph})", vals)
            new_id = cur.lastrowid

        conn.commit()
        cur.execute(f"SELECT * FROM records WHERE id = {placeholder()}", (new_id,))
        row = fetchone(cur)
    finally:
        conn.close()

    if row:
        for k in ("created_at", "updated_at"):
            if row.get(k) and not isinstance(row[k], str):
                row[k] = row[k].isoformat()

    return jsonify(row), 201


@app.route("/api/records/<int:rec_id>", methods=["GET"])
def get_record(rec_id):
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(f"SELECT * FROM records WHERE id = {placeholder()}", (rec_id,))
        row = fetchone(cur)
    finally:
        conn.close()

    if not row:
        return jsonify({"error": "Not found"}), 404

    for k in ("created_at", "updated_at"):
        if row.get(k) and not isinstance(row[k], str):
            row[k] = row[k].isoformat()

    return jsonify(row)


@app.route("/api/records/<int:rec_id>", methods=["PUT"])
def update_record(rec_id):
    data = request.get_json(force=True) or {}
    conn = get_connection()
    try:
        cur = conn.cursor()

        cur.execute(f"SELECT id FROM records WHERE id = {placeholder()}", (rec_id,))
        if not cur.fetchone():
            return jsonify({"error": "Not found"}), 404

        updates = {c: data[c] for c in COLUMNS if c in data}
        updates["updated_at"] = datetime.now(timezone.utc).isoformat()

        p = placeholder()
        set_clause = ", ".join(f"{k} = {p}" for k in updates)
        vals = list(updates.values()) + [rec_id]

        cur.execute(f"UPDATE records SET {set_clause} WHERE id = {p}", vals)
        conn.commit()

        cur.execute(f"SELECT * FROM records WHERE id = {placeholder()}", (rec_id,))
        row = fetchone(cur)
    finally:
        conn.close()

    if row:
        for k in ("created_at", "updated_at"):
            if row.get(k) and not isinstance(row[k], str):
                row[k] = row[k].isoformat()

    return jsonify(row)


@app.route("/api/records/<int:rec_id>", methods=["DELETE"])
def delete_record(rec_id):
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(f"DELETE FROM records WHERE id = {placeholder()}", (rec_id,))
        conn.commit()
    finally:
        conn.close()
    return jsonify({"ok": True})


@app.route("/api/records/<int:rec_id>/pdf")
def download_pdf(rec_id):
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(f"SELECT * FROM records WHERE id = {placeholder()}", (rec_id,))
        row = fetchone(cur)
    finally:
        conn.close()

    if not row:
        return jsonify({"error": "Not found"}), 404

    output_path = generate_pdf(row)
    return send_file(
        output_path,
        as_attachment=True,
        download_name=os.path.basename(output_path),
        mimetype="application/pdf",
    )


# ─── Inicio ───────────────────────────────────────────────────────────────────

with app.app_context():
    init_db()

if __name__ == "__main__":
    print("=" * 50)
    print("  Affidavit Manager en http://localhost:8080")
    print("=" * 50)
    app.run(debug=True, port=8080)
