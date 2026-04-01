"""
Affidavit Manager — Flask Backend
CRUD + Auth (admin/worker/notary) + PDF generation + Media upload + Batch download.
Soporta PostgreSQL (DATABASE_URL env) y SQLite (local).
"""

import os
import re
import uuid
import zipfile
from datetime import datetime, timezone
from functools import wraps

from flask import (Flask, request, jsonify, send_file,
                   render_template, session, redirect, url_for)
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

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

BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
DB_PATH     = os.path.join(BASE_DIR, "records.db")
MEDIA_DIR   = os.path.join(BASE_DIR, "media")
OUTPUT_DIR  = os.path.join(BASE_DIR, "output")

ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "gif", "webp", "mp4", "mov", "avi", "pdf"}

app = Flask(__name__)
app.config["JSON_ENSURE_ASCII"] = False
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "lbj-hpd-secret-2026")
app.config["MAX_CONTENT_LENGTH"] = 200 * 1024 * 1024  # 200 MB


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
    if rec:
        for k in ("created_at", "updated_at"):
            if rec.get(k) and not isinstance(rec[k], str):
                rec[k] = rec[k].isoformat()
    return rec


# ─── Schema ───────────────────────────────────────────────────────────────────

SCHEMA_USERS = """
CREATE TABLE IF NOT EXISTS users (
    id        {pk},
    username  TEXT NOT NULL UNIQUE,
    password  TEXT NOT NULL,
    role      TEXT NOT NULL DEFAULT 'worker',
    full_name TEXT,
    active    INTEGER NOT NULL DEFAULT 1,
    created_at {ts_default}
)
"""

SCHEMA_RECORDS = """
CREATE TABLE IF NOT EXISTS records (
    id                   {pk},
    doc_type             TEXT NOT NULL DEFAULT 'work',
    status               TEXT NOT NULL DEFAULT 'pending',

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

    sworn_day            TEXT,
    sworn_month          TEXT,
    sworn_year           TEXT,

    batch                TEXT,

    created_at           {ts_default},
    updated_at           {ts_default}
)
"""

SCHEMA_MEDIA = """
CREATE TABLE IF NOT EXISTS media (
    id         {pk},
    record_id  INTEGER NOT NULL,
    filename   TEXT NOT NULL,
    orig_name  TEXT,
    mime_type  TEXT,
    uploaded_by TEXT,
    created_at {ts_default}
)
"""

def _fmt(schema):
    return (
        schema.replace("{pk}", "SERIAL PRIMARY KEY").replace("{ts_default}", "TIMESTAMP DEFAULT NOW()")
        if USE_POSTGRES else
        schema.replace("{pk}", "INTEGER PRIMARY KEY AUTOINCREMENT").replace("{ts_default}", "TEXT DEFAULT (datetime('now'))")
    )

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
    ("bid_amount", "TEXT"), ("total_charge", "TEXT"), ("batch", "TEXT"),
    ("work_contractor_name", "TEXT"), ("arrival_date_4", "TEXT"),
    ("signer_name", "TEXT"),
]

def init_db():
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(_fmt(SCHEMA_USERS))
        cur.execute(_fmt(SCHEMA_RECORDS))
        cur.execute(_fmt(SCHEMA_MEDIA))
        for col, typ in MIGRATION_COLS:
            try:
                cur.execute(f"ALTER TABLE records ADD COLUMN {col} {typ}")
            except Exception:
                pass
        # Admin por defecto
        try:
            cur.execute(
                f"INSERT INTO users (username, password, role, full_name) VALUES ({ph()},{ph()},{ph()},{ph()})",
                ("admin", generate_password_hash("admin123"), "admin", "Administrator")
            )
        except Exception:
            pass
        conn.commit()
    finally:
        conn.close()
    os.makedirs(MEDIA_DIR, exist_ok=True)
    os.makedirs(OUTPUT_DIR, exist_ok=True)


