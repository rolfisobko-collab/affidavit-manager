# HPD OMO Service Manager — LB & J Construction Inc.

> Sistema de gestión de servicios de reparaciones de emergencia para el **NYC Department of Housing Preservation and Development (HPD)**, operado por **LB & J Construction Inc.**

---

## ¿Qué es este sistema?

LB & J Construction es un contratista de emergencia contratado por HPD para realizar reparaciones urgentes en edificios residenciales de la Ciudad de Nueva York.

Cada trabajo se origina como un **Open Market Order (OMO)** — una orden emitida por HPD que le indica al contratista a qué edificio ir y qué reparar. Este sistema gestiona el ciclo de vida completo de cada OMO: desde que se recibe la orden hasta que se cobra.

---

## El flujo de un servicio (OMO)

```
┌─────────────────────────────────────────────────────────────────────┐
│  HPD emite un OMO (e.g., EQ20025)                                   │
│  → Edificio: 227 Cherry St, Apt 11C, Manhattan                     │
│  → Trabajo: Reparación de emergencia (carpintería, plomería, etc.)  │
└─────────────────────────────┬───────────────────────────────────────┘
                              │
                              ▼
                    Contratista visita el sitio
                              │
              ┌───────────────┴───────────────────┐
              │                                   │
              ▼                                   ▼
   ╔═══════════════════╗              ╔══════════════════════╗
   ║  TRABAJO REALIZADO ║              ║  SIN TRABAJO         ║
   ║  (Work Performed)  ║              ║  (No Work Performed) ║
   ╚════════════╤══════╝              ╚══════════╤═══════════╝
                │                               │
    3 sub-tipos:│                   4 razones:  │
    6. ALL work  │                   4. Inaccesible
    7. PARTIAL   │                   5. Ya hecho por otros
    8. INTERRUPTED│                  6. Siendo hecho por otros
                │                   7. Acceso denegado
                │                               │
                ▼                               ▼
   ┌────────────────────────┐    ┌──────────────────────────────┐
   │  DOCUMENTOS GENERADOS  │    │  DOCUMENTOS GENERADOS        │
   │                        │    │                              │
   │ 1. Work Performed       │    │ 1. No Work Performed         │
   │    Affidavit (2 pág.)   │    │    Affidavit (2 pág.)        │
   │    + Notary signature   │    │    + Notary signature        │
   │                        │    │                              │
   │ 2. Invoice              │    │ 2. Invoice                   │
   │    - Materials + qty    │    │    - Mat. 1: "NO WORK DONE"  │
   │    - Bid amount         │    │    - Service charge only     │
   │    - Total charge       │    │    - Total = service charge  │
   └────────────────────────┘    └──────────────────────────────┘
                │                               │
                └───────────────┬───────────────┘
                                ▼
                  Firmados + sellados por Notario
                  (Rajinder Singh — Notary Public)
                                ▼
                    Enviados a HPD Fiscal
                    (Affidavit + Invoice juntos)
                                ▼
                       HPD procesa y paga
```

---

## Los documentos (PDFs) — Cómo se conectan

### 1. Work Performed Affidavit (`work_template.pdf`)

**Cuándo se genera:** El contratista pudo realizar el trabajo.

**Qué declara (bajo juramento ante notario):**
- Página 1: OMO#, condado, fecha dirigido, dirección, tipo de trabajo realizado
  - Ítem 6: TODO el trabajo completado (con fechas inicio/fin)
  - Ítem 7: Trabajo PARCIAL (razón + monto)
  - Ítem 8: Trabajo INTERRUMPIDO por el dueño/agente (monto parcial cobrado)
- Página 2: Si fue interrumpido → datos de quien impidió el trabajo (nombre, relación, descripción)
- Página 2: Fecha de juramento ante notario

**Campos pre-llenados por LB & J:**
- Nombre del declarante: `I, JASPREET SINGH, PRESIDENT OF LB AND J CONSTRUCTION INC`
- Notario: `Rajinder Singh`

