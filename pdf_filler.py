"""
PDF Filler — rellena los affidavits y la invoice usando campos de formulario reales.
Los nuevos templates (Rev. 03.10.2025) son PDFs fillables, no scaneados,
por lo que la precisión es perfecta sin necesidad de coordenadas manuales.
"""

import fitz  # PyMuPDF
import os
import zipfile
from datetime import datetime

BASE_DIR       = os.path.dirname(os.path.abspath(__file__))
WORK_TEMPLATE  = os.path.join(BASE_DIR, "pdfs", "work_template.pdf")
NOWORK_TEMPLATE= os.path.join(BASE_DIR, "pdfs", "nowork_template.pdf")
INVOICE_TEMPLATE = os.path.join(BASE_DIR, "pdfs", "invoice_template.pdf")
OUTPUT_DIR     = os.path.join(BASE_DIR, "output")

# County → Borough mapping
COUNTY_BOROUGH = {
    "kings":    "Brooklyn",
    "new york": "Manhattan",
    "bronx":    "Bronx",
    "queens":   "Queens",
    "richmond": "Staten Island",
}

# ─── Mapeados de campos ────────────────────────────────────────────────────────
#
# Cada campo tiene nombre (field_name en el PDF) e índice (para campos duplicados).
# Los campos con nombre '1' (OMO#) existen en múltiples páginas — al settear
# uno se sincronizan todos automáticamente por la spec de PDF.

WORK_FIELDS = {
    # nombre_en_record  : (nombre_campo_pdf, índice_si_duplicado)
    "omo_number"        : "1",     # header pág 1, ítem 3 y header pág 2 (mismo nombre → sync)
    # county ('2') lo completa la escribana — NO se rellena desde el sistema
    "date_directed"     : "4",
    "building_address"  : "5",
    "work_start_date"   : "6",     # "beginning on ___"
    "work_end_date"     : "7",     # "completed on ___"
    # work_contractor_name: campo '3' ya tiene el texto del juramento hardcodeado en el template — NO se pisa
    "signer_name"       : "15",   # Type or Print Name del firmante (pág 2)
    "partial_reason"    : "8",
    "partial_amount"    : "9",
    "interrupted_amount": "10",
    "prevented_name"    : "11",    # pág 2 — quien impidió
    "prevented_rel"     : "13",    # "as: ___"
    "prevented_desc"    : "14",
    # sworn_day/month/year: los completa la notaria a mano — NO se rellenan desde el sistema
}

NOWORK_FIELDS = {
    "omo_number"        : "1",     # header + ítem 2 OMO# (sync automático)
    # county ('2') lo completa la escribana — NO se rellena desde el sistema
    "building_address"  : "23",    # "to go to building located at ___"
    "service_charge"    : "4",
    "inacc_reason"      : "5",     # línea 1 de inaccesibilidad
    "inacc_reason2"     : "6",     # línea 2 de inaccesibilidad
    "attempt_date1"     : "7",
    "attempt_date2"     : "9",
    "phone_date1"       : "8",
    "phone_date2"       : "10",
    "arrival_5"         : "11",
    "arrival_6"         : "12",
    "contractor_name"   : "13",
    "arrival_7"         : "14",    # pág 2 — ítem 7 "work site on ___"
    "individual_name"   : "15",
    "individual_rel"    : "16",    # "building ___"
    "individual_desc"   : "17",
    "individual_phone"  : "18",
    "signer_name"       : "50",   # Type or Print Name del firmante (pág 2)
    # sworn_day/month/year: los completa la notaria a mano — NO se rellenan desde el sistema
}

INVOICE_FIELDS = {
    "omo_number"        : "OMO",
    "invoice_number"    : "Invoice",
    "rc_number"         : "If Yes Provide RC or Mini RC",
    "trade"             : "TRADE",
    "invoice_date"      : "INVOICE DATE",
    "borough"           : "BOROUGH",
    "work_start_date"   : "Date Work Started_2",
    "building_address"  : "Building Address",
    "work_end_date"     : "Date Work Completed_2",
    "work_location_apt" : "Work LocationApt",
    "inv_desc1"         : "DESCRIPTION OF WORK DONERow1",
    "inv_desc2"         : "DESCRIPTION OF WORK DONERow2",
    "inv_desc3"         : "DESCRIPTION OF WORK DONERow3",
    "inv_desc4"         : "DESCRIPTION OF WORK DONERow4",
    "inv_desc5"         : "DESCRIPTION OF WORK DONERow5",
    "inv_desc6"         : "DESCRIPTION OF WORK DONERow6",
    "bid_amount"        : "Bid Amount_2",
    "total_charge"      : "TOTAL CHARGE",
    "signer_name"       : "NAME Please Print",
}