COLUMNS = [
    "doc_type", "status", "omo_number", "county", "building_address", "date_directed",
    "work_type", "work_start_date", "work_end_date", "partial_reason",
    "partial_amount", "interrupted_amount", "prevented_name", "prevented_rel",
    "prevented_desc", "service_charge", "nowork_reason", "inacc_reason",
    "attempt_date1", "attempt_date2", "phone_date1", "phone_date2",
    "arrival_date", "arrival_date_4", "contractor_name", "work_contractor_name",
    "signer_name",
    "individual_name", "individual_rel", "individual_desc", "individual_phone",
    "invoice_number", "invoice_date", "trade", "borough", "work_location_apt",
    "rc_number",
    "inv_desc1", "inv_desc2", "inv_desc3", "inv_desc4", "inv_desc5", "inv_desc6",
    "inv_mat1", "inv_mat2", "inv_mat3", "inv_mat4", "inv_mat5", "inv_mat6",
    "inv_qty1", "inv_qty2", "inv_qty3", "inv_qty4", "inv_qty5", "inv_qty6",
    "bid_amount", "total_charge",
    "sworn_day", "sworn_month", "sworn_year", "batch",
]

# Campos que worker NO puede ver/editar
PRICE_FIELDS = {
    "partial_amount", "interrupted_amount", "service_charge",
    "bid_amount", "total_charge",
    "inv_mat1","inv_mat2","inv_mat3","inv_mat4","inv_mat5","inv_mat6",
    "inv_qty1","inv_qty2","inv_qty3","inv_qty4","inv_qty5","inv_qty6",
    "invoice_number","invoice_date","rc_number",
    "inv_desc1","inv_desc2","inv_desc3","inv_desc4","inv_desc5","inv_desc6",
}


# ─── Auth helpers ─────────────────────────────────────────────────────────────

def current_user():
    uid = session.get("user_id")
    if not uid:
        return None
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(f"SELECT * FROM users WHERE id = {ph()}", (uid,))
        return fetchone(cur)
    finally:
        conn.close()

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("user_id"):
            if request.is_json:
                return jsonify({"error": "Unauthorized"}), 401
            return redirect(url_for("login_page"))
        return f(*args, **kwargs)
    return decorated

def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            user = current_user()
            if not user or user["role"] not in roles:
                if request.is_json:
                    return jsonify({"error": "Forbidden"}), 403
                return redirect(url_for("login_page"))
            return f(*args, **kwargs)
        return decorated
    return decorator

def strip_prices(record):
    """Elimina campos de precio para rol worker."""
    return {k: v for k, v in record.items() if k not in PRICE_FIELDS}


# ─── Auth routes ──────────────────────────────────────────────────────────────

@app.route("/login")
def login_page():
    if session.get("user_id"):
        return redirect(url_for("index"))
    return render_template("login.html")

@app.route("/api/auth/login", methods=["POST"])
def api_login():
    data = request.get_json(force=True) or {}
    username = (data.get("username") or "").strip().lower()
    password = data.get("password") or ""
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(f"SELECT * FROM users WHERE username = {ph()} AND active = 1", (username,))
        user = fetchone(cur)
    finally:
        conn.close()
    if not user or not check_password_hash(user["password"], password):
        return jsonify({"error": "Invalid credentials"}), 401
    session["user_id"] = user["id"]
    session["role"]    = user["role"]
    return jsonify({"ok": True, "role": user["role"], "full_name": user.get("full_name", "")})

@app.route("/api/auth/logout", methods=["POST"])
def api_logout():
    session.clear()
    return jsonify({"ok": True})

@app.route("/api/auth/me")
def api_me():
    user = current_user()
    if not user:
        return jsonify({"error": "Not logged in"}), 401
    return jsonify({"id": user["id"], "username": user["username"],
                    "role": user["role"], "full_name": user.get("full_name", "")})


# ─── User management (admin only) ─────────────────────────────────────────────

@app.route("/api/users", methods=["GET"])
@login_required
@role_required("admin")
def list_users():
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT id, username, role, full_name, active, created_at FROM users ORDER BY id")
        users = fetchall(cur)
    finally:
        conn.close()
    for u in users:
        if u.get("created_at") and not isinstance(u["created_at"], str):
            u["created_at"] = u["created_at"].isoformat()
    return jsonify(users)