**Se entrega a HPD junto con:** la Invoice

---

### 2. No Work Performed Affidavit (`nowork_template.pdf`)

**Cuándo se genera:** El contratista NO pudo realizar el trabajo.

**Qué declara (bajo juramento ante notario):**
- Página 1: OMO#, condado, dirección, cargo de servicio
  - Razón 4: Área físicamente inaccesible
    → 2 intentos de acceso (72hs de diferencia) + 2 intentos telefónicos
  - Razón 5: El trabajo ya fue completado por otros (fecha de llegada)
  - Razón 6: El trabajo está siendo realizado por otros (fecha + nombre del contratista)
  - Razón 7: Acceso denegado → continúa en página 2
- Página 2 (razón 7): Datos del individuo que denegó el acceso (nombre, relación, descripción, teléfono)
- Página 2: Fecha de juramento ante notario

**Campos pre-llenados por LB & J:**
- Nombre del declarante: `I, JASPREET SINGH, PRESIDENT OF LB AND J CONSTRUCTION INC`
- Notario: `Rajinder Singh`

**Se entrega a HPD junto con:** la Invoice (con "NO WORK DONE" como material)

---

### 3. Invoice (`invoice_template.pdf`)

**Cuándo se genera:** SIEMPRE — para todo tipo de servicio (work o no-work).

**Datos clave:**
| Campo | Work Performed | No Work Performed |
|-------|---------------|-------------------|
| Material row 1 | Descripción real (ej: "INSTALL HINGES") | `NO WORK DONE` (valor por defecto del template) |
| Bid Amount | Monto del trabajo | = Service Charge |
| Total Charge | Monto total | = Service Charge |
| Description | Descripción del trabajo realizado | "NO WORK PERFORMED – SERVICE CHARGE" |

**Campos pre-llenados permanentes (LB & J):**
- Tax ID: `820952348`
- Name: `Jaspreet Singh`
- Title: `President`
- Dirección: `110 Jericho Turnpike Ste 206, Floral Park, NY 11001`

**⚠️ Dato importante descubierto:** El template de invoice tiene `"NO WORK DONE"` como valor por defecto en el campo de material #1. Esto confirma que el mismo template se usa para ambos escenarios.

**Se entrega a HPD junto con:** el Affidavit correspondiente

---

### Relación entre los campos de ambos documentos

```
SERVICE (OMO)
├── omo_number          → Affidavit: campo [1] (header + ítem 3/2 + pág.2 header)
│                       → Invoice: campo [OMO]
├── county              → Affidavit: campo [2]
├── borough             → Invoice: campo [BOROUGH] (auto-derivado del county)
├── building_address    → Affidavit: campo [5] / [23]
│                       → Invoice: campo [Building Address]
├── work_location_apt   → Invoice: campo [Work LocationApt]
├── date_directed       → Affidavit: campo [4] (ítem 2 "That on...")
│                       = work_start_date en la Invoice
├── work_start_date     → Affidavit: campo [6] (ítem 6 "beginning on")
│                       → Invoice: campo [Date Work Started_2]
├── work_end_date       → Affidavit: campo [7] (ítem 6 "completed on")
│                       → Invoice: campo [Date Work Completed_2]
├── trade               → Invoice: campo [TRADE]
├── invoice_date        → Invoice: campo [INVOICE DATE]
└── sworn_day/month/year→ Affidavit: campos [19]/[21]/[22]
```

---

## Estados del servicio

```
PENDING ──→ WORK PERFORMED ──→ SUBMITTED ──→ PAID
        └──→ NO WORK       ──→ SUBMITTED ──→ PAID
```

| Estado | Color | Descripción |
|--------|-------|-------------|
| `pending` | ⚪ Gris | OMO recibido, visita pendiente |
| `work_performed` | 🟢 Verde | Trabajo realizado, documentos listos |
| `no_work_performed` | 🔴 Rojo | Sin trabajo, documentos listos |
| `submitted` | 🔵 Azul | Documentos enviados a HPD Fiscal |
| `paid` | 🟡 Dorado | Pago recibido de HPD |