# Materiales: campos '1'-'6' del invoice y 6 primeros campos 'Quanity'
INVOICE_MAT_FIELDS  = [str(i) for i in range(1, 7)]   # nombres de campo material
INVOICE_QTY_FIELD   = "Quanity"                        # campo duplicado (12 instancias)


# ─── Motor de relleno ─────────────────────────────────────────────────────────

def _fill_pdf(template_path: str, field_values: dict, output_path: str):
    """
    Rellena un PDF fillable usando los nombres de campo.
    Itera página a página para mantener las referencias de widgets válidas.
    """
    doc = fitz.open(template_path)

    for page in doc:
        for w in page.widgets():
            name = w.field_name
            if name in field_values and field_values[name]:
                w.field_value = str(field_values[name])
                w.update()

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    doc.save(output_path)
    doc.close()
    return output_path


def _build_affidavit_values(record: dict) -> dict:
    """Construye el dict de valores para el affidavit (work o nowork)."""
    fields = WORK_FIELDS if record.get("doc_type") == "work" else NOWORK_FIELDS
    values = {}

    for rec_key, pdf_key in fields.items():
        val = record.get(rec_key, "") or ""

        # sworn_year: solo 2 dígitos (el template ya imprime "20")
        if rec_key == "sworn_year" and len(val) >= 4:
            val = val[-2:]

        # arrival_5/6/7 no existen en record → mapear arrival_date al campo correcto según razón
        if rec_key in ("arrival_5", "arrival_6", "arrival_7"):
            reason = str(record.get("nowork_reason") or "")
            reason_to_key = {"5": "arrival_5", "6": "arrival_6", "7": "arrival_7"}
            if reason_to_key.get(reason) == rec_key:
                val = record.get("arrival_date", "") or ""
            else:
                val = ""

        # inacc_reason2 no existe como campo en record → se divide inacc_reason
        if rec_key == "inacc_reason2":
            full = record.get("inacc_reason", "") or ""
            # Si el texto es largo, dividir en mitad para las dos líneas
            mid = len(full) // 2
            if len(full) > 60:
                # Cortar en el espacio más cercano a la mitad
                cut = full.rfind(" ", 0, mid + 10)
                val = full[cut:].strip() if cut > 0 else full[mid:]
            else:
                val = ""  # Si es corto, entra en la primera línea sola

        if rec_key == "inacc_reason" and record.get("inacc_reason", ""):
            full = record.get("inacc_reason", "") or ""
            if len(full) > 60:
                mid = len(full) // 2
                cut = full.rfind(" ", 0, mid + 10)
                val = full[:cut].strip() if cut > 0 else full[:mid]

        if val:
            values[pdf_key] = val

    return values


def _build_invoice_values(record: dict) -> dict:
    """
    Construye el dict de valores para la invoice.

    Lógica según tipo de servicio:
    - work_performed:  materiales + amounts del record
    - no_work_performed: mat[1] queda como "NO WORK DONE" (default del template),
                         bid_amount y total_charge se toman del service_charge
    """
    values = {}

    for rec_key, pdf_key in INVOICE_FIELDS.items():
        val = record.get(rec_key, "") or ""
        if val:
            values[pdf_key] = val

    # Auto-derivar borough desde county si no está seteado
    if not values.get("BOROUGH"):
        county = (record.get("county") or "").lower().strip()
        borough = COUNTY_BOROUGH.get(county, "")
        if borough:
            values["BOROUGH"] = borough

    # Invoice date: si no está, usar work_end_date o today
    if not values.get("INVOICE DATE"):
        values["INVOICE DATE"] = (
            record.get("work_end_date") or
            record.get("invoice_date") or
            datetime.today().strftime("%m/%d/%y")
        )

    # ── Lógica específica para No Work Performed ──────────────────────────────
    if record.get("doc_type") == "nowork":
        svc = (record.get("service_charge") or "0.00").strip()
        values["Bid Amount_2"] = svc
        values["TOTAL CHARGE"] = svc

        # Limpiar TODOS los campos de descripción — no queremos inv_desc del OMO
        for i in range(1, 9):
            values.pop(f"DESCRIPTION OF WORK DONERow{i}", None)

        reason = str(record.get("nowork_reason") or "")
        arrival = record.get("arrival_date") or ""
        date_str = f" ON {arrival.upper()}" if arrival else ""

        if reason == "4":
            values["DESCRIPTION OF WORK DONERow1"] = "NO WORK PERFORMED – AREA PHYSICALLY INACCESSIBLE."
        elif reason == "5":
            values["DESCRIPTION OF WORK DONERow1"] = f"NO WORK PERFORMED – WHEN I ARRIVED AT THE WORK SITE{date_str},"
            values["DESCRIPTION OF WORK DONERow2"] = "I FOUND THE WORK DESCRIBED IN THE OMO HAD BEEN COMPLETED BY OTHERS."
        elif reason == "6":
            values["DESCRIPTION OF WORK DONERow1"] = f"NO WORK PERFORMED – WHEN I ARRIVED AT THE WORK SITE{date_str},"
            values["DESCRIPTION OF WORK DONERow2"] = "I FOUND THE WORK DESCRIBED IN THE OMO WAS BEING PERFORMED BY OTHERS."
        elif reason == "7":
            values["DESCRIPTION OF WORK DONERow1"] = "I WAS DENIED ACCESS BY THE TENANT, OCCUPANT OR OWNER."
        else:
            values["DESCRIPTION OF WORK DONERow1"] = "NO WORK PERFORMED – SERVICE CHARGE ONLY"
        # NO setear campo '1' (material) → template mantiene "NO WORK DONE"

    return values