@app.route("/api/users", methods=["POST"])
@login_required
@role_required("admin")
def create_user():
    data = request.get_json(force=True) or {}
    username  = (data.get("username") or "").strip().lower()
    password  = data.get("password") or ""
    role      = data.get("role", "worker")
    full_name = data.get("full_name", "")
    if not username or not password:
        return jsonify({"error": "username and password required"}), 400
    if role not in ("admin", "worker", "notary"):
        return jsonify({"error": "Invalid role"}), 400
    conn = get_connection()
    try:
        cur = conn.cursor()
        if USE_POSTGRES:
            cur.execute(
                f"INSERT INTO users (username,password,role,full_name) VALUES ({ph()},{ph()},{ph()},{ph()}) RETURNING id",
                (username, generate_password_hash(password), role, full_name)
            )
            new_id = cur.fetchone()[0]
        else:
            cur.execute(
                f"INSERT INTO users (username,password,role,full_name) VALUES ({ph()},{ph()},{ph()},{ph()})",
                (username, generate_password_hash(password), role, full_name)
            )
            new_id = cur.lastrowid
        conn.commit()
        cur.execute(f"SELECT id,username,role,full_name,active FROM users WHERE id={ph()}", (new_id,))
        row = fetchone(cur)
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    finally:
        conn.close()
    return jsonify(row), 201

@app.route("/api/users/<int:uid>", methods=["PUT"])
@login_required
@role_required("admin")
def update_user(uid):
    data = request.get_json(force=True) or {}
    conn = get_connection()
    try:
        cur = conn.cursor()
        updates = {}
        if "full_name" in data: updates["full_name"] = data["full_name"]
        if "role"      in data and data["role"] in ("admin","worker","notary"): updates["role"] = data["role"]
        if "active"    in data: updates["active"] = 1 if data["active"] else 0
        if "password"  in data and data["password"]: updates["password"] = generate_password_hash(data["password"])
        if not updates:
            return jsonify({"error": "Nothing to update"}), 400
        set_clause = ", ".join(f"{k}={ph()}" for k in updates)
        cur.execute(f"UPDATE users SET {set_clause} WHERE id={ph()}", list(updates.values()) + [uid])
        conn.commit()
        cur.execute(f"SELECT id,username,role,full_name,active FROM users WHERE id={ph()}", (uid,))
        row = fetchone(cur)
    finally:
        conn.close()
    return jsonify(row)

@app.route("/api/users/<int:uid>", methods=["DELETE"])
@login_required
@role_required("admin")
def delete_user(uid):
    if uid == session.get("user_id"):
        return jsonify({"error": "Cannot delete yourself"}), 400
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(f"DELETE FROM users WHERE id={ph()}", (uid,))
        conn.commit()
    finally:
        conn.close()
    return jsonify({"ok": True})


# ─── Records routes ───────────────────────────────────────────────────────────

@app.route("/")
@login_required
def index():
    return render_template("index.html")

@app.route("/api/records", methods=["GET"])
@login_required
def list_records():
    q    = request.args.get("q", "").strip().lower()
    role = session.get("role", "worker")
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM records ORDER BY id DESC")
        records = [serialize(r) for r in fetchall(cur)]
    finally:
        conn.close()
    if q:
        records = [r for r in records if q in " ".join(str(v).lower() for v in r.values() if v)]
    if role == "worker":
        records = [strip_prices(r) for r in records]
    return jsonify(records)

@app.route("/api/records", methods=["POST"])
@login_required
@role_required("admin", "worker")
def create_record():
    data = request.get_json(force=True) or {}
    role = session.get("role", "worker")
    if role == "worker":
        for f in PRICE_FIELDS:
            data.pop(f, None)
    conn = get_connection()
    try:
        cur  = conn.cursor()
        cols = [c for c in COLUMNS if c in data]
        vals = [data[c] for c in cols]
        if USE_POSTGRES:
            cur.execute(f"INSERT INTO records ({', '.join(cols)}) VALUES ({phs(cols)}) RETURNING id", vals)
            new_id = cur.fetchone()[0]
        else:
            cur.execute(f"INSERT INTO records ({', '.join(cols)}) VALUES ({phs(cols)})", vals)
            new_id = cur.lastrowid
        conn.commit()
        cur.execute(f"SELECT * FROM records WHERE id={ph()}", (new_id,))
        row = serialize(fetchone(cur))
    finally:
        conn.close()
    if role == "worker":
        row = strip_prices(row)
    return jsonify(row), 201

@app.route("/api/records/<int:rec_id>", methods=["GET"])
@login_required
def get_record(rec_id):
    role = session.get("role", "worker")
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(f"SELECT * FROM records WHERE id={ph()}", (rec_id,))
        row = serialize(fetchone(cur))
    finally:
        conn.close()
    if not row:
        return jsonify({"error": "Not found"}), 404
    if role == "worker":
        row = strip_prices(row)
    return jsonify(row)

