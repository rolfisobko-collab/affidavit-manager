"""
PDF Filler - Escribe sobre los templates de affidavit existentes.
Coordenadas en el espacio del PDF (2480 x 3508 unidades, A4 a 300 DPI).

Para ajustar posiciones: cada campo tiene (x, y) donde (0,0) es esquina superior izquierda.
Modificar los valores en WORK_FIELDS y NOWORK_FIELDS si el texto aparece desplazado.
"""

import fitz  # PyMuPDF
import os
import shutil
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
WORK_TEMPLATE   = os.path.join(BASE_DIR, "pdfs", "work_template.pdf")
NOWORK_TEMPLATE = os.path.join(BASE_DIR, "pdfs", "nowork_template.pdf")
OUTPUT_DIR      = os.path.join(BASE_DIR, "output")

# Fuente y tamaño de texto para rellenar los blancos
# En este PDF, 1 unidad ≈ 1/300 pulgada. 12pt estándar ≈ 50 unidades.
FONT      = "helv"
FONT_SIZE = 42
COLOR     = (0, 0, 0)  # Negro

# ─────────────────────────────────────────────────────────────────────────────
# WORK PERFORMED AFFIDAVIT  —  coordenadas por campo
# Calibradas usando marcadores cada 50 unidades sobre el PDF (2480 x 3508 pts)
# Formato: { nombre: (page_idx, x, y) }   y = baseline del texto
# ─────────────────────────────────────────────────────────────────────────────
WORK_FIELDS = {
    # ── Página 1 (índice 0) ──────────────────────────────────────────────────
    "omo_header":        (0,  960, 490),   # OMO # en el encabezado (blank line)
    "county":            (0,  500, 740),   # County of ___ (blank after "COUNTY OF ")
    "date_directed":     (0,  490, 1240),  # "That on [fecha] I was directed..."
    "building_address":  (0,  190, 1340),  # dirección del edificio (línea completa)
    "omo_item3":         (0,  380, 1615),  # OMO # en "# ___" segunda línea ítem 3

    "work_start_date":   (0, 1510, 2315),  # "beginning on [fecha]"  (fin de línea)
    "work_end_date":     (0,  575, 2390),  # "and completed on [fecha]"  (inicio de línea)

    "partial_reason":    (0,  285, 2580),  # blank line debajo de "due to"  (ítem 7)
    "partial_amount":    (0, 1360, 2715),  # "$___" monto ítem 7
    "interrupted_amount":(0,  330, 2968),  # "$___" monto ítem 8 — después del "$" en la última línea

    # ── Página 2 (índice 1) ──────────────────────────────────────────────────
    "omo_p2":            (1, 1150, 240),   # OMO # encabezado pág 2 (after "OMO # ")
    "prevented_name":    (1,  920, 548),   # nombre de quien impidió — después de "name as: "
    "prevented_rel":     (1,  495, 620),   # relación con el edificio — después de "as: "
    "prevented_desc":    (1,  975, 732),   # descripción física — después de "Description of individual "
    "sworn_day":         (1,  580, 1178),  # día ante notario
    "sworn_month":       (1,  718, 1178),  # mes ante notario
    "sworn_year":        (1, 1050, 1178),  # 2 últimos dígitos del año (el "20" ya está impreso)
}

# ─────────────────────────────────────────────────────────────────────────────
# NO WORK PERFORMED AFFIDAVIT  —  coordenadas por campo
# ─────────────────────────────────────────────────────────────────────────────
NOWORK_FIELDS = {
    # ── Página 1 (índice 0) ──────────────────────────────────────────────────
    "omo_header":        (0,  960, 448),   # OMO # encabezado
    "county":            (0,  500, 682),   # County of ___
    "omo_item2":         (0, 1720, 1250),  # OMO # en "...OMO # ___" (fin de línea 1)
    "building_address":  (0, 1230, 1310),  # dirección — blank después de "to go to the building located at "
    "service_charge":    (0, 1400, 1524),  # "$___" cargo servicio ítem 3

    # Razón 4 – físicamente inaccesible
    "inacc_reason":      (0,  285, 1898),  # blank line de inaccesibilidad
    "attempt_date1":     (0, 1658, 2092),  # "access on ___"  (fin de línea)
    "attempt_date2":     (0,  378, 2158),  # "and ___"         (inicio de línea)
    "phone_date1":       (0, 1658, 2158),  # "telephone on ___" (fin de la misma línea)
    "phone_date2":       (0,  378, 2225),  # "and ___"          (inicio de línea 3)

    # Razón 5 – trabajo ya completado por otros
    "arrival_5":         (0, 1300, 2400),  # "work site on ___" ítem 5

    # Razón 6 – trabajo siendo ejecutado por otros
    "arrival_6":         (0, 1300, 2548),  # "work site on ___" ítem 6
    "contractor_name":   (0, 1618, 2682),  # "name as: ___"  ítem 6a

    # ── Página 2 (índice 1) ──────────────────────────────────────────────────
    "omo_p2":            (1, 1150, 268),   # OMO # encabezado pág 2 (after "OMO # ")

    # Razón 7 – acceso denegado
    "arrival_7":         (1, 1300, 578),   # "work site on ___" ítem 7
    "individual_name":   (1,  950, 833),   # nombre — después de "Stated his/her name as: "
    "individual_rel":    (1,  845, 898),   # relación — después de "building "
    "individual_desc":   (1,  975, 1033),  # descripción — después de "Description of individual "
    "individual_phone":  (1, 1370, 1193),  # teléfono — después de "Telephone number of the individual "

    "sworn_day":         (1,  548, 1778),  # día ante notario
    "sworn_month":       (1,  703, 1778),  # mes ante notario
    "sworn_year":        (1, 1003, 1778),  # año ante notario
}


