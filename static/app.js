/* ═══════════════════════════════════════════════════════════════════════════════
   HPD Service Manager — Application Logic
   ═══════════════════════════════════════════════════════════════════════════════ */

// ── Translations ───────────────────────────────────────────────────────────────
const LANG = {
  en: {
    app_title: 'HPD Service Manager',
    new_btn: 'New OMO',
    pipe_all: 'All', pipe_pending: 'Pending', pipe_work: 'Work Done',
    pipe_nowork: 'No Work', pipe_submitted: 'Submitted', pipe_paid: 'Paid',
    search_ph: 'Search OMO#, address, county…',
    filter_all: 'All Types', filter_work: 'Work Performed', filter_nowork: 'No Work Performed',
    empty_title: 'No services found',
    empty_sub: 'Create a new OMO or adjust your filters.',
    modal_new: 'New OMO Service',
    modal_edit: 'Edit Service',
    modal_sub_new: 'Fill in the details for this Open Market Order',
    modal_sub_edit: 'Update service information',
    step_job: 'Job Info', step_outcome: 'Outcome', step_invoice: 'Invoice', step_notary: 'Notary',
    // Job tab
    lbl_omo: 'OMO Number', lbl_status: 'Current Status',
    lbl_address: 'Building Address', lbl_apt: 'Work Location / Apt',
    lbl_county: 'County', lbl_borough: 'Borough',
    lbl_trade: 'Trade / Type of Work', lbl_date_directed: 'Date Directed by HPD',
    opt_county_0: '— Select county —',
    opt_county_kings: 'Kings (Brooklyn)', opt_county_ny: 'New York (Manhattan)',
    opt_county_bronx: 'Bronx', opt_county_queens: 'Queens', opt_county_richmond: 'Richmond (S.I.)',
    opt_borough_0: '— Auto from county —',
    // Outcome tab
    doctype_work_label: 'Work Performed',
    doctype_work_desc: 'Contractor completed repair work',
    doctype_nowork_label: 'No Work Performed',
    doctype_nowork_desc: 'Contractor could not perform work',
    sep_work_type: 'Work Type (Answer 6, 7 or 8)',
    sep_work_dates: 'Work Dates',
    lbl_work_start: 'Work Start Date', lbl_work_end: 'Work End Date',
    wt_all: '6 · ALL work completed',
    wt_partial: '7 · PARTIAL work',
    wt_interrupted: '8 · INTERRUPTED by owner',
    lbl_partial_reason: 'Reason for partial work',
    lbl_partial_amount: 'Partial Amount ($)',
    lbl_interrupted_amount: 'Amount for work done ($)',
    sep_prevented: 'Individual who prevented work (Page 2)',
    lbl_prev_name: 'Name', lbl_prev_rel: 'Relationship to building', lbl_prev_desc: 'Physical description',
    lbl_service_charge: 'Service Charge ($)',
    sep_nowork_reason: 'Reason — Answer 4, 5, 6 or 7',
    nr_4: '4 · Physically inaccessible',
    nr_5: '5 · Work done by others',
    nr_6: '6 · Work being done by others',
    nr_7: '7 · Access denied',
    lbl_inacc_reason: 'Describe inaccessibility',
    lbl_attempt1: 'Access attempt date 1 (≥72h apart)',
    lbl_attempt2: 'Access attempt date 2',
    lbl_phone1: 'Phone attempt date 1',
    lbl_phone2: 'Phone attempt date 2',
    lbl_arrival: 'Date of arrival at site',
    lbl_contractor: 'Contractor name (who was working)',
    lbl_ind_name: 'Individual name',
    lbl_ind_rel: 'Relationship to building',
    lbl_ind_desc: 'Physical description',
    lbl_ind_phone: 'Telephone number',
    // Invoice tab
    lbl_invoice_num: 'Invoice #', lbl_invoice_date: 'Invoice Date',
    lbl_rc: 'RC / Mini RC #', lbl_work_start_inv: 'Date Work Started',
    lbl_work_end_inv: 'Date Work Completed',
    sep_description: 'Description of Work Done (up to 6 rows)',
    sep_materials: 'Materials & Quantities',
    mat_th_desc: 'Material Description', mat_th_qty: 'Qty',
    sep_amounts: 'Amounts',
    lbl_bid: 'Bid Amount ($)', lbl_total: 'Total Charge ($)',
    callout_nowork: 'For No Work services: "NO WORK DONE" is auto-set as material and the Service Charge is used as the invoice amount. You can skip the materials table.',
    // Notary tab
    sep_notary_date: 'Sworn Date',
    lbl_day: 'Day', lbl_month: 'Month', lbl_year: 'Year',
    callout_notary: 'Notary Public: Rajinder Singh (pre-printed in PDF). Manual signature + stamp required on the printed document.',
    // Actions
    cancel: 'Cancel', save: 'Save Service',
    action_mark_work: 'Work Done',
    action_mark_nowork: 'No Work',
    action_submit: 'Submit to HPD',
    action_paid: 'Mark Paid',
    // Validation errors
    err_omo_required: 'OMO Number is required',
    err_county_required: 'County is required',
    err_address_required: 'Building address is required',
    err_dates_required: 'Work start and end dates are required',
    // Form labels new
    sep_contractor: 'Contractor',
    lbl_contractor_work: 'Contractor Name',
    hint_72h: '(must be 72h apart)',
    warn_72h: '⚠️ Attempts must be at least 72 hours apart (HPD requirement)',
    warn_dates: '⚠️ Required to generate the affidavit PDF',
    lbl_signer_name: 'Signer / Printed Name',
    hint_signer: '(appears on affidavit signature line)',
    action_aff: 'Print Affidavit', action_inv: 'Print Invoice', action_zip: 'Download All',
    action_edit: 'Edit', action_del: 'Delete',
    // Toast
    toast_saved: 'Service saved successfully',
    toast_deleted: 'Service deleted',
    toast_status: 'Status updated',
    toast_error: 'Something went wrong. Please try again.',
    // Confirm
    confirm_delete: 'Delete this service? This action cannot be undone.',
    // Sidebar
    nav_omos: 'OMOs', nav_users: 'Users', nav_batch: 'Batch',
    // Pages
    page_omos_title: 'Open Market Orders', page_omos_sub: 'Manage HPD service records',
    page_users_title: 'User Management', page_users_sub: 'Create and manage system accounts',
    page_batch_title: 'Batch Download', page_batch_sub: 'Download all documents organized by batch as a ZIP',
    btn_new_user: '＋ New User',
    // User form
    form_new_account: 'New Account',
    lbl_username: 'Username', lbl_fullname: 'Full Name', lbl_password: 'Password', lbl_role: 'Role',
    ph_username: 'e.g. javier', ph_fullname: 'Full name', ph_password: 'Password',
    role_worker: 'Worker — Mark work, upload media',
    role_notary: 'Notary — Download PDFs only',
    role_admin: 'Admin — Full access',
    btn_create_user: 'Create User',
    // Batch
    batch_select_title: 'Select Batch',
    batch_select_desc: 'Choose a batch to download all its Affidavits, Invoices, and media files as a single ZIP.',
    batch_all: '— All records —',
    batch_dl_btn: '📥 Download ZIP',
    batch_callout: 'ZIP structure: BatchName / OMO# / Affidavit + Invoice + media/',
    // Media modal
    media_title: '📷 Media',
    media_sub: 'Photos and videos for this OMO',
    media_camera: 'Camera', media_video: 'Video', media_gallery: 'Gallery / Files',
    // Context menu
    ctx_affidavit: 'Affidavit PDF', ctx_invoice: 'Invoice PDF', ctx_zip: 'Download All (ZIP)',
    // Import PDF
    import_pdf_btn: '📄 Import HPD PDF',
  },
  es: {
    app_title: 'Gestor de Servicios HPD',
    new_btn: 'Nueva OMO',
    pipe_all: 'Todos', pipe_pending: 'Pendiente', pipe_work: 'Trabajo Hecho',
    pipe_nowork: 'Sin Trabajo', pipe_submitted: 'Enviado', pipe_paid: 'Pagado',
    search_ph: 'Buscar OMO#, dirección, condado…',
    filter_all: 'Todos los tipos', filter_work: 'Trabajo Realizado', filter_nowork: 'Sin Trabajo',
    empty_title: 'No se encontraron servicios',
    empty_sub: 'Creá una nueva OMO o ajustá los filtros.',
    modal_new: 'Nueva Orden OMO',
    modal_edit: 'Editar Servicio',
    modal_sub_new: 'Completá los datos de esta Orden de Mercado Abierto',
    modal_sub_edit: 'Actualizá la información del servicio',
    step_job: 'Trabajo', step_outcome: 'Resultado', step_invoice: 'Factura', step_notary: 'Notario',
    lbl_omo: 'Número OMO', lbl_status: 'Estado actual',
    lbl_address: 'Dirección del edificio', lbl_apt: 'Ubicación / Apt',
    lbl_county: 'Condado', lbl_borough: 'Barrio',
    lbl_trade: 'Oficio / Tipo de trabajo', lbl_date_directed: 'Fecha dirigido por HPD',
    opt_county_0: '— Seleccioná el condado —',
    opt_county_kings: 'Kings (Brooklyn)', opt_county_ny: 'New York (Manhattan)',
    opt_county_bronx: 'Bronx', opt_county_queens: 'Queens', opt_county_richmond: 'Richmond (S.I.)',
    opt_borough_0: '— Auto desde condado —',
    doctype_work_label: 'Trabajo Realizado',
    doctype_work_desc: 'El contratista realizó las reparaciones',
    doctype_nowork_label: 'Sin Trabajo',
    doctype_nowork_desc: 'El contratista no pudo realizar el trabajo',
    sep_work_type: 'Tipo de trabajo (Responder 6, 7 u 8)',
    sep_work_dates: 'Fechas del trabajo',
    lbl_work_start: 'Fecha inicio', lbl_work_end: 'Fecha fin',
    wt_all: '6 · TODO el trabajo completado',
    wt_partial: '7 · Trabajo PARCIAL',
    wt_interrupted: '8 · INTERRUMPIDO por el dueño',
    lbl_partial_reason: 'Razón del trabajo parcial',
    lbl_partial_amount: 'Monto parcial ($)',
    lbl_interrupted_amount: 'Monto por trabajo realizado ($)',
    sep_prevented: 'Persona que impidió el trabajo (Pág. 2)',
    lbl_prev_name: 'Nombre', lbl_prev_rel: 'Relación con el edificio', lbl_prev_desc: 'Descripción física',
    lbl_service_charge: 'Cargo de servicio ($)',
    sep_nowork_reason: 'Razón — Responder 4, 5, 6 o 7',
    nr_4: '4 · Físicamente inaccesible',
    nr_5: '5 · Trabajo ya hecho por otros',
    nr_6: '6 · Trabajo siendo hecho por otros',
    nr_7: '7 · Acceso denegado',
    lbl_inacc_reason: 'Describir inaccesibilidad',
    lbl_attempt1: 'Intento de acceso 1 (≥72h de diferencia)',
    lbl_attempt2: 'Intento de acceso 2',
    lbl_phone1: 'Intento telefónico 1',
    lbl_phone2: 'Intento telefónico 2',
    lbl_arrival: 'Fecha de llegada al sitio',
    lbl_contractor: 'Nombre del contratista (quien trabajaba)',
    lbl_ind_name: 'Nombre del individuo',
    lbl_ind_rel: 'Relación con el edificio',
    lbl_ind_desc: 'Descripción física',
    lbl_ind_phone: 'Número de teléfono',
    lbl_invoice_num: 'N° Factura', lbl_invoice_date: 'Fecha de factura',
    lbl_rc: 'RC / Mini RC #', lbl_work_start_inv: 'Fecha inicio del trabajo',
    lbl_work_end_inv: 'Fecha fin del trabajo',
    sep_description: 'Descripción del trabajo (hasta 6 líneas)',
    sep_materials: 'Materiales y Cantidades',
    mat_th_desc: 'Descripción del material', mat_th_qty: 'Cant.',
    sep_amounts: 'Montos',
    lbl_bid: 'Monto ofertado ($)', lbl_total: 'Cargo total ($)',
    callout_nowork: 'Para servicios sin trabajo: "NO WORK DONE" se pone automático como material y el Cargo de Servicio se usa como monto.',
    sep_notary_date: 'Fecha de juramento',
    lbl_day: 'Día', lbl_month: 'Mes', lbl_year: 'Año',
    callout_notary: 'Notario Público: Rajinder Singh (pre-impreso en el PDF). La firma y el sello deben agregarse a mano.',
    cancel: 'Cancelar', save: 'Guardar Servicio',
    action_mark_work: 'Trabajo Hecho',
    action_mark_nowork: 'Sin Trabajo',
    action_submit: 'Enviar a HPD',
    action_paid: 'Marcar Pagado',
    // Validation errors
    err_omo_required: 'El número OMO es obligatorio',
    err_county_required: 'El condado es obligatorio',
    err_address_required: 'La dirección del edificio es obligatoria',
    err_dates_required: 'Las fechas de inicio y fin del trabajo son obligatorias',
    // Form labels new
    sep_contractor: 'Contratista',
    lbl_contractor_work: 'Nombre del Contratista',
    hint_72h: '(deben ser 72h de diferencia)',
    warn_72h: '⚠️ Los intentos deben tener al menos 72 horas de diferencia (requerimiento HPD)',
    warn_dates: '⚠️ Requerido para generar el PDF del affidavit',
    lbl_signer_name: 'Firmante / Nombre impreso',
    hint_signer: '(aparece en la línea de firma del affidavit)',
    action_aff: 'Imprimir Affidavit', action_inv: 'Imprimir Factura', action_zip: 'Descargar Todo',
    action_edit: 'Editar', action_del: 'Eliminar',
    toast_saved: 'Servicio guardado correctamente',
    toast_deleted: 'Servicio eliminado',
    toast_status: 'Estado actualizado',
    toast_error: 'Algo salió mal. Intentá de nuevo.',
    confirm_delete: '¿Eliminar este servicio? Esta acción no se puede deshacer.',
    // Sidebar
    nav_omos: 'OMOs', nav_users: 'Usuarios', nav_batch: 'Lote',
    // Pages
    page_omos_title: 'Órdenes de Mercado Abierto', page_omos_sub: 'Gestión de registros de servicios HPD',
    page_users_title: 'Gestión de Usuarios', page_users_sub: 'Crear y administrar cuentas del sistema',
    page_batch_title: 'Descarga por Lote', page_batch_sub: 'Descargá todos los documentos organizados por lote en un ZIP',
    btn_new_user: '＋ Nuevo Usuario',
    // User form
    form_new_account: 'Nueva Cuenta',
    lbl_username: 'Usuario', lbl_fullname: 'Nombre completo', lbl_password: 'Contraseña', lbl_role: 'Rol',
    ph_username: 'ej. javier', ph_fullname: 'Nombre completo', ph_password: 'Contraseña',
    role_worker: 'Worker — Marcar trabajo, subir fotos',
    role_notary: 'Notario — Solo descargar PDFs',
    role_admin: 'Admin — Acceso completo',
    btn_create_user: 'Crear Usuario',
    // Batch
    batch_select_title: 'Seleccionar Lote',
    batch_select_desc: 'Elegí un lote para descargar todos sus Affidavits, Facturas y archivos multimedia en un solo ZIP.',
    batch_all: '— Todos los registros —',
    batch_dl_btn: '📥 Descargar ZIP',
    batch_callout: 'Estructura ZIP: NombreLote / OMO# / Affidavit + Factura + media/',
    // Media modal
    media_title: '📷 Multimedia',
    media_sub: 'Fotos y videos de esta OMO',
    media_camera: 'Cámara', media_video: 'Video', media_gallery: 'Galería / Archivos',
    // Context menu
    ctx_affidavit: 'PDF Affidavit', ctx_invoice: 'PDF Factura', ctx_zip: 'Descargar Todo (ZIP)',
    // Import PDF
    import_pdf_btn: '📄 Importar PDF de HPD',
  },
};