def _build_invoice_qty_values(record: dict) -> list:
    """
    Devuelve lista de (índice, valor) para los campos 'Quanity' duplicados.
    Solo sets los primeros 6 slots.
    """
    result = []
    for i in range(1, 7):
        qty = record.get(f"inv_qty{i}") or ""
        result.append((i - 1, qty))  # (índice en lista de widgets, valor)
    return result


# ─── API pública ──────────────────────────────────────────────────────────────

def fill_affidavit(record: dict, output_path: str) -> str:
    """Genera el affidavit (work o nowork) y lo guarda en output_path."""
    template = WORK_TEMPLATE if record.get("doc_type") == "work" else NOWORK_TEMPLATE
    values   = _build_affidavit_values(record)
    return _fill_pdf(template, values, output_path)


def fill_invoice(record: dict, output_path: str) -> str:
    """Genera la invoice y la guarda en output_path."""
    values = _build_invoice_values(record)

    doc = fitz.open(INVOICE_TEMPLATE)

    # Contadores de instancias para campos duplicados (ej: 'Quanity')
    qty_counter = 0

    for page in doc:
        for w in page.widgets():
            name = w.field_name

            # Campos normales
            if name in values and values[name]:
                w.field_value = str(values[name])
                w.update()
                continue

            # Materiales: campos '1'-'12' (usar solo '1'-'6')
            if name in INVOICE_MAT_FIELDS:
                idx = INVOICE_MAT_FIELDS.index(name) + 1
                mat = record.get(f"inv_mat{idx}") or ""
                if mat:
                    w.field_value = str(mat)
                    w.update()
                continue

            # Cantidades: campo 'Quanity' duplicado (por orden de aparición)
            if name == INVOICE_QTY_FIELD and qty_counter < 6:
                qty = record.get(f"inv_qty{qty_counter + 1}") or ""
                if qty:
                    w.field_value = str(qty)
                    w.update()
                qty_counter += 1

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    doc.save(output_path)
    doc.close()
    return output_path


def generate_pdfs(record: dict) -> dict:
    """
    Genera el affidavit Y la invoice para un registro.
    Devuelve {'affidavit': path, 'invoice': path, 'zip': path}
    """
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    rec_id  = record.get("id", "tmp")
    omo_num = (record.get("omo_number") or "sin_omo").replace("/", "_").replace(" ", "_")
    doc_type = "WORK" if record.get("doc_type") == "work" else "NOWORK"

    aff_path = os.path.join(OUTPUT_DIR, f"{doc_type}_Affidavit_{omo_num}_{rec_id}.pdf")
    inv_path = os.path.join(OUTPUT_DIR, f"Invoice_{omo_num}_{rec_id}.pdf")
    zip_path = os.path.join(OUTPUT_DIR, f"Docs_{omo_num}_{rec_id}.zip")

    fill_affidavit(record, aff_path)
    fill_invoice(record, inv_path)

    # Crear ZIP con ambos docs
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.write(aff_path, os.path.basename(aff_path))
        zf.write(inv_path, os.path.basename(inv_path))

    return {"affidavit": aff_path, "invoice": inv_path, "zip": zip_path}


# Backward-compat alias
def generate_pdf(record: dict) -> str:
    return generate_pdfs(record)["affidavit"]