@app.route("/api/records/<int:rec_id>", methods=["PUT"])
@login_required
@role_required("admin", "worker")
def update_record(rec_id):
    data = request.get_json(force=True) or {}
    role = session.get("role", "worker")
    if role == "worker":
        for f in PRICE_FIELDS:
            data.pop(f, None)
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(f"SELECT id FROM records WHERE id={ph()}", (rec_id,))
        if not cur.fetchone():
            return jsonify({"error": "Not found"}), 404
        updates = {c: data[c] for c in COLUMNS if c in data}
        updates["updated_at"] = datetime.now(timezone.utc).isoformat()
        set_clause = ", ".join(f"{k}={ph()}" for k in updates)
        cur.execute(f"UPDATE records SET {set_clause} WHERE id={ph()}", list(updates.values()) + [rec_id])
        conn.commit()
        cur.execute(f"SELECT * FROM records WHERE id={ph()}", (rec_id,))
        row = serialize(fetchone(cur))
    finally:
        conn.close()
    if role == "worker":
        row = strip_prices(row)
    return jsonify(row)

@app.route("/api/records/<int:rec_id>", methods=["DELETE"])
@login_required
@role_required("admin")
def delete_record(rec_id):
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(f"DELETE FROM records WHERE id={ph()}", (rec_id,))
        cur.execute(f"DELETE FROM media WHERE record_id={ph()}", (rec_id,))
        conn.commit()
    finally:
        conn.close()
    return jsonify({"ok": True})

@app.route("/api/records/<int:rec_id>/status", methods=["PATCH"])
@login_required
@role_required("admin", "worker")
def update_status(rec_id):
    data   = request.get_json(force=True) or {}
    new_st = data.get("status", "")
    valid  = {"pending", "work_performed", "no_work_performed", "submitted", "paid"}
    if new_st not in valid:
        return jsonify({"error": f"Invalid status"}), 400
    # Worker solo puede marcar work_performed / no_work_performed
    if session.get("role") == "worker" and new_st not in ("work_performed", "no_work_performed"):
        return jsonify({"error": "Forbidden"}), 403
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(f"SELECT id FROM records WHERE id={ph()}", (rec_id,))
        if not cur.fetchone():
            return jsonify({"error": "Not found"}), 404
        cur.execute(
            f"UPDATE records SET status={ph()}, updated_at={ph()} WHERE id={ph()}",
            (new_st, datetime.now(timezone.utc).isoformat(), rec_id),
        )
        conn.commit()
        cur.execute(f"SELECT * FROM records WHERE id={ph()}", (rec_id,))
        row = serialize(fetchone(cur))
    finally:
        conn.close()
    return jsonify(row)

@app.route("/api/records/<int:rec_id>/pdf/<doc>")
@login_required
def download_pdf(rec_id, doc):
    """doc = 'affidavit' | 'invoice' | 'zip'"""
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(f"SELECT * FROM records WHERE id={ph()}", (rec_id,))
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
    return send_file(path, as_attachment=True, download_name=os.path.basename(path), mimetype=mime)


# ─── Media upload/download ────────────────────────────────────────────────────

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/api/records/<int:rec_id>/media", methods=["GET"])
@login_required
def list_media(rec_id):
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(f"SELECT * FROM media WHERE record_id={ph()} ORDER BY id", (rec_id,))
        rows = fetchall(cur)
    finally:
        conn.close()
    for r in rows:
        if r.get("created_at") and not isinstance(r["created_at"], str):
            r["created_at"] = r["created_at"].isoformat()
    return jsonify(rows)

@app.route("/api/records/<int:rec_id>/media", methods=["POST"])
@login_required
@role_required("admin", "worker")
def upload_media(rec_id):
    if "file" not in request.files:
        return jsonify({"error": "No file"}), 400
    file = request.files["file"]
    if not file.filename or not allowed_file(file.filename):
        return jsonify({"error": "File type not allowed"}), 400
    ext      = file.filename.rsplit(".", 1)[1].lower()
    unique   = f"{rec_id}_{uuid.uuid4().hex}.{ext}"
    rec_dir  = os.path.join(MEDIA_DIR, str(rec_id))
    os.makedirs(rec_dir, exist_ok=True)
    file.save(os.path.join(rec_dir, unique))
    conn = get_connection()
    try:
        cur = conn.cursor()
        if USE_POSTGRES:
            cur.execute(
                f"INSERT INTO media (record_id,filename,orig_name,mime_type,uploaded_by) VALUES ({ph()},{ph()},{ph()},{ph()},{ph()}) RETURNING id",
                (rec_id, unique, secure_filename(file.filename), file.content_type, str(session.get("user_id")))
            )
            mid = cur.fetchone()[0]
        else:
            cur.execute(
                f"INSERT INTO media (record_id,filename,orig_name,mime_type,uploaded_by) VALUES ({ph()},{ph()},{ph()},{ph()},{ph()})",
                (rec_id, unique, secure_filename(file.filename), file.content_type, str(session.get("user_id")))
            )
            mid = cur.lastrowid
        conn.commit()
        cur.execute(f"SELECT * FROM media WHERE id={ph()}", (mid,))
        row = fetchone(cur)
    finally:
        conn.close()
    if row.get("created_at") and not isinstance(row["created_at"], str):
        row["created_at"] = row["created_at"].isoformat()
    return jsonify(row), 201