const STATUS_META = {
  pending:           { icon: '⏳', badge: 'badge-pending',      pipe_key: 'pipe_pending' },
  work_performed:    { icon: '✅', badge: 'badge-work_performed', pipe_key: 'pipe_work' },
  no_work_performed: { icon: '🚫', badge: 'badge-no_work_performed', pipe_key: 'pipe_nowork' },
  submitted:         { icon: '📤', badge: 'badge-submitted',     pipe_key: 'pipe_submitted' },
  paid:              { icon: '💰', badge: 'badge-paid',          pipe_key: 'pipe_paid' },
};

const COUNTY_BOROUGH = {
  Kings: 'Brooklyn', 'New York': 'Manhattan',
  Bronx: 'Bronx', Queens: 'Queens', Richmond: 'Staten Island',
};

// ── State ──────────────────────────────────────────────────────────────────────
let lang         = localStorage.getItem('hpd_lang') || 'en';
let services     = [];
let editId       = null;
let docType      = 'work';
let workType     = 'ALL';
let noworkReason = '';
let statusFilter = 'all';
let currentUser  = null;   // { id, username, role, full_name }
let mediaRecordId = null;

// ── Helpers ────────────────────────────────────────────────────────────────────
const t   = key => (LANG[lang][key] ?? key);
const $   = id  => document.getElementById(id);
const val = id  => ($( id)?.value ?? '');
const set = (id, v) => { if ($(id)) $(id).value = v ?? ''; };