---

## Ejemplos reales analizados

### EQ20025 — Work Performed
- **Edificio:** 227 Cherry Street, Apt. 11C, Manhattan
- **Trabajo:** Puerta con auto-cierre (hinges)
- **Invoice #:** 2029
- **Fecha:** 03/17/26
- **Monto:** $270.00
- **Material:** `INSTALL HINGES-TOTAL DOORS= (1)` | Qty: 1

### EQ20453 — Work Performed
- **Edificio:** 227 West 15 Street, Apt. 1, Manhattan
- **Trabajo:** Idéntico (auto-closing door)
- **Invoice #:** 2027
- **Fecha:** 03/13/26
- **Monto:** $270.00

> Ambos ejemplos muestran el mismo tipo de trabajo con el mismo monto, sugiriendo que hay un catálogo de trabajos estándar con precios fijos.

---

## Stack técnico

| Capa | Tecnología |
|------|------------|
| Backend | Python 3 + Flask |
| PDF Filling | PyMuPDF (fitz) — form fields nativos |
| Base de datos | PostgreSQL (producción) / SQLite (local) |
| Frontend | Vanilla JS + HTML/CSS (SPA responsive) |
| Servidor prod. | Gunicorn |
| Deploy | Render.com (free tier) |

---

## Instalación local

```bash
# Clonar el repositorio
git clone https://github.com/rolfisobko-collab/affidavit-manager.git
cd affidavit-manager

# Instalar dependencias
pip3 install -r requirements.txt

# Iniciar el servidor
python3 app.py
# → http://localhost:8080
```

---

## Estructura del proyecto

```
affidavit-manager/
├── app.py                   # Backend Flask — CRUD + generación de PDFs
├── pdf_filler.py            # Motor de relleno de PDFs
├── requirements.txt
├── Procfile                 # Comando Gunicorn para Render
├── render.yaml              # Config de infraestructura en Render
├── pdfs/
│   ├── work_template.pdf    # Template: Work Performed Affidavit
│   ├── nowork_template.pdf  # Template: No Work Performed Affidavit
│   └── invoice_template.pdf # Template: Invoice (pre-set con "NO WORK DONE")
├── templates/
│   └── index.html           # Frontend SPA (EN/ES)
├── output/                  # PDFs generados (gitignored)
└── records.db               # SQLite local (gitignored)
```

---

## Deployment en Render.com

El archivo `render.yaml` configura automáticamente:
- Web service (Python, Gunicorn, free tier)
- PostgreSQL database (free tier)
- Variable `DATABASE_URL` conectando ambos

El sistema detecta automáticamente si usa PostgreSQL (`DATABASE_URL` presente) o SQLite (local).

---

## Notas operativas importantes

1. **Firma y sello notarial:** Los PDFs generados tienen el nombre del notario (`Rajinder Singh`) pre-impreso en el campo tipográfico, pero la **firma manuscrita y el sello deben ser añadidos a mano** en el documento impreso.

2. **Firma del principal:** El campo `SIGNATURE OF PRINCIPAL (Blue ink only)` también requiere firma manuscrita en tinta azul.

3. **OMO# en affidavit:** El número de OMO aparece automáticamente en el encabezado de página 1, en el ítem 3 o 2, y en el encabezado de página 2 — todo desde un único campo de entrada (sincronización nativa del PDF).

4. **Invoice para No Work:** El template ya tiene `"NO WORK DONE"` como valor por defecto en el campo de material #1. El sistema lo preserva automáticamente cuando el servicio es tipo `no_work_performed`.

5. **Borough vs County:** El invoice usa "Borough" (Brooklyn, Manhattan, Bronx, Queens, Staten Island) mientras el affidavit usa "County" (Kings, New York, Bronx, Queens, Richmond). El sistema los auto-mapea.