@app.route("/api/media/<int:media_id>", methods=["DELETE"])
@login_required
@role_required("admin")
def delete_media(media_id):
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(f"SELECT * FROM media WHERE id={ph()}", (media_id,))
        m = fetchone(cur)
        if m:
            path = os.path.join(MEDIA_DIR, str(m["record_id"]), m["filename"])
            if os.path.exists(path):
                os.remove(path)
            cur.execute(f"DELETE FROM media WHERE id={ph()}", (media_id,))
            conn.commit()
    finally:
        conn.close()
    return jsonify({"ok": True})

@app.route("/media/<int:rec_id>/<filename>")
@login_required
def serve_media(rec_id, filename):
    path = os.path.join(MEDIA_DIR, str(rec_id), secure_filename(filename))
    if not os.path.exists(path):
        return jsonify({"error": "Not found"}), 404
    return send_file(path)


# ─── Batch download ───────────────────────────────────────────────────────────

@app.route("/api/batch/download", methods=["POST"])
@login_required
def batch_download():
    """
    Body: { "batch": "Batch 14" }  o  { "ids": [1,2,3] }
    Genera un ZIP con subcarpetas por OMO: Batch14/EQ20025/Affidavit+Invoice
    """
    data     = request.get_json(force=True) or {}
    batch_name = data.get("batch", "").strip()
    ids        = data.get("ids", [])

    conn = get_connection()
    try:
        cur = conn.cursor()
        if batch_name:
            cur.execute(f"SELECT * FROM records WHERE batch={ph()}", (batch_name,))
        elif ids:
            placeholders = ",".join([ph()] * len(ids))
            cur.execute(f"SELECT * FROM records WHERE id IN ({placeholders})", ids)
        else:
            cur.execute("SELECT * FROM records")
        records = fetchall(cur)
    finally:
        conn.close()

    if not records:
        return jsonify({"error": "No records found"}), 404

    safe_batch = secure_filename(batch_name or "All_Records")
    zip_path   = os.path.join(OUTPUT_DIR, f"{safe_batch}_{uuid.uuid4().hex[:6]}.zip")

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for rec in records:
            omo = (rec.get("omo_number") or f"ID{rec['id']}").replace("/","_").replace(" ","_")
            folder = f"{safe_batch}/{omo}/"
            try:
                paths = generate_pdfs(rec)
                zf.write(paths["affidavit"], folder + os.path.basename(paths["affidavit"]))
                zf.write(paths["invoice"],   folder + os.path.basename(paths["invoice"]))
            except Exception:
                pass
            # Adjuntar media
            rec_dir = os.path.join(MEDIA_DIR, str(rec["id"]))
            if os.path.isdir(rec_dir):
                for fname in os.listdir(rec_dir):
                    fpath = os.path.join(rec_dir, fname)
                    if os.path.isfile(fpath):
                        zf.write(fpath, folder + "media/" + fname)

    return send_file(zip_path, as_attachment=True,
                     download_name=f"{safe_batch}.zip", mimetype="application/zip")

@app.route("/api/batches", methods=["GET"])
@login_required
def list_batches():
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT DISTINCT batch FROM records WHERE batch IS NOT NULL AND batch != '' ORDER BY batch")
        rows = [r["batch"] for r in fetchall(cur)]
    finally:
        conn.close()
    return jsonify(rows)


# ─── HPD OMO PDF Parser ───────────────────────────────────────────────────────