function esc(str) {
  const d = document.createElement('div');
  d.textContent = str ?? '';
  return d.innerHTML;
}

// ── Language ───────────────────────────────────────────────────────────────────
function setLang(l) {
  lang = l;
  localStorage.setItem('hpd_lang', l);
  document.documentElement.lang = l;
  $('btnEN').classList.toggle('active', l === 'en');
  $('btnES').classList.toggle('active', l === 'es');
  // Traducir textContent
  document.querySelectorAll('[data-t]').forEach(el => {
    const k = el.dataset.t;
    if (LANG[l][k] != null) el.textContent = LANG[l][k];
  });
  // Traducir placeholders
  document.querySelectorAll('[data-ph]').forEach(el => {
    const k = el.dataset.ph;
    if (LANG[l][k] != null) el.placeholder = LANG[l][k];
  });
  $('searchInput').placeholder = t('search_ph');
  renderAll();
}

// ── Pipeline filter ────────────────────────────────────────────────────────────
function setStatusFilter(s) {
  statusFilter = s;
  document.querySelectorAll('.ps-node').forEach(c => {
    c.classList.toggle('active-filter', c.dataset.s === s);
  });
  renderAll();
}

// ── Modal: tabs ────────────────────────────────────────────────────────────────
let currentTab = 0;

function goTab(i) {
  currentTab = i;
  // Step items visibles (excluye los ocultos por admin-only)
  const steps = [...document.querySelectorAll('.step-item')].filter(el => el.style.display !== 'none');
  steps.forEach((el, j) => {
    el.classList.toggle('active', j === i);
    el.classList.toggle('done', j < i);
  });
  document.querySelectorAll('.tab-content').forEach((el, j) => {
    el.classList.toggle('active', j === i);
  });
  $('footerTabInfo').textContent = `${i + 1} / ${steps.length}`;
}

// ── Doc type ───────────────────────────────────────────────────────────────────
function setDocType(type) {
  docType = type;
  const isWork = type === 'work';

  $('dtWork').className  = 'doctype-opt' + (isWork   ? ' active-work' : '');
  $('dtNoWork').className = 'doctype-opt' + (!isWork ? ' active-nowork' : '');

  $('workSection').style.display   = isWork   ? 'contents' : 'none';
  $('noworkSection').style.display = !isWork  ? 'contents' : 'none';
  $('calloutNoWork').style.display = !isWork  ? 'flex'     : 'none';

  // Sync status selector
  const st = val('status');
  if (isWork  && st === 'no_work_performed') set('status', 'work_performed');
  if (!isWork && st === 'work_performed')    set('status', 'no_work_performed');
}