def _insert_text(page, x: float, y: float, text: str):
    """Inserta texto en una página en coordenadas absolutas (top-left origin)."""
    if not text:
        return
    page.insert_text(
        (x, y),
        str(text),
        fontname=FONT,
        fontsize=FONT_SIZE,
        color=COLOR,
    )


def fill_work_pdf(record: dict, output_path: str) -> str:
    """Genera un PDF 'Work Performed' llenado con los datos del registro."""
    doc = fitz.open(WORK_TEMPLATE)
    pages = list(doc)

    def page_write(field_key, value):
        if not value:
            return
        pg_idx, x, y = WORK_FIELDS[field_key]
        _insert_text(pages[pg_idx], x, y, value)

    omo = record.get("omo_number", "")
    page_write("omo_header",   omo)
    page_write("omo_p2",       omo)
    page_write("omo_item3",    omo)
    page_write("county",       record.get("county", ""))
    page_write("date_directed", record.get("date_directed", ""))
    page_write("building_address", record.get("building_address", ""))

    work_type = record.get("work_type", "")

    if work_type == "ALL":
        page_write("work_start_date", record.get("work_start_date", ""))
        page_write("work_end_date",   record.get("work_end_date", ""))

    elif work_type == "PARTIAL":
        page_write("partial_reason", record.get("partial_reason", ""))
        amt = record.get("partial_amount", "")
        page_write("partial_amount", amt)

    elif work_type == "INTERRUPTED":
        amt = record.get("interrupted_amount", "")
        page_write("interrupted_amount", amt)

    # Datos de la persona que impidió el trabajo (página 2, aplica a ítem 8)
    page_write("prevented_name", record.get("prevented_name", ""))
    page_write("prevented_rel",  record.get("prevented_rel", ""))
    page_write("prevented_desc", record.get("prevented_desc", ""))

    # Sección notario  (el formulario ya imprime "20", solo escribimos los 2 últimos dígitos)
    page_write("sworn_day",   record.get("sworn_day", ""))
    page_write("sworn_month", record.get("sworn_month", ""))
    yr = record.get("sworn_year", "")
    page_write("sworn_year",  yr[-2:] if len(yr) >= 4 else yr)

    doc.save(output_path)
    doc.close()
    return output_path


def fill_nowork_pdf(record: dict, output_path: str) -> str:
    """Genera un PDF 'No Work Performed' llenado con los datos del registro."""
    doc = fitz.open(NOWORK_TEMPLATE)
    pages = list(doc)

    def page_write(field_key, value):
        if not value:
            return
        pg_idx, x, y = NOWORK_FIELDS[field_key]
        _insert_text(pages[pg_idx], x, y, value)

    omo = record.get("omo_number", "")
    page_write("omo_header",   omo)
    page_write("omo_p2",       omo)
    page_write("omo_item2",    omo)
    page_write("county",       record.get("county", ""))
    page_write("building_address",  record.get("building_address", ""))
    page_write("service_charge",    record.get("service_charge", ""))

    reason = record.get("nowork_reason", "")
    arrival = record.get("arrival_date", "")

    if reason == "4":
        page_write("inacc_reason",  record.get("inacc_reason", ""))
        page_write("attempt_date1", record.get("attempt_date1", ""))
        page_write("attempt_date2", record.get("attempt_date2", ""))
        page_write("phone_date1",   record.get("phone_date1", ""))
        page_write("phone_date2",   record.get("phone_date2", ""))

    elif reason == "5":
        page_write("arrival_5", arrival)

    elif reason == "6":
        page_write("arrival_6",       arrival)
        page_write("contractor_name", record.get("contractor_name", ""))

    elif reason == "7":
        page_write("arrival_7",       arrival)
        page_write("individual_name", record.get("individual_name", ""))
        page_write("individual_rel",  record.get("individual_rel", ""))
        page_write("individual_desc", record.get("individual_desc", ""))
        page_write("individual_phone",record.get("individual_phone", ""))

    # Sección notario  (el formulario ya imprime "20", solo escribimos los 2 últimos dígitos)
    page_write("sworn_day",   record.get("sworn_day", ""))
    page_write("sworn_month", record.get("sworn_month", ""))
    yr = record.get("sworn_year", "")
    page_write("sworn_year",  yr[-2:] if len(yr) >= 4 else yr)

    doc.save(output_path)
    doc.close()
    return output_path


def generate_pdf(record: dict) -> str:
    """
    Genera el PDF llenado para un registro y devuelve la ruta del archivo.
    El archivo se guarda en /output/ con nombre OMO_<id>.pdf
    """
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    rec_id  = record.get("id", "tmp")
    omo_num = record.get("omo_number", "sin_omo").replace("/", "_").replace(" ", "_")
    filename = f"{'WORK' if record.get('doc_type') == 'work' else 'NOWORK'}_{omo_num}_{rec_id}.pdf"
    output_path = os.path.join(OUTPUT_DIR, filename)

    if record.get("doc_type") == "work":
        fill_work_pdf(record, output_path)
    else:
        fill_nowork_pdf(record, output_path)

    return output_path
