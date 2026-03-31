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
    action_mark_work: '✅ Mark Work Done',
    action_mark_nowork: '🚫 Mark No Work',
    action_submit: '📤 Submit to HPD',
    action_paid: '💰 Mark Paid',
    action_aff: 'Affidavit', action_inv: 'Invoice', action_zip: 'All Docs',
    action_edit: 'Edit', action_del: 'Delete',
    // Toast
    toast_saved: 'Service saved successfully',
    toast_deleted: 'Service deleted',
    toast_status: 'Status updated',
    toast_error: 'Something went wrong. Please try again.',
    // Confirm
    confirm_delete: 'Delete this service? This action cannot be undone.',
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
    action_mark_work: '✅ Trabajo Hecho',
    action_mark_nowork: '🚫 Sin Trabajo',
    action_submit: '📤 Enviar a HPD',
    action_paid: '💰 Marcar Pagado',
    action_aff: 'Affidavit', action_inv: 'Factura', action_zip: 'Todo (ZIP)',
    action_edit: 'Editar', action_del: 'Eliminar',
    toast_saved: 'Servicio guardado correctamente',
    toast_deleted: 'Servicio eliminado',
    toast_status: 'Estado actualizado',
    toast_error: 'Algo salió mal. Intentá de nuevo.',
    confirm_delete: '¿Eliminar este servicio? Esta acción no se puede deshacer.',
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
  $('btnEN').classList.toggle('active', l === 'en');
  $('btnES').classList.toggle('active', l === 'es');
  document.querySelectorAll('[data-t]').forEach(el => {
    const k = el.dataset.t;
    if (LANG[l][k] != null) el.textContent = LANG[l][k];
  });
  $('searchInput').placeholder = t('search_ph');
  renderAll();
}

// ── Pipeline filter ────────────────────────────────────────────────────────────
function setStatusFilter(s) {
  statusFilter = s;
  document.querySelectorAll('.pipe-card').forEach(c => {
    c.classList.toggle('active-filter', c.dataset.s === s);
  });
  renderAll();
}

// ── Modal: tabs ────────────────────────────────────────────────────────────────
let currentTab = 0;

function goTab(i) {
  currentTab = i;
  document.querySelectorAll('.step-item').forEach((el, j) => {
    el.classList.toggle('active', j === i);
    el.classList.toggle('done', j < i);
  });
  document.querySelectorAll('.tab-content').forEach((el, j) => {
    el.classList.toggle('active', j === i);
  });
  $('footerTabInfo').textContent = `${i + 1} / 4`;
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
  'partial_reason', 'partial_amount',
  'interrupted_amount', 'prevented_name', 'prevented_rel', 'prevented_desc',
  'service_charge', 'inacc_reason',
  'attempt_date1', 'attempt_date2', 'phone_date1', 'phone_date2',
  'contractor_name',
  'individual_name', 'individual_rel', 'individual_desc', 'individual_phone',
  'invoice_number', 'invoice_date', 'rc_number',
  'work_start_date_inv', 'work_end_date_inv',
  'inv_desc1', 'inv_desc2', 'inv_desc3', 'inv_desc4', 'inv_desc5', 'inv_desc6',
  'inv_mat1', 'inv_mat2', 'inv_mat3', 'inv_mat4', 'inv_mat5', 'inv_mat6',
  'inv_qty1', 'inv_qty2', 'inv_qty3', 'inv_qty4', 'inv_qty5', 'inv_qty6',
  'bid_amount', 'total_charge',
  'sworn_day', 'sworn_month', 'sworn_year',
  'arrival_date_5', 'arrival_date_6', 'arrival_date_7',
];