function setWorkType(wt) {
  workType = wt;
  ['ALL', 'PARTIAL', 'INTERRUPTED'].forEach(k => {
    $('wt_' + k).className = 'reason-pill' + (k === wt ? ' active-work' : '');
  });
  $('wBlock_PARTIAL').classList.toggle('visible', wt === 'PARTIAL');
  $('wBlock_INTERRUPTED').classList.toggle('visible', wt === 'INTERRUPTED');
}

// ── Warning fechas obligatorias para work_performed ────────────────────────
function checkDatesWarning() {
  const warn = $('warnDates');
  if (!warn) return;
  const missing = !val('work_start_date').trim() || !val('work_end_date').trim();
  warn.style.display = (docType === 'work' && missing) ? '' : 'none';
}

// ── Validación 72h entre intentos de acceso (razón 4) ────────────────────────
function check72h() {
  const d1 = new Date(val('attempt_date1'));
  const d2 = new Date(val('attempt_date2'));
  const warn = $('warn72h');
  if (!warn) return;
  if (!isNaN(d1) && !isNaN(d2) && Math.abs(d2 - d1) < 72 * 60 * 60 * 1000) {
    warn.style.display = '';
  } else {
    warn.style.display = 'none';
  }
}

function setNoWorkReason(r) {
  noworkReason = r;
  ['4', '5', '6', '7'].forEach(k => {
    $('nr_' + k).className = 'reason-pill' + (k === r ? ' active-nowork' : '');
    $('nwBlock_' + k).classList.toggle('visible', k === r);
  });
}

// ── Auto borough ───────────────────────────────────────────────────────────────
function autoBoroughFromCounty() {
  const b = COUNTY_BOROUGH[val('county')] || '';
  if (b) set('borough', b);
}

// ── Modal open/close ───────────────────────────────────────────────────────────
const FORM_FIELDS = [
  'omo_number', 'status', 'county', 'building_address', 'date_directed',
  'work_location_apt', 'trade', 'borough',
  'work_start_date', 'work_end_date',
  'work_contractor_name', 'signer_name',
  'partial_reason', 'partial_amount',
  'interrupted_amount', 'prevented_name', 'prevented_rel', 'prevented_desc',
  'service_charge', 'inacc_reason',
  'attempt_date1', 'attempt_date2', 'phone_date1', 'phone_date2',
  'arrival_date_4', 'arrival_date_5', 'arrival_date_6', 'arrival_date_7',
  'contractor_name',
  'individual_name', 'individual_rel', 'individual_desc', 'individual_phone',
  'invoice_number', 'invoice_date', 'rc_number',
  'work_start_date_inv', 'work_end_date_inv',
  'inv_desc1', 'inv_desc2', 'inv_desc3', 'inv_desc4', 'inv_desc5', 'inv_desc6',
  'inv_mat1', 'inv_mat2', 'inv_mat3', 'inv_mat4', 'inv_mat5', 'inv_mat6',
  'inv_qty1', 'inv_qty2', 'inv_qty3', 'inv_qty4', 'inv_qty5', 'inv_qty6',
  'bid_amount', 'total_charge',
  'sworn_day', 'sworn_month', 'sworn_year',
];

function openModal(rec = null) {
  editId = rec?.id ?? null;

  $('modalTitle').textContent = t(rec ? 'modal_edit' : 'modal_new');
  $('modalSub').textContent   = t(rec ? 'modal_sub_edit' : 'modal_sub_new');

  // Reset all fields (except signer_name which is hardcoded)
  FORM_FIELDS.forEach(id => { if (id !== 'signer_name') set(id, ''); });

  if (rec) {
    FORM_FIELDS.forEach(id => {
      if (id === 'arrival_date_5' || id === 'arrival_date_6' || id === 'arrival_date_7') {
        set(id, rec.arrival_date);
      } else if (id === 'work_start_date_inv') {
        set(id, rec.work_start_date || rec.date_directed);
      } else if (id === 'work_end_date_inv') {
        set(id, rec.work_end_date);
      } else {
        set(id, rec[id]);
      }
    });
  }

  setDocType(rec?.doc_type ?? 'work');
  setWorkType(rec?.work_type ?? 'ALL');

  noworkReason = rec?.nowork_reason ?? '';
  ['4', '5', '6', '7'].forEach(k => {
    $('nr_' + k).className = 'reason-pill' + (k === noworkReason ? ' active-nowork' : '');
    $('nwBlock_' + k).classList.toggle('visible', k === noworkReason);
  });

  if (!rec) set('status', 'pending');

  goTab(0);
  $('btnSave').disabled = false;
  // Reset import status
  const importSt = $('importStatus');
  if (importSt) { importSt.textContent = ''; importSt.className = 'import-status'; }
  document.querySelectorAll('.autofilled').forEach(el => el.classList.remove('autofilled'));
  $('overlay').classList.add('open');
  document.body.style.overflow = 'hidden';
}

function closeModal() {
  $('overlay').classList.remove('open');
  document.body.style.overflow = '';
}

function overlayClick(e) {
  if (e.target === $('overlay')) closeModal();
}