BOROUGH_TO_COUNTY = {
    "manhattan": "New York", "bronx": "Bronx",
    "brooklyn": "Kings",    "queens": "Queens",
    "staten island": "Richmond",
}

def _clean(s):
    return " ".join(s.split()) if s else ""

def parse_hpd_omo_pdf(file_bytes):
    """
    Extrae campos del PDF de HPD (OPM-201) usando PyMuPDF + regex.
    En este formato el valor suele estar en la línea ANTERIOR a la etiqueta.
    """
    import fitz
    doc  = fitz.open(stream=file_bytes, filetype="pdf")
    text = "\n".join(page.get_text() for page in doc)
    doc.close()

    lines = [l.strip() for l in text.split("\n")]
    result = {}

    def prev_val(label_re, offset=1):
        """Devuelve el valor N líneas antes de una etiqueta."""
        for i, l in enumerate(lines):
            if re.match(label_re, l, re.I) and i >= offset:
                v = lines[i - offset].strip()
                if v:
                    return v
        return None

    def next_val(label_re):
        """Devuelve el valor en la línea inmediatamente siguiente a una etiqueta."""
        for i, l in enumerate(lines):
            if re.match(label_re, l, re.I) and i + 1 < len(lines):
                v = lines[i + 1].strip()
                if v:
                    return v
        return None

    def inline_val(label_re):
        """Devuelve el valor inline después de los dos puntos en la misma línea."""
        for l in lines:
            m = re.match(label_re + r'[:\s]+(.+)', l, re.I)
            if m:
                return m.group(1).strip()
        return None

    # ── OMO Number ──
    # Formato: EQ20453 está 2 líneas antes de "OMO #:"
    #   56: 'EQ20453'
    #   57: 'OMO #:'
    v = prev_val(r'OMO\s*#\s*:?$', offset=1)
    if v and not re.match(r'^[A-Z]{1,3}\d{4,6}$', v):
        v = None
    if not v:
        m = re.search(r'OMO\s*[#Nn][o.]?\s*:?\s*([A-Z]{1,3}\d{4,6})', text, re.I)
        v = m.group(1).upper() if m else None
    if not v:
        m = re.search(r'\b(EQ\d{4,6}|EM\d{4,6}|HP\d{4,6})\b', text)
        v = m.group(1).upper() if m else None
    if v and re.match(r'^[A-Z]{1,3}\d{4,6}$', v):
        result["omo_number"] = v

    # ── Building address + Borough ──
    # Estructura en el PDF:
    #   58: '227 WEST 15 STREET Apt. 1'   ← dirección (2 antes de "Building Address:")
    #   59: 'Manhattan'                    ← borough (1 antes de "Building Address:")
    #   60: 'Building Address:'
    addr_v  = prev_val(r'Building\s+Address\s*:?$', offset=2)
    boro_v  = prev_val(r'Building\s+Address\s*:?$', offset=1)

    if not addr_v:
        addr_v = inline_val(r'Bldg\s+Address')
    if addr_v:
        apt_m = re.match(r'(.+?)\s+Apt[.:]?\s*(.+)', addr_v, re.I)
        if apt_m:
            result["building_address"] = _clean(apt_m.group(1))
            result["work_location_apt"] = _clean(apt_m.group(2))
        else:
            result["building_address"] = _clean(addr_v)

    if boro_v and re.match(r'^[A-Za-z ]+$', boro_v) and len(boro_v) < 30:
        boro = _clean(boro_v).rstrip(",").title()
        result["borough"] = boro
        key = boro.lower().strip()
        if key in BOROUGH_TO_COUNTY:
            result["county"] = BOROUGH_TO_COUNTY[key]

    if not boro_v:
        v = inline_val(r'Boro(?:ugh)?')
        if v:
            boro = _clean(v).rstrip(",").title()
            result["borough"] = boro
            if boro.lower() in BOROUGH_TO_COUNTY:
                result["county"] = BOROUGH_TO_COUNTY[boro.lower()]

    # Manhattan / borough shorthands como fallback
    if "borough" not in result:
        if re.search(r'\bManhattan\b', text, re.I):
            result["borough"] = "Manhattan"; result["county"] = "New York"
        elif re.search(r'\bBronx\b', text, re.I):
            result["borough"] = "Bronx";     result["county"] = "Bronx"
        elif re.search(r'\bBrooklyn\b', text, re.I):
            result["borough"] = "Brooklyn";  result["county"] = "Kings"
        elif re.search(r'\bQueens\b', text, re.I):
            result["borough"] = "Queens";    result["county"] = "Queens"
        elif re.search(r'\bStaten Island\b', text, re.I):
            result["borough"] = "Staten Island"; result["county"] = "Richmond"

    # ── Work Start Date  →  inline "Work Start Date: 2/19/26" ──
    v = inline_val(r'Work\s+Start\s+Date')
    if v:
        result["date_directed"] = v

    # ── Work Completion Date  →  línea anterior a "Work Completion Date:" ──
    v = prev_val(r'Work\s+Completion\s+Date\s*:?$')
    if not v:
        v = inline_val(r'Work\s+Completion\s+Date')
    if v and re.match(r'\d{1,2}/\d{1,2}/\d{2,4}', v):
        result["work_end_date"] = v

    # ── RC Number ──
    # En el PDF el RC está inline: "RC No.: XXXXX" o en línea siguiente
    v = inline_val(r'RC\s*No\.?')
    if v and re.match(r'[A-Z0-9\-]+', v) and len(v) < 30:
        result["rc_number"] = v.strip()
    if not result.get("rc_number"):
        v = next_val(r'RC\s*No\.?\s*:?\s*$')
        if v and re.match(r'[A-Z0-9\-]+', v) and len(v) < 30:
            result["rc_number"] = v.strip()

    # ── Trade ──
    # Página 3: "GC:" aparece como checkbox marcado → el trade es "GC"
    # Otros posibles: "PLUMBING", "ELECTRICAL", etc. en campo "TRADE:" inline
    v = inline_val(r'TRADE')
    if not v or v.startswith('BID') or v.startswith('$'):
        v = None
    if not v:
        # Buscar checkboxes de tipo de trade en Work Description Form
        trade_map = [
            (r'\bGC\s*:', 'GC'),
            (r'\bPLUMBING\s*:', 'Plumbing'),
            (r'\bELECTRICAL\s*:', 'Electrical'),
            (r'\bHINGE\s*:', 'Hinge'),
            (r'\bPAINT\s*:', 'Painting'),
        ]
        for pattern, label in trade_map:
            # Solo cuenta si la línea es exactamente ese checkbox (corta)
            for l in lines:
                if re.match(pattern + r'\s*$', l, re.I):
                    v = label
                    break
            if v:
                break
    if v and len(v) < 40:
        result["trade"] = v

    # ── Job description — página 3, después de "Job Description:" ──
    # Corta antes del boilerplate de contactos HPD o instrucciones
    m = re.search(
        r'Job\s+Description[:\s]*\n(.*?)(?:CONTRACTOR MUST CONTACT|IF NO WORK IS PERFORMED|BUILDING ADDRESS:|TRADE:|BID AMOUNT)',
        text, re.I | re.S
    )
    if m:
        raw = m.group(1)
        # Filtrar boilerplate y líneas muy cortas
        SKIP = re.compile(r'NYC HPD EMERGENCY|ESSENTIAL SERVICE WORK|CONTRACTOR MUST SIGN', re.I)
        desc_lines = [l.strip() for l in raw.split('\n')
                      if len(l.strip()) > 4 and not SKIP.search(l)]
        desc = _clean(" ".join(desc_lines))
        words = desc.split()
        lines_out, current = [], []
        for w in words:
            current.append(w)
            if len(" ".join(current)) > 75:
                lines_out.append(" ".join(current[:-1]))
                current = [w]
        if current:
            lines_out.append(" ".join(current))
        for i, line in enumerate(lines_out[:6], 1):
            result[f"inv_desc{i}"] = line

    return result


@app.route("/api/parse-omo-pdf", methods=["POST"])
@login_required
@role_required("admin", "worker")
def parse_omo_pdf():
    if "file" not in request.files:
        return jsonify({"error": "No file"}), 400
    file = request.files["file"]
    if not file.filename.lower().endswith(".pdf"):
        return jsonify({"error": "Must be a PDF"}), 400
    try:
        data = parse_hpd_omo_pdf(file.read())
    except Exception as e:
        return jsonify({"error": f"Parse error: {e}"}), 500
    return jsonify(data)


# ─── Inicio ───────────────────────────────────────────────────────────────────

with app.app_context():
    init_db()

if __name__ == "__main__":
    print("=" * 50)
    print("  Affidavit Manager → http://localhost:8080")
    print("=" * 50)
    app.run(debug=True, port=8080)