function openModal(rec = null) {
  editId = rec?.id ?? null;

  $('modalTitle').textContent = t(rec ? 'modal_edit' : 'modal_new');
  $('modalSub').textContent   = t(rec ? 'modal_sub_edit' : 'modal_sub_new');

  // Reset all fields
  FORM_FIELDS.forEach(id => set(id, ''));

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

  const arrMap = { '4': 'arrival_date_5', '5': 'arrival_date_5', '6': 'arrival_date_6', '7': 'arrival_date_7' };
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
    // Notary
    sworn_day:   val('sworn_day'),
    sworn_month: val('sworn_month'),
    sworn_year:  val('sworn_year'),
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
function dlPdf(id, doc) {
  window.open(`/api/records/${id}/pdf/${doc}`, '_blank');
}

// ── Load & Render ──────────────────────────────────────────────────────────────
async function loadServices() {
  const res = await fetch('/api/records');
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

  container.innerHTML = rows.map((r, idx) => {
    const sm    = STATUS_META[r.status] || STATUS_META.pending;
    const label = t(sm.pipe_key);
    const date  = r.date_directed || r.work_start_date || r.invoice_date || '—';
    const addr  = r.building_address || '—';
    const amt   = r.total_charge   ? `$${r.total_charge}`
                : r.service_charge ? `$${r.service_charge}`
                : null;

    // Chips
    const chips = [
      r.county   ? `<span class="meta-chip">📍 ${esc(r.county)}</span>` : '',
      r.trade    ? `<span class="meta-chip">🔧 ${esc(r.trade)}</span>`  : '',
      r.invoice_number ? `<span class="meta-chip">🧾 #${esc(r.invoice_number)}</span>` : '',
    ].filter(Boolean).join('');

    // Context actions
    const actions = [];
    if (r.status === 'pending') {
      actions.push(`<button class="act-btn act-work" onclick="setStatus(${r.id},'work_performed')">${t('action_mark_work')}</button>`);
      actions.push(`<button class="act-btn act-nowork" onclick="setStatus(${r.id},'no_work_performed')">${t('action_mark_nowork')}</button>`);
    }
    if (r.status === 'work_performed' || r.status === 'no_work_performed') {
      actions.push(`<button class="act-btn act-dl" onclick="dlPdf(${r.id},'affidavit')" title="${t('action_aff')}">📋 ${t('action_aff')}</button>`);
      actions.push(`<button class="act-btn act-dl" onclick="dlPdf(${r.id},'invoice')"   title="${t('action_inv')}">🧾 ${t('action_inv')}</button>`);
      actions.push(`<button class="act-btn act-zip" onclick="dlPdf(${r.id},'zip')"      title="${t('action_zip')}">📦 ${t('action_zip')}</button>`);
      actions.push(`<button class="act-btn act-submit" onclick="setStatus(${r.id},'submitted')">${t('action_submit')}</button>`);
    }
    if (r.status === 'submitted') {
      actions.push(`<button class="act-btn act-dl"  onclick="dlPdf(${r.id},'affidavit')">📋 ${t('action_aff')}</button>`);
      actions.push(`<button class="act-btn act-dl"  onclick="dlPdf(${r.id},'invoice')}">🧾 ${t('action_inv')}</button>`);
      actions.push(`<button class="act-btn act-paid" onclick="setStatus(${r.id},'paid')">${t('action_paid')}</button>`);
    }
    if (r.status === 'paid') {
      actions.push(`<button class="act-btn act-zip" onclick="dlPdf(${r.id},'zip')">📦 ${t('action_zip')}</button>`);
    }
    actions.push(`<button class="act-btn act-edit" onclick="openModal(${JSON.stringify(r).replace(/"/g,'&quot;')})">${t('action_edit')}</button>`);
    actions.push(`<button class="act-btn act-danger" onclick="deleteService(${r.id})">${t('action_del')}</button>`);

    return `
    <div class="service-card entering" data-status="${r.status}" style="animation-delay:${idx * 30}ms">
      <div class="card-left">
        <span class="omo-num">${esc(r.omo_number) || '—'}</span>
        <div class="omo-date">${esc(date)}</div>
      </div>
      <div class="card-mid">
        <div class="card-address" title="${esc(addr)}">${esc(addr)}</div>
        <div class="card-meta">${chips}</div>
      </div>
      <div class="card-right">
        <div>
          <span class="status-badge ${sm.badge}">${sm.icon} ${label}</span>
        </div>
        <div class="${amt ? 'card-amount' : 'card-amount no-amount'}">${amt ?? '—'}</div>
        <div class="card-actions">${actions.join('')}</div>
      </div>
    </div>`;
  }).join('');
}

// ── Toast ──────────────────────────────────────────────────────────────────────
let toastTimer;
function showToast(msg, type = 'info') {
  const el = $('toast');
  el.textContent = msg;
  el.className   = `show ${type}`;
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => { el.className = ''; }, 3200);
}

// ── Init ───────────────────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  setStatusFilter('all');
  setLang(lang);
  loadServices();
});