// ── Save ───────────────────────────────────────────────────────────────────────
async function save() {
  const btn = $('btnSave');
  btn.disabled = true;
  btn.textContent = '…';

  // Validación campos obligatorios
  if (!val('omo_number').trim()) {
    showToast(t('err_omo_required'), 'error');
    btn.disabled = false; btn.textContent = t('save');
    return;
  }
  if (!val('county')) {
    showToast(t('err_county_required'), 'error');
    btn.disabled = false; btn.textContent = t('save');
    return;
  }
  if (!val('building_address').trim()) {
    showToast(t('err_address_required'), 'error');
    btn.disabled = false; btn.textContent = t('save');
    return;
  }
  if (docType === 'work' && val('status') === 'work_performed' && (!val('work_start_date').trim() || !val('work_end_date').trim())) {
    showToast(t('err_dates_required'), 'error');
    btn.disabled = false; btn.textContent = t('save');
    return;
  }

  const arrMap = { '4': 'arrival_date_4', '5': 'arrival_date_5', '6': 'arrival_date_6', '7': 'arrival_date_7' };
  const arrivalVal = arrMap[noworkReason] ? val(arrMap[noworkReason]) : '';

  const data = {
    doc_type: docType,
    status:   val('status') || 'pending',
    omo_number:       val('omo_number'),
    county:           val('county'),
    building_address: val('building_address'),
    date_directed:    val('date_directed'),
    work_location_apt:val('work_location_apt'),
    trade:            val('trade'),
    borough:          val('borough'),
    work_start_date:  val('work_start_date') || val('work_start_date_inv'),
    work_end_date:    val('work_end_date')   || val('work_end_date_inv'),
    // Work fields
    work_type:         docType === 'work' ? workType : '',
    work_contractor_name: docType === 'work' ? val('work_contractor_name') : '',
    signer_name:          val('signer_name'),
    partial_reason:    docType === 'work' && workType === 'PARTIAL'      ? val('partial_reason')     : '',
    partial_amount:    docType === 'work' && workType === 'PARTIAL'      ? val('partial_amount')     : '',
    interrupted_amount:docType === 'work' && workType === 'INTERRUPTED'  ? val('interrupted_amount') : '',
    prevented_name:    docType === 'work' && workType === 'INTERRUPTED'  ? val('prevented_name')     : '',
    prevented_rel:     docType === 'work' && workType === 'INTERRUPTED'  ? val('prevented_rel')      : '',
    prevented_desc:    docType === 'work' && workType === 'INTERRUPTED'  ? val('prevented_desc')     : '',
    // No-work fields
    service_charge:    docType === 'nowork' ? val('service_charge') : '',
    nowork_reason:     docType === 'nowork' ? noworkReason          : '',
    inacc_reason:      noworkReason === '4' ? val('inacc_reason')   : '',
    attempt_date1:     noworkReason === '4' ? val('attempt_date1')  : '',
    attempt_date2:     noworkReason === '4' ? val('attempt_date2')  : '',
    phone_date1:       noworkReason === '4' ? val('phone_date1')    : '',
    phone_date2:       noworkReason === '4' ? val('phone_date2')    : '',
    arrival_date:      arrivalVal,
    contractor_name:   noworkReason === '6' ? val('contractor_name') : '',
    arrival_date_4:    noworkReason === '4' ? val('arrival_date_4')  : '',
    individual_name:   noworkReason === '7' ? val('individual_name') : '',
    individual_rel:    noworkReason === '7' ? val('individual_rel')  : '',
    individual_desc:   noworkReason === '7' ? val('individual_desc') : '',
    individual_phone:  noworkReason === '7' ? val('individual_phone'): '',
    // Invoice
    invoice_number:   val('invoice_number'),
    invoice_date:     val('invoice_date'),
    rc_number:        val('rc_number'),
    inv_desc1: val('inv_desc1'), inv_desc2: val('inv_desc2'),
    inv_desc3: val('inv_desc3'), inv_desc4: val('inv_desc4'),
    inv_desc5: val('inv_desc5'), inv_desc6: val('inv_desc6'),
    inv_mat1: val('inv_mat1'), inv_mat2: val('inv_mat2'),
    inv_mat3: val('inv_mat3'), inv_mat4: val('inv_mat4'),
    inv_mat5: val('inv_mat5'), inv_mat6: val('inv_mat6'),
    inv_qty1: val('inv_qty1'), inv_qty2: val('inv_qty2'),
    inv_qty3: val('inv_qty3'), inv_qty4: val('inv_qty4'),
    inv_qty5: val('inv_qty5'), inv_qty6: val('inv_qty6'),
    bid_amount:   val('bid_amount'),
    total_charge: val('total_charge'),
    // sworn_day/month/year: los completa la notaria a mano — no se envían desde el sistema
  };

  try {
    const url    = editId ? `/api/records/${editId}` : '/api/records';
    const method = editId ? 'PUT' : 'POST';
    const res    = await fetch(url, {
      method,
      headers: { 'Content-Type': 'application/json' },
      body:    JSON.stringify(data),
    });
    if (!res.ok) throw new Error();
    showToast(t('toast_saved'), 'success');
    closeModal();
    await loadServices();
  } catch {
    showToast(t('toast_error'), 'error');
  } finally {
    btn.disabled = false;
    btn.textContent = t('save');
  }
}

// ── Delete ─────────────────────────────────────────────────────────────────────
async function deleteService(id) {
  if (!confirm(t('confirm_delete'))) return;
  await fetch(`/api/records/${id}`, { method: 'DELETE' });
  showToast(t('toast_deleted'), 'info');
  await loadServices();
}

// ── Status transition ─────────────────────────────────────────────────────────
function openModalForStatus(id, docTypeOverride) {
  const rec = services.find(r => r.id === id);
  if (!rec) return;
  const recCopy = Object.assign({}, rec, { doc_type: docTypeOverride });
  openModal(recCopy);
  // Pre-set status and go directly to Outcome tab (tab index 1)
  if (docTypeOverride === 'work') set('status', 'work_performed');
  if (docTypeOverride === 'nowork') set('status', 'no_work_performed');
  goTab(1);
}

async function setStatus(id, status) {
  const res = await fetch(`/api/records/${id}/status`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ status }),
  });
  if (res.ok) {
    showToast(t('toast_status'), 'success');
    await loadServices();
  } else {
    showToast(t('toast_error'), 'error');
  }
}

// ── Download ───────────────────────────────────────────────────────────────────
async function dlPdf(id, doc) {
  showToast('Generating…', 'info');
  try {
    const res = await fetch(`/api/records/${id}/pdf/${doc}`, { credentials: 'same-origin' });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      showToast(err.error || t('toast_error'), 'error');
      return;
    }
    const blob = await res.blob();
    const url  = URL.createObjectURL(blob);
    const cd   = res.headers.get('Content-Disposition') || '';
    const match = cd.match(/filename[^;=\n]*=([^;\n]*)/);
    const name  = match ? match[1].replace(/['"]/g, '').trim() : `${doc}_${id}.${doc === 'zip' ? 'zip' : 'pdf'}`;
    const a = document.createElement('a');
    a.href = url;
    a.download = name;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    showToast('Downloaded ✓', 'success');
  } catch {
    showToast(t('toast_error'), 'error');
  }
}

// ── Role helpers ───────────────────────────────────────────────────────────────
function isAdmin()  { return currentUser?.role === 'admin'; }
function isWorker() { return currentUser?.role === 'worker'; }
function isNotary() { return currentUser?.role === 'notary'; }

function applyRoleUI() {
  const role = currentUser?.role || 'worker';
  document.querySelectorAll('.admin-only').forEach(el => {
    el.style.display = (role === 'admin') ? '' : 'none';
  });
  document.querySelectorAll('.admin-worker-only').forEach(el => {
    el.style.display = (role === 'admin' || role === 'worker') ? '' : 'none';
  });
  document.querySelectorAll('.worker-notary-only').forEach(el => {
    el.style.display = (role !== 'admin') ? '' : 'none';
  });
}

// ── Sidebar page navigation ────────────────────────────────────────────────────
function switchTab(name) {
  document.querySelectorAll('.page-section').forEach(s => s.classList.remove('active'));
  document.querySelectorAll('.snav-item').forEach(b => b.classList.remove('active'));
  const page = $('page-' + name);
  const btn  = $('nav-' + name);
  if (page) page.classList.add('active');
  if (btn)  btn.classList.add('active');
  // Cargar datos según pestaña
  if (name === 'users')  loadUsers();
  if (name === 'batch')  loadBatches();
}

function toggleNewUserForm() {
  const f = $('newUserForm');
  f.style.display = f.style.display === 'none' ? '' : 'none';
}

// ── Load & Render ──────────────────────────────────────────────────────────────
async function loadServices() {
  const res = await fetch('/api/records');
  if (res.status === 401) { window.location.href = '/login'; return; }
  services  = await res.json();
  renderAll();
}

function renderAll() {
  const q    = $('searchInput').value.trim().toLowerCase();
  const type = $('filterType').value;

  // Pipeline counts
  const counts = { all: services.length };
  Object.keys(STATUS_META).forEach(s => { counts[s] = services.filter(r => r.status === s).length; });
  $('pc_all').textContent           = counts.all;
  $('pc_pending').textContent       = counts.pending       ?? 0;
  $('pc_work_performed').textContent= counts.work_performed ?? 0;
  $('pc_no_work').textContent       = counts.no_work_performed ?? 0;
  $('pc_submitted').textContent     = counts.submitted     ?? 0;
  $('pc_paid').textContent          = counts.paid          ?? 0;

  // Filter
  let rows = services;
  if (statusFilter && statusFilter !== 'all') rows = rows.filter(r => r.status === statusFilter);
  if (type)                                   rows = rows.filter(r => r.doc_type === type);
  if (q) rows = rows.filter(r => Object.values(r).some(v => v && String(v).toLowerCase().includes(q)));

  const container = $('servicesContainer');

  if (!rows.length) {
    container.innerHTML = `
      <div class="empty-state">
        <div class="empty-icon">🏗️</div>
        <div class="empty-title">${t('empty_title')}</div>
        <div class="empty-sub">${t('empty_sub')}</div>
      </div>`;
    return;
  }

  const role = currentUser?.role || 'worker';

  container.innerHTML = rows.map((r, idx) => {
    const sm   = STATUS_META[r.status] || STATUS_META.pending;
    const addr = r.building_address || '—';
    const amt  = role === 'admin' && (r.total_charge || r.service_charge)
                 ? `$${r.total_charge || r.service_charge}` : null;
    const date = r.date_directed || r.work_start_date || '—';

    const chips = [
      r.borough ? `<span class="chip">${esc(r.borough)}</span>` : '',
      r.trade   ? `<span class="chip">${esc(r.trade)}</span>`   : '',
      r.work_location_apt ? `<span class="chip">Apt ${esc(r.work_location_apt)}</span>` : '',
      `<span class="chip">${esc(date)}</span>`,
    ].filter(Boolean).join('');

    // ── Workflow primary actions (1-2 big buttons) ──
    const wfBtns = [];
    if (role !== 'notary') {
      if (r.status === 'pending') {
        // Open modal pre-set to work/nowork so user fills form before changing status
        wfBtns.push(`<button class="act-primary act-work" onclick="openModalForStatus(${r.id},'work')">${t('action_mark_work')}</button>`);
        wfBtns.push(`<button class="act-primary act-nowork" onclick="openModalForStatus(${r.id},'nowork')">${t('action_mark_nowork')}</button>`);
      }
      if (role === 'admin') {
        if (r.status === 'work_performed' || r.status === 'no_work_performed')
          wfBtns.push(`<button class="act-primary act-submit" onclick="setStatus(${r.id},'submitted')">${t('action_submit')}</button>`);
        if (r.status === 'submitted')
          wfBtns.push(`<button class="act-primary act-paid" onclick="setStatus(${r.id},'paid')">${t('action_paid')}</button>`);
      }
    }

    // ── Print buttons ─ always visible next to status buttons when not pending ──
    if (r.status && r.status !== 'pending') {
      wfBtns.push(`<button class="act-media-btn" onclick="dlPdf(${r.id},'affidavit')" title="Print Affidavit">📄 ${t('action_aff')}</button>`);
      wfBtns.push(`<button class="act-media-btn" onclick="dlPdf(${r.id},'invoice')" title="Print Invoice">🧾 ${t('action_inv')}</button>`);
    }
    const printBtns = []; // now merged into wfBtns

    const stripeClass = `stripe-${r.status === 'work_performed' ? 'work' : r.status === 'no_work_performed' ? 'nowork' : r.status || 'pending'}`;

    return `
    <div class="service-card entering" data-status="${r.status}" style="animation-delay:${idx * 25}ms">
      <div class="card-main">
        <div class="card-stripe ${stripeClass}"></div>
        <div class="card-omo">${esc(r.omo_number) || '—'}</div>
        <div class="card-info">
          <div class="card-address" title="${esc(addr)}">${esc(addr)}</div>
          <div class="card-chips">${chips}</div>
        </div>
        <div class="card-right">
          <span class="status-badge ${sm.badge}">${sm.icon} ${t(sm.pipe_key)}</span>
          ${amt ? `<div class="card-amount">${amt}</div>` : ''}
        </div>
      </div>
      <div class="card-actions">
        ${wfBtns.join('')}
        <button class="act-media-btn" onclick="openMediaModal(${r.id},'${esc(r.omo_number||r.id)}')">📷 Media</button>
        <button class="act-more-btn" onclick="toggleCtx(event,${r.id})" title="More actions">•••</button>
      </div>
    </div>`;
  }).join('');
}

// ── Context menu (global, body-level) ─────────────────────────────────────────
let _ctxRecordId = null;

function toggleCtx(e, id) {
  e.stopPropagation();
  e.preventDefault();

  // Capture btn reference BEFORE any state changes
  const btn = e.currentTarget || e.target.closest('.act-more-btn');
  const br  = btn.getBoundingClientRect();

  const menu = $('globalCtxMenu');
  const alreadyOpen = menu.classList.contains('open') && _ctxRecordId === id;
  closeCtx();
  if (alreadyOpen) return;

  _ctxRecordId = id;
  const rec = services.find(s => s.id === id);
  if (!rec) return;

  // Label items
  $('ctxAffidavit').querySelector('.ctx-item-label').textContent = t('ctx_affidavit');
  $('ctxInvoice').querySelector('.ctx-item-label').textContent   = t('ctx_invoice');
  $('ctxZip').querySelector('.ctx-item-label').textContent       = t('ctx_zip');
  $('ctxEdit').querySelector('.ctx-item-label').textContent      = t('action_edit');
  $('ctxDelete').querySelector('.ctx-item-label').textContent    = t('action_del');

  // Wire actions
  $('ctxAffidavit').onclick = () => { dlPdf(id, 'affidavit'); closeCtx(); };
  $('ctxInvoice').onclick   = () => { dlPdf(id, 'invoice');   closeCtx(); };
  $('ctxZip').onclick       = () => { dlPdf(id, 'zip');       closeCtx(); };
  $('ctxEdit').onclick      = () => { openModal(rec);          closeCtx(); };
  $('ctxDelete').onclick    = () => { deleteService(id);       closeCtx(); };

  // Show/hide role-gated items
  const role = currentUser?.role;
  document.querySelectorAll('.admin-worker-ctx').forEach(el => {
    el.style.display = (role === 'admin' || role === 'worker') ? '' : 'none';
  });
  document.querySelectorAll('.admin-ctx').forEach(el => {
    el.style.display = (role === 'admin') ? '' : 'none';
  });

  // Position fixed relative to button
  const mw = 210;
  menu.style.position   = 'fixed';
  menu.style.width      = mw + 'px';
  menu.style.left       = Math.min(br.right - mw, window.innerWidth - mw - 8) + 'px';
  menu.style.top        = '-9999px';
  menu.style.bottom     = '';
  menu.style.visibility = 'hidden';
  menu.classList.add('open');

  const mh = menu.offsetHeight;
  menu.style.visibility = '';

  menu.style.top = (br.bottom + mh + 8 > window.innerHeight)
    ? (br.top - mh - 6) + 'px'
    : (br.bottom + 6) + 'px';
}

function closeCtx() {
  const menu = $('globalCtxMenu');
  if (menu) { menu.classList.remove('open'); }
  _ctxRecordId = null;
}

document.addEventListener('click', e => {
  if (!e.target.closest('#globalCtxMenu') && !e.target.closest('.act-more-btn')) closeCtx();
});

// ── Toast ──────────────────────────────────────────────────────────────────────
let toastTimer;
function showToast(msg, type = 'info') {
  const el = $('toast');
  el.textContent = msg;
  el.className   = `show ${type}`;
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => { el.className = ''; }, 3200);
}

// ── Import HPD PDF ─────────────────────────────────────────────────────────────
async function importOmoPdf(input) {
  const file = input.files[0];
  if (!file) return;
  const btn    = document.querySelector('.btn-import-pdf');
  const status = $('importStatus');

  btn.disabled = true;
  status.className = 'import-status spin';
  status.textContent = '⏳ Parsing…';

  const fd = new FormData();
  fd.append('file', file);

  try {
    const res  = await fetch('/api/parse-omo-pdf', { method: 'POST', body: fd });
    const data = await res.json();

    if (!res.ok) {
      status.className = 'import-status err';
      status.textContent = '✗ ' + (data.error || 'Parse failed');
      return;
    }

    // Mapeo de campos retornados por el backend → IDs del formulario
    const MAP = {
      omo_number:       'omo_number',
      building_address: 'building_address',
      work_location_apt:'work_location_apt',
      borough:          'borough',
      county:           'county',
      trade:            'trade',
      date_directed:    'date_directed',
      work_end_date:    'work_end_date',
      rc_number:        'rc_number',
      inv_desc1:        'inv_desc1',
      inv_desc2:        'inv_desc2',
      inv_desc3:        'inv_desc3',
      inv_desc4:        'inv_desc4',
      inv_desc5:        'inv_desc5',
      inv_desc6:        'inv_desc6',
    };

    let filled = 0;
    for (const [key, elId] of Object.entries(MAP)) {
      if (data[key]) {
        const el = $(elId);
        if (el) {
          el.value = data[key];
          el.classList.add('autofilled');
          filled++;
        }
      }
    }

    // Si el county se detectó, forzar autoBoroughFromCounty para sincronizar
    if (data.county) {
      const countyEl = $('county');
      if (countyEl) {
        // county es un <select> — buscar la opción que incluya el valor
        Array.from(countyEl.options).forEach(opt => {
          if (opt.value.toLowerCase().includes(data.county.toLowerCase()) ||
              data.county.toLowerCase().includes(opt.value.toLowerCase())) {
            countyEl.value = opt.value;
            countyEl.classList.add('autofilled');
          }
        });
        autoBoroughFromCounty();
      }
    }

    // Navegar al tab Job Info para que el usuario vea los campos
    goTab(0);

    const unfilled = Object.keys(MAP).length - filled;
    status.className = 'import-status ok';
    status.textContent = `✓ ${filled} fields filled`;
    if (unfilled > 0) status.textContent += ` (${unfilled} not found)`;

    showToast(`OMO PDF imported — ${filled} fields auto-filled`, 'success');
  } catch (e) {
    status.className = 'import-status err';
    status.textContent = '✗ Network error';
    showToast('Failed to parse PDF', 'error');
  } finally {
    btn.disabled = false;
    input.value = '';  // reset so same file can be re-imported
  }
}

// ── Auth ───────────────────────────────────────────────────────────────────────
async function initAuth() {
  try {
    const res = await fetch('/api/auth/me');
    if (!res.ok) { window.location.href = '/login'; return false; }
    currentUser = await res.json();
    // Header user widget
    const name = currentUser.full_name || currentUser.username;
    $('userName').textContent  = name;
    $('userRole').textContent  = currentUser.role;
    $('userAvatar').textContent = name.charAt(0).toUpperCase();
    applyRoleUI();
    return true;
  } catch { window.location.href = '/login'; return false; }
}

async function doLogout() {
  await fetch('/api/auth/logout', { method: 'POST' });
  window.location.href = '/login';
}

// ── Users modal ────────────────────────────────────────────────────────────────
async function openUsersModal() {
  $('usersOverlay').classList.add('open');
  document.body.style.overflow = 'hidden';
  await loadUsers();
  await loadBatches();
}
function closeUsersModal() {
  $('usersOverlay').classList.remove('open');
  document.body.style.overflow = '';
}
function openNewUserForm()  { $('newUserForm').style.display = ''; }
function closeNewUserForm() { $('newUserForm').style.display = 'none'; }

async function loadUsers() {
  const res   = await fetch('/api/users');
  const users = await res.json();
  const list  = $('usersList');
  if (!users.length) { list.innerHTML = '<p style="color:var(--text-3);padding:16px">No users yet.</p>'; return; }
  list.innerHTML = users.map(u => {
    const roleClass = u.active ? `role-${u.role}` : 'role-inactive';
    const roleLabel = u.active ? u.role : 'inactive';
    return `
    <div class="user-row">
      <div class="user-row-avatar">${(u.full_name||u.username).charAt(0).toUpperCase()}</div>
      <div class="user-row-info">
        <div class="user-row-name">${esc(u.full_name||u.username)}</div>
        <div class="user-row-meta">@${esc(u.username)}</div>
      </div>
      <span class="user-row-role ${roleClass}">${roleLabel}</span>
      <div class="user-row-actions">
        <button class="btn-icon" onclick="toggleUserActive(${u.id},${u.active})">${u.active ? '🔒 Disable' : '✅ Enable'}</button>
        <button class="btn-icon danger" onclick="deleteUserRow(${u.id})">🗑</button>
      </div>
    </div>`;
  }).join('');
}

async function createUser() {
  const body = {
    username:  $('nu_username').value.trim(),
    password:  $('nu_password').value,
    role:      $('nu_role').value,
    full_name: $('nu_fullname').value.trim(),
  };
  if (!body.username || !body.password) { showToast(t('toast_error'), 'error'); return; }
  const res = await fetch('/api/users', {
    method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify(body)
  });
  if (res.ok) {
    showToast(t('toast_saved'), 'success');
    toggleNewUserForm();
    $('nu_username').value = $('nu_password').value = $('nu_fullname').value = '';
    await loadUsers();
  } else {
    const e = await res.json();
    showToast(e.error || t('toast_error'), 'error');
  }
}

async function toggleUserActive(uid, active) {
  await fetch(`/api/users/${uid}`, {
    method:'PUT', headers:{'Content-Type':'application/json'},
    body: JSON.stringify({ active: !active })
  });
  await loadUsers();
}

async function deleteUserRow(uid) {
  if (!confirm(t('confirm_delete'))) return;
  await fetch(`/api/users/${uid}`, { method: 'DELETE' });
  await loadUsers();
}

// ── Batch download modal ───────────────────────────────────────────────────────
async function openBatchModal() {
  $('batchOverlay').classList.add('open');
  document.body.style.overflow = 'hidden';
  await loadBatches();
}
function closeBatchModal() {
  $('batchOverlay').classList.remove('open');
  document.body.style.overflow = '';
}

async function loadBatches() {
  const res     = await fetch('/api/batches');
  const batches = await res.json();
  const sel     = $('batchSelect');
  sel.innerHTML = `<option value="">${t('batch_all')}</option>`;
  batches.forEach(b => {
    const opt = document.createElement('option');
    opt.value = b; opt.textContent = b;
    sel.appendChild(opt);
  });
}

async function doBatchDownload() {
  const batch = $('batchSelect').value;
  const btn   = $('btnBatchDl');
  btn.disabled = true;
  btn.textContent = '⏳…';
  try {
    const res = await fetch('/api/batch/download', {
      method: 'POST', headers:{'Content-Type':'application/json'},
      body: JSON.stringify({ batch })
    });
    if (!res.ok) { showToast(t('toast_error'), 'error'); return; }
    const blob = await res.blob();
    const url  = URL.createObjectURL(blob);
    const a    = document.createElement('a');
    a.href = url; a.download = (batch || 'All_Records') + '.zip';
    a.click();
    URL.revokeObjectURL(url);
    showToast(t('toast_saved'), 'success');
  } catch { showToast(t('toast_error'), 'error'); }
  finally { btn.disabled = false; btn.textContent = t('batch_dl_btn'); }
}

// ── Media modal ────────────────────────────────────────────────────────────────
async function openMediaModal(recId, omoNum) {
  mediaRecordId = recId;
  $('mediaModalTitle').textContent = `📷 Media — ${omoNum}`;
  $('mediaOverlay').classList.add('open');
  document.body.style.overflow = 'hidden';
  await loadMedia(recId);

  // Drag & drop
  const zone = $('mediaDropZone');
  if (zone) {
    zone.ondragover = e => { e.preventDefault(); zone.style.borderColor = 'var(--lbj-blue)'; };
    zone.ondragleave = () => { zone.style.borderColor = ''; };
    zone.ondrop = e => { e.preventDefault(); zone.style.borderColor = ''; handleMediaFiles(e.dataTransfer.files); };
  }
}
function closeMediaModal() {
  $('mediaOverlay').classList.remove('open');
  document.body.style.overflow = '';
  mediaRecordId = null;
}

async function loadMedia(recId) {
  const res   = await fetch(`/api/records/${recId}/media`);
  const files = await res.json();
  const grid  = $('mediaGrid');
  if (!files.length) {
    grid.innerHTML = '<p style="color:var(--text-3);font-size:.85rem;padding:8px 0">No media uploaded yet.</p>';
    return;
  }
  grid.innerHTML = files.map(f => {
    const isImg = /\.(jpg|jpeg|png|gif|webp)$/i.test(f.filename);
    const isVid = /\.(mp4|mov|avi)$/i.test(f.filename);
    const url   = `/media/${recId}/${f.filename}`;
    const thumb = isImg
      ? `<img src="${url}" loading="lazy" alt="${esc(f.orig_name||f.filename)}">`
      : `<div class="media-item-icon">${isVid ? '🎥' : '📄'}</div>`;
    const adminDel = isAdmin()
      ? `<button class="media-btn-del" onclick="deleteMedia(${f.id})">🗑</button>` : '';
    return `
    <div class="media-item">
      ${thumb}
      <div class="media-item-overlay">
        <a href="${url}" target="_blank" style="color:#fff;font-size:.8rem;font-weight:600">View</a>
        ${adminDel}
      </div>
      <div class="media-item-name">${esc(f.orig_name||f.filename)}</div>
    </div>`;
  }).join('');
}

async function handleMediaFiles(files) {
  if (!files || !files.length) return;
  for (const file of files) {
    const fd = new FormData();
    fd.append('file', file);
    const res = await fetch(`/api/records/${mediaRecordId}/media`, { method:'POST', body: fd });
    if (!res.ok) { showToast(`Failed: ${file.name}`, 'error'); }
  }
  showToast(t('toast_saved'), 'success');
  await loadMedia(mediaRecordId);
}

async function deleteMedia(mediaId) {
  if (!confirm(t('confirm_delete'))) return;
  await fetch(`/api/media/${mediaId}`, { method: 'DELETE' });
  await loadMedia(mediaRecordId);
}

// ── Init ───────────────────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', async () => {
  const ok = await initAuth();
  if (!ok) return;
  setStatusFilter('all');
  setLang(lang);
  await loadServices();
});
