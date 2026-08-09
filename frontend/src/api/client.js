/**
 * Panggilan API relatif ke origin (Nginx / Vite proxy → /api/v1).
 */
export async function apiFetch(path, options = {}) {
  const url = path.startsWith('/') ? `/api/v1${path}` : `/api/v1/${path}`
  const isForm = typeof FormData !== 'undefined' && options.body instanceof FormData
  const token = typeof localStorage !== 'undefined' ? localStorage.getItem('auth_token') : null
  const authHeader = token ? { Authorization: `Bearer ${token}` } : {}
  const r = await fetch(url, {
    ...options,
    headers: isForm
      ? { ...authHeader, ...options.headers }
      : { 'Content-Type': 'application/json', ...authHeader, ...options.headers },
  })
  if (!r.ok) {
    const text = await r.text()
    throw new Error(text || r.statusText)
  }
  if (r.status === 204) return null
  const ct = r.headers.get('content-type') || ''
  if (ct.includes('application/json')) return r.json()
  return r.text()
}

/**
 * GET file dokumen dengan Bearer (HTML/PDF/Excel). Tab baru lewat window.open tidak mengirim token.
 * @param {string} apiPath path setelah /api/v1, mis. `/documents/surat-jalan/12` atau `.../12/pdf`
 * @param {{ mode?: 'open'|'download', downloadFallbackName?: string }} opts
 */
export async function fetchAuthenticatedDocument(apiPath, opts = {}) {
  const { mode = 'open', downloadFallbackName = 'download' } = opts
  const path = apiPath.startsWith('/') ? apiPath : `/${apiPath}`
  const url = `/api/v1${path}`
  const token = typeof localStorage !== 'undefined' ? localStorage.getItem('auth_token') : null
  const r = await fetch(url, {
    headers: token ? { Authorization: `Bearer ${token}` } : {},
  })
  if (!r.ok) {
    const text = await r.text()
    let msg = text || r.statusText
    try {
      const j = JSON.parse(text)
      if (j?.detail != null) {
        msg = typeof j.detail === 'string' ? j.detail : JSON.stringify(j.detail)
      }
    } catch {
      /* gunakan text mentah */
    }
    throw new Error(msg)
  }
  const blob = await r.blob()
  const blobUrl = URL.createObjectURL(blob)
  if (mode === 'open') {
    const w = window.open(blobUrl, '_blank', 'noopener,noreferrer')
    if (!w) {
      URL.revokeObjectURL(blobUrl)
      throw new Error(
        'Pop-up diblokir browser — izinkan pop-up untuk situs ini agar dokumen terbuka di tab baru.',
      )
    }
    setTimeout(() => URL.revokeObjectURL(blobUrl), 120_000)
    return
  }
  const dispo = r.headers.get('content-disposition') || ''
  const m = dispo.match(/filename="?([^";]+)"?/i)
  const name = m ? m[1] : downloadFallbackName
  const a = document.createElement('a')
  a.href = blobUrl
  a.download = name
  a.click()
  URL.revokeObjectURL(blobUrl)
}

// --- Auth ---
export function login(username, password) {
  return apiFetch('/auth/login', { method: 'POST', body: JSON.stringify({ username, password }) })
}

export function me() {
  return apiFetch('/auth/me')
}

// --- Notifications ---
export function listNotifications(params = {}) {
  const q = new URLSearchParams()
  if (params.unread_only) q.set('unread_only', 'true')
  if (params.limit != null) q.set('limit', String(params.limit))
  if (params.offset != null) q.set('offset', String(params.offset))
  const suffix = q.toString() ? `?${q}` : ''
  return apiFetch(`/notifications${suffix}`)
}

export function unreadNotificationsCount() {
  return apiFetch('/notifications/unread-count')
}

export function markNotificationRead(id) {
  return apiFetch(`/notifications/${id}/read`, { method: 'POST' })
}

export function markAllNotificationsRead() {
  return apiFetch('/notifications/read-all', { method: 'POST' })
}

export function listUsers() {
  return apiFetch('/auth/users')
}

export function createUser(body) {
  return apiFetch('/auth/users', { method: 'POST', body: JSON.stringify(body) })
}

export function updateUser(id, body) {
  return apiFetch(`/auth/users/${id}`, { method: 'PUT', body: JSON.stringify(body) })
}

export function getPermissionMatrix() {
  return apiFetch('/permissions/matrix')
}

export function savePermissionMatrix(matrix) {
  return apiFetch('/permissions/matrix', { method: 'PUT', body: JSON.stringify({ matrix }) })
}

export function listAuditLogs(params = {}) {
  const q = new URLSearchParams()
  if (params.entity_type) q.set('entity_type', params.entity_type)
  if (params.entity_id != null) q.set('entity_id', String(params.entity_id))
  if (params.limit != null) q.set('limit', String(params.limit))
  const suffix = q.toString() ? `?${q}` : ''
  return apiFetch(`/audit/logs${suffix}`)
}

/** Date dari el-date-picker / string → 'YYYY-MM-DD' untuk body JSON */
export function toIsoDate(val) {
  if (val == null || val === '') return null
  if (typeof val === 'string') return val.slice(0, 10)
  const d = new Date(val)
  if (Number.isNaN(d.getTime())) return null
  return d.toISOString().slice(0, 10)
}

export function dashboardSummary() {
  return apiFetch('/dashboard/summary')
}

export function listExchangeRates() {
  return apiFetch('/exchange-rates')
}

export function createExchangeRate(body) {
  return apiFetch('/exchange-rates', { method: 'POST', body: JSON.stringify(body) })
}

// --- Customers ---
export function listCustomers() {
  return apiFetch('/customers')
}

export function listCustomersPage(params = {}) {
  const q = new URLSearchParams()
  if (params.q != null && String(params.q).trim()) q.set('q', String(params.q).trim())
  if (params.is_export_customer != null) q.set('is_export_customer', String(Boolean(params.is_export_customer)))
  if (params.limit != null) q.set('limit', String(params.limit))
  if (params.offset != null) q.set('offset', String(params.offset))
  const suffix = q.toString() ? `?${q}` : ''
  return apiFetch(`/customers/page${suffix}`)
}

export function getCustomer(id) {
  return apiFetch(`/customers/${id}`)
}

export function createCustomer(body) {
  return apiFetch('/customers', { method: 'POST', body: JSON.stringify(body) })
}

export function updateCustomer(id, body) {
  return apiFetch(`/customers/${id}`, { method: 'PUT', body: JSON.stringify(body) })
}

export function deleteCustomer(id) {
  return apiFetch(`/customers/${id}`, { method: 'DELETE' })
}

export function listQuotations(params = {}) {
  const q = new URLSearchParams()
  if (params.q != null && String(params.q).trim()) q.set('q', String(params.q).trim())
  if (params.customer_id != null && params.customer_id !== '') q.set('customer_id', String(params.customer_id))
  if (params.status != null && String(params.status).trim()) q.set('status', String(params.status).trim())
  if (params.date_from) q.set('date_from', params.date_from)
  if (params.date_to) q.set('date_to', params.date_to)
  if (params.limit != null) q.set('limit', String(params.limit))
  if (params.offset != null) q.set('offset', String(params.offset))
  const suffix = q.toString() ? `?${q}` : ''
  return apiFetch(`/quotations${suffix}`)
}

export function getQuotation(id) {
  return apiFetch(`/quotations/${id}`)
}

export function createQuotation(body) {
  return apiFetch('/quotations', { method: 'POST', body: JSON.stringify(body) })
}

export function updateQuotation(id, body) {
  return apiFetch(`/quotations/${id}`, { method: 'PUT', body: JSON.stringify(body) })
}

export function deleteQuotation(id) {
  return apiFetch(`/quotations/${id}`, { method: 'DELETE' })
}

export function addQuotationLine(quotationId, body) {
  return apiFetch(`/quotations/${quotationId}/lines`, { method: 'POST', body: JSON.stringify(body) })
}

export function updateQuotationLine(lineId, body) {
  return apiFetch(`/quotation-lines/${lineId}`, { method: 'PUT', body: JSON.stringify(body) })
}

export function deleteQuotationLine(lineId) {
  return apiFetch(`/quotation-lines/${lineId}`, { method: 'DELETE' })
}

/** Data wilayah Indonesia: provinsi → kab/kota → kecamatan → kelurahan/desa */
export function wilayahProvinces() {
  return apiFetch('/wilayah/provinces')
}

export function wilayahRegencies(provinceCode) {
  return apiFetch(`/wilayah/regencies/${encodeURIComponent(provinceCode)}`)
}

export function wilayahDistricts(regencyCode) {
  return apiFetch(`/wilayah/districts/${encodeURIComponent(regencyCode)}`)
}

export function wilayahVillages(districtCode) {
  return apiFetch(`/wilayah/villages/${encodeURIComponent(districtCode)}`)
}

// --- PO / Sales Order (satu tabel) ---
export function listPo(params = {}) {
  const q = new URLSearchParams()
  if (params.mkt_workflow_stage) q.set('mkt_workflow_stage', params.mkt_workflow_stage)
  if (params.order_date) q.set('order_date', params.order_date)
  if (params.order_date_from && String(params.order_date_from).trim())
    q.set('order_date_from', String(params.order_date_from).trim().slice(0, 10))
  if (params.order_date_to && String(params.order_date_to).trim())
    q.set('order_date_to', String(params.order_date_to).trim().slice(0, 10))
  if (params.q && String(params.q).trim()) q.set('q', String(params.q).trim())
  if (params.customer_id != null && params.customer_id !== '') q.set('customer_id', String(params.customer_id))
  if (params.buyer && String(params.buyer).trim()) q.set('buyer', String(params.buyer).trim())
  if (params.status && String(params.status).trim()) q.set('status', String(params.status).trim())
  if (params.po_category && String(params.po_category).trim()) q.set('po_category', String(params.po_category).trim())
  if (params.limit != null) q.set('limit', String(params.limit))
  if (params.offset != null) q.set('offset', String(params.offset))
  const suffix = q.toString() ? `?${q}` : ''
  return apiFetch(`/po${suffix}`)
}

export function listPoPage(params = {}) {
  const q = new URLSearchParams()
  if (params.mkt_workflow_stage) q.set('mkt_workflow_stage', params.mkt_workflow_stage)
  if (params.order_date) q.set('order_date', params.order_date)
  if (params.order_date_from && String(params.order_date_from).trim())
    q.set('order_date_from', String(params.order_date_from).trim().slice(0, 10))
  if (params.order_date_to && String(params.order_date_to).trim())
    q.set('order_date_to', String(params.order_date_to).trim().slice(0, 10))
  if (params.q && String(params.q).trim()) q.set('q', String(params.q).trim())
  if (params.customer_id != null && params.customer_id !== '') q.set('customer_id', String(params.customer_id))
  if (params.buyer && String(params.buyer).trim()) q.set('buyer', String(params.buyer).trim())
  if (params.status && String(params.status).trim()) q.set('status', String(params.status).trim())
  if (params.po_category && String(params.po_category).trim()) q.set('po_category', String(params.po_category).trim())
  if (params.limit != null) q.set('limit', String(params.limit))
  if (params.offset != null) q.set('offset', String(params.offset))
  const suffix = q.toString() ? `?${q}` : ''
  return apiFetch(`/po/page${suffix}`)
}

export function fetchPoMaterialHints(poIds = []) {
  const ids = (poIds || []).filter((id) => id != null && id !== '')
  if (!ids.length) return Promise.resolve({ items: [] })
  const q = new URLSearchParams({ po_ids: ids.join(',') })
  return apiFetch(`/po/material-hints?${q}`)
}

export function listPoForCopy(params = {}) {
  const q = new URLSearchParams()
  if (params.customer_id) q.set('customer_id', params.customer_id)
  q.set('limit', '100')
  const suffix = q.toString() ? `?${q}` : ''
  return apiFetch(`/po${suffix}`)
}

export function listPoMktStages() {
  return apiFetch('/po/mkt-workflow-stages')
}

export function fetchNextPoNumber(params = {}) {
  const q = new URLSearchParams()
  if (params.po_category && String(params.po_category).trim()) {
    q.set('po_category', String(params.po_category).trim())
  }
  if (params.order_date && String(params.order_date).trim()) {
    q.set('order_date', String(params.order_date).trim())
  }
  if (params.material_group && String(params.material_group).trim()) {
    q.set('material_group', String(params.material_group).trim())
  }
  if (params.order_type_label && String(params.order_type_label).trim()) {
    q.set('order_type_label', String(params.order_type_label).trim())
  }
  const qs = q.toString()
  return apiFetch(`/po/next-number${qs ? `?${qs}` : ''}`)
}

/** Cek duplikat No. PO customer untuk customer yang sama. */
export function checkPoCustomerRef({ customer_id, po_customer_ref, exclude_po_id } = {}) {
  const q = new URLSearchParams()
  q.set('customer_id', String(customer_id))
  q.set('po_customer_ref', String(po_customer_ref).trim())
  if (exclude_po_id != null) q.set('exclude_po_id', String(exclude_po_id))
  return apiFetch(`/po/check-customer-ref?${q.toString()}`)
}

export function generatePoDetailLot(detailId) {
  return apiFetch(`/po-detail/${detailId}/generate-lot`, { method: 'POST' })
}

export function generateLotPreview(body) {
  return apiFetch('/po/generate-lot', { method: 'POST', body: JSON.stringify(body) })
}

/** Baris outstanding format marketing (join PO header + detail). @param {{ balance_filter?: 'all'|'exclude_zero'|'positive_only', po_q?: string, shipment_status?: 'all'|'sent'|'not_sent' }} params */
export function listMarketingOutstandingLines(params = {}) {
  const q = new URLSearchParams()
  if (params.balance_filter) q.set('balance_filter', params.balance_filter)
  if (params.computed_balance != null) q.set('computed_balance', String(params.computed_balance))
  if (params.po_q && String(params.po_q).trim()) q.set('po_q', String(params.po_q).trim())
  if (params.shipment_status) q.set('shipment_status', params.shipment_status)
  if (params.material_status) q.set('material_status', params.material_status)
  if (params.factory_code && String(params.factory_code).trim()) q.set('factory_code', String(params.factory_code).trim())
  if (params.po_category && String(params.po_category).trim()) q.set('po_category', String(params.po_category).trim())
  if (params.order_date_from && String(params.order_date_from).trim())
    q.set('order_date_from', String(params.order_date_from).trim().slice(0, 10))
  if (params.order_date_to && String(params.order_date_to).trim())
    q.set('order_date_to', String(params.order_date_to).trim().slice(0, 10))
  if (params.limit != null) q.set('limit', String(params.limit))
  const suffix = q.toString() ? `?${q}` : ''
  return apiFetch(`/marketing/outstanding-lines${suffix}`)
}

function _normalizePoDetailIdsCsv(raw) {
  if (raw == null || raw === '') return ''
  const parts = Array.isArray(raw) ? raw : String(raw).split(',')
  return parts
    .map((x) => String(x).trim())
    .filter((x) => /^\d+$/.test(x))
    .join(',')
}

function _marketingOutstandingExportQuery(params = {}, { includePoCategory = false } = {}) {
  const q = new URLSearchParams()
  if (params.balance_filter) q.set('balance_filter', params.balance_filter)
  if (params.computed_balance != null) q.set('computed_balance', String(params.computed_balance))
  if (params.po_q && String(params.po_q).trim()) q.set('po_q', String(params.po_q).trim())
  if (params.shipment_status) q.set('shipment_status', params.shipment_status)
  if (params.material_status) q.set('material_status', params.material_status)
  if (params.factory_code && String(params.factory_code).trim()) q.set('factory_code', String(params.factory_code).trim())
  if (includePoCategory && params.po_category && String(params.po_category).trim()) {
    q.set('po_category', String(params.po_category).trim())
  }
  if (params.order_date_from && String(params.order_date_from).trim())
    q.set('order_date_from', String(params.order_date_from).trim().slice(0, 10))
  if (params.order_date_to && String(params.order_date_to).trim())
    q.set('order_date_to', String(params.order_date_to).trim().slice(0, 10))
  const idsCsv = _normalizePoDetailIdsCsv(params.po_detail_ids)
  if (idsCsv) q.set('po_detail_ids', idsCsv)
  return q
}

export function marketingOutstandingCsvUrl(params = {}) {
  const q = _marketingOutstandingExportQuery(params, { includePoCategory: true })
  const suffix = q.toString() ? `?${q}` : ''
  return `/marketing/outstanding-lines.csv${suffix}`
}

/** Path unduhan Excel outstanding (Bearer di frontend saat fetch). */
export function marketingOutstandingXlsxPath(params = {}) {
  const q = _marketingOutstandingExportQuery(params, { includePoCategory: true })
  const suffix = q.toString() ? `?${q}` : ''
  return `/marketing/outstanding-lines.xlsx${suffix}`
}

/** Unduhan Excel lembar RETUR (hanya baris `po_category=return`). Query sama seperti outstanding, tanpa `po_category`. */
export function marketingOutstandingReturnXlsxPath(params = {}) {
  const q = _marketingOutstandingExportQuery(params)
  const suffix = q.toString() ? `?${q}` : ''
  return `/marketing/outstanding-return-lines.xlsx${suffix}`
}

/** Workbook multi-lembar PROD / CLAIM / SAMPLE / SUBCONT / RETUR (format manual marketing). */
export function marketingOutstandingManualXlsxPath(params = {}) {
  const suffix = _marketingOutstandingExportQuery(params).toString()
  return `/marketing/outstanding-manual.xlsx${suffix ? `?${suffix}` : ''}`
}

/** Baris delivery list (join surat jalan + produksi + PO) — format lembar marketing. */
export function listMarketingDeliveryLines(params = {}) {
  const q = new URLSearchParams()
  if (params.q && String(params.q).trim()) q.set('q', String(params.q).trim())
  if (params.delivery_status && String(params.delivery_status).trim())
    q.set('delivery_status', String(params.delivery_status).trim())
  if (params.packing_status && String(params.packing_status).trim())
    q.set('packing_status', String(params.packing_status).trim())
  if (params.invpl_printed && String(params.invpl_printed).trim())
    q.set('invpl_printed', String(params.invpl_printed).trim())
  if (params.delivery_date_from && String(params.delivery_date_from).trim())
    q.set('delivery_date_from', String(params.delivery_date_from).trim().slice(0, 10))
  if (params.delivery_date_to && String(params.delivery_date_to).trim())
    q.set('delivery_date_to', String(params.delivery_date_to).trim().slice(0, 10))
  if (params.factory_code && String(params.factory_code).trim())
    q.set('factory_code', String(params.factory_code).trim())
  if (params.po_category && String(params.po_category).trim())
    q.set('po_category', String(params.po_category).trim())
  if (params.customer && String(params.customer).trim()) q.set('customer', String(params.customer).trim())
  if (params.limit != null) q.set('limit', String(params.limit))
  if (params.skip != null) q.set('skip', String(params.skip))
  const suffix = q.toString() ? `?${q}` : ''
  return apiFetch(`/marketing/delivery-lines${suffix}`)
}

export function marketingDeliveryCsvUrl(params = {}) {
  const q = new URLSearchParams()
  if (params.q && String(params.q).trim()) q.set('q', String(params.q).trim())
  if (params.delivery_status && String(params.delivery_status).trim())
    q.set('delivery_status', String(params.delivery_status).trim())
  if (params.packing_status && String(params.packing_status).trim())
    q.set('packing_status', String(params.packing_status).trim())
  if (params.invpl_printed && String(params.invpl_printed).trim())
    q.set('invpl_printed', String(params.invpl_printed).trim())
  if (params.delivery_date_from && String(params.delivery_date_from).trim())
    q.set('delivery_date_from', String(params.delivery_date_from).trim().slice(0, 10))
  if (params.delivery_date_to && String(params.delivery_date_to).trim())
    q.set('delivery_date_to', String(params.delivery_date_to).trim().slice(0, 10))
  if (params.factory_code && String(params.factory_code).trim())
    q.set('factory_code', String(params.factory_code).trim())
  if (params.po_category && String(params.po_category).trim())
    q.set('po_category', String(params.po_category).trim())
  if (params.customer && String(params.customer).trim()) q.set('customer', String(params.customer).trim())
  const suffix = q.toString() ? `?${q}` : ''
  return `/marketing/delivery-lines.csv${suffix}`
}

/** Path unduhan Excel delivery list (Bearer lewat fetchAuthenticatedDocument). */
export function marketingDeliveryXlsxPath(params = {}) {
  const q = new URLSearchParams()
  if (params.q && String(params.q).trim()) q.set('q', String(params.q).trim())
  if (params.delivery_status && String(params.delivery_status).trim())
    q.set('delivery_status', String(params.delivery_status).trim())
  if (params.packing_status && String(params.packing_status).trim())
    q.set('packing_status', String(params.packing_status).trim())
  if (params.invpl_printed && String(params.invpl_printed).trim())
    q.set('invpl_printed', String(params.invpl_printed).trim())
  if (params.delivery_date_from && String(params.delivery_date_from).trim())
    q.set('delivery_date_from', String(params.delivery_date_from).trim().slice(0, 10))
  if (params.delivery_date_to && String(params.delivery_date_to).trim())
    q.set('delivery_date_to', String(params.delivery_date_to).trim().slice(0, 10))
  if (params.factory_code && String(params.factory_code).trim())
    q.set('factory_code', String(params.factory_code).trim())
  if (params.po_category && String(params.po_category).trim())
    q.set('po_category', String(params.po_category).trim())
  if (params.customer && String(params.customer).trim()) q.set('customer', String(params.customer).trim())
  const suffix = q.toString() ? `?${q}` : ''
  return `/marketing/delivery-lines.xlsx${suffix}`
}

export function createMarketingOutstandingSnapshot(body) {
  return apiFetch('/marketing/outstanding-snapshots', { method: 'POST', body: JSON.stringify(body) })
}

export function listMarketingOutstandingSnapshots(params = {}) {
  const q = new URLSearchParams()
  if (params.skip != null) q.set('skip', String(params.skip))
  if (params.limit != null) q.set('limit', String(params.limit))
  const suffix = q.toString() ? `?${q}` : ''
  return apiFetch(`/marketing/outstanding-snapshots${suffix}`)
}

export function getMarketingOutstandingSnapshot(id) {
  return apiFetch(`/marketing/outstanding-snapshots/${id}`)
}

export function listMarketingDeliveryPlanning(params = {}) {
  const q = new URLSearchParams()
  if (params.date_from && String(params.date_from).trim()) q.set('date_from', String(params.date_from).trim().slice(0, 10))
  if (params.date_to && String(params.date_to).trim()) q.set('date_to', String(params.date_to).trim().slice(0, 10))
  if (params.factory_code && String(params.factory_code).trim()) q.set('factory_code', String(params.factory_code).trim())
  const suffix = q.toString() ? `?${q}` : ''
  return apiFetch(`/marketing/delivery-planning${suffix}`)
}

export function getMarketingDeliveryToday(params = {}) {
  const q = new URLSearchParams()
  if (params.on_date && String(params.on_date).trim()) q.set('on_date', String(params.on_date).trim().slice(0, 10))
  if (params.factory_code && String(params.factory_code).trim()) q.set('factory_code', String(params.factory_code).trim())
  const suffix = q.toString() ? `?${q}` : ''
  return apiFetch(`/marketing/delivery-today${suffix}`)
}

/** Unduhan PDF sales contract / sales order per PO. */
export function salesContractPdfPath(poId) {
  return `/documents/sales-contract/${poId}/pdf`
}

/** Unduhan Word (.docx) sales contract per PO. */
export function salesContractDocxPath(poId) {
  return `/documents/sales-contract/${poId}/docx`
}

/** Unduhan PDF Proforma Invoice per PO. */
export function proformaInvoicePdfPath(poId) {
  return `/documents/proforma-invoice/${poId}/pdf`
}

/** Unduhan Word (.docx) Proforma Invoice per PO. */
export function proformaInvoiceDocxPath(poId) {
  return `/documents/proforma-invoice/${poId}/docx`
}

export function proformaInvoiceBatchPdfPath() {
  return `/api/v1/documents/proforma-invoice/batch/pdf`
}

export function proformaInvoiceBatchDocxPath() {
  return `/api/v1/documents/proforma-invoice/batch/docx`
}

export function createOutstandingScheduleBatch(body) {
  return apiFetch('/marketing/outstanding-schedule-batch', {
    method: 'POST',
    body: JSON.stringify(body),
  })
}

export function listOutstandingPackingOptions(poDetailIds = []) {
  const ids = (poDetailIds || []).filter((x) => x != null).join(',')
  return apiFetch(`/marketing/outstanding-packing-options?po_detail_ids=${encodeURIComponent(ids)}`)
}

export function createOutstandingShipBatch(body) {
  return apiFetch('/marketing/outstanding-ship-batch', {
    method: 'POST',
    body: JSON.stringify(body),
  })
}


export function advanceMktWorkflow(poId) {
  return apiFetch(`/po/${poId}/mkt-workflow/advance`, { method: 'POST' })
}

export function rollbackMktWorkflow(poId, { reason } = {}) {
  return apiFetch(`/po/${poId}/mkt-workflow/rollback`, {
    method: 'POST',
    body: JSON.stringify({ reason: reason || '' }),
  })
}

export function getPo(id) {
  return apiFetch(`/po/${id}`)
}

export function listPoDetails(poId) {
  return apiFetch(`/po/${poId}/details`)
}

export function createPo(body) {
  return apiFetch('/po', { method: 'POST', body: JSON.stringify(body) })
}

/** Salin PO (header + baris) ke nomor PO baru; baris dapat nomor lot kosong. */
export function duplicatePo(poId) {
  return apiFetch(`/po/${poId}/duplicate`, { method: 'POST' })
}

export function updatePo(id, body) {
  return apiFetch(`/po/${id}`, { method: 'PUT', body: JSON.stringify(body) })
}

/** Revisi marketing: ETD header, alamat kirim, follow-up material, baris (ETD/remark/jadwal) — tidak mengubah tanggal order / customer / harga. */
export function marketingRevisePo(poId, body) {
  return apiFetch(`/po/${poId}/marketing-revise`, { method: 'PATCH', body: JSON.stringify(body) })
}

export function deletePo(id) {
  return apiFetch(`/po/${id}`, { method: 'DELETE' })
}

export function addPoDetail(poId, body) {
  return apiFetch(`/po/${poId}/details`, { method: 'POST', body: JSON.stringify(body) })
}

export function updatePoDetail(detailId, body) {
  return apiFetch(`/po-detail/${detailId}`, { method: 'PUT', body: JSON.stringify(body) })
}

export function deletePoDetail(detailId) {
  return apiFetch(`/po-detail/${detailId}`, { method: 'DELETE' })
}

export function setPoDetailDeliverySchedules(detailId, schedules) {
  return apiFetch(`/po-detail/${detailId}/delivery-schedules`, {
    method: 'PUT',
    body: JSON.stringify({ schedules }),
  })
}

export function listPoDetailDeliverySchedules(detailId) {
  return apiFetch(`/po-detail/${detailId}/delivery-schedules`)
}

// --- Masters ---
export function listBrands() {
  return apiFetch('/masters/brands')
}

export function listBrandBuyers(brandId) {
  return apiFetch(`/masters/brands/${brandId}/buyers`)
}

export function createBrand(body) {
  return apiFetch('/masters/brands', { method: 'POST', body: JSON.stringify(body) })
}

export function updateBrand(id, body) {
  return apiFetch(`/masters/brands/${id}`, { method: 'PUT', body: JSON.stringify(body) })
}

export function deleteBrand(id) {
  return apiFetch(`/masters/brands/${id}`, { method: 'DELETE' })
}

export function listMasterItems() {
  return apiFetch('/masters/items')
}

export function listMasterItemsPage({ limit = 50, offset = 0, keyword, category, sort_by, sort_dir } = {}) {
  const p = new URLSearchParams({ limit: String(limit), offset: String(offset) })
  if (keyword != null && String(keyword).trim()) p.append('keyword', String(keyword).trim())
  if (category != null && String(category).trim()) p.append('category', String(category).trim())
  if (sort_by != null && String(sort_by).trim()) p.append('sort_by', String(sort_by).trim())
  if (sort_dir != null && String(sort_dir).trim()) p.append('sort_dir', String(sort_dir).trim())
  return apiFetch(`/masters/items/page?${p}`)
}

/** Cascade PO: nilai unik material → ketebalan → warna dari master_items. */
export function listMasterItemDimensionValues(kind, { material_name, thickness_text, category } = {}) {
  const p = new URLSearchParams({ kind })
  if (material_name != null && String(material_name).trim()) p.append('material_name', String(material_name).trim())
  if (thickness_text != null && String(thickness_text).trim()) p.append('thickness_text', String(thickness_text).trim())
  if (category != null && String(category).trim()) p.append('category', String(category).trim())
  return apiFetch(`/masters/items/dimension-values?${p}`)
}

/** Resolve tepat satu master item dari material + ketebalan + warna (status single|ambiguous|none). */
export function resolveMasterItemByDimensions({ material_name, thickness_text, color, category }) {
  const p = new URLSearchParams({
    material_name: String(material_name || '').trim(),
    thickness_text: String(thickness_text || '').trim(),
    color: String(color || '').trim(),
  })
  if (category != null && String(category).trim()) p.append('category', String(category).trim())
  return apiFetch(`/masters/items/resolve-by-dimensions?${p}`)
}

export function createMasterItem(body) {
  return apiFetch('/masters/items', { method: 'POST', body: JSON.stringify(body) })
}

export function updateMasterItem(id, body) {
  return apiFetch(`/masters/items/${id}`, { method: 'PUT', body: JSON.stringify(body) })
}

export function deleteMasterItem(id) {
  return apiFetch(`/masters/items/${id}`, { method: 'DELETE' })
}

export async function exportMasterItems() {
  const r = await fetch(`/api/v1/masters/items/export`, {
    headers: { Authorization: `Bearer ${localStorage.getItem('auth_token')}` },
  })
  if (!r.ok) throw new Error(r.statusText)
  const blob = await r.blob()
  const blobUrl = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = blobUrl
  a.download = 'master_items.xlsx'
  a.click()
  URL.revokeObjectURL(blobUrl)
}

export async function importMasterItems(file) {
  const fd = new FormData()
  fd.append('file', file)
  return apiFetch('/masters/items/import', { method: 'POST', body: fd })
}

export function listFluorescentColors(params = {}) {
  const q = new URLSearchParams()
  if (params.buyer_code && String(params.buyer_code).trim()) q.set('buyer_code', String(params.buyer_code).trim())
  if (params.season_label && String(params.season_label).trim()) q.set('season_label', String(params.season_label).trim())
  if (params.color_class && String(params.color_class).trim()) q.set('color_class', String(params.color_class).trim())
  const suffix = q.toString() ? `?${q.toString()}` : ''
  return apiFetch(`/masters/fluorescent-colors${suffix}`)
}

export function listFluorescentColorsPage(params = {}) {
  const q = new URLSearchParams()
  if (params.buyer_code && String(params.buyer_code).trim()) q.set('buyer_code', String(params.buyer_code).trim())
  if (params.season_label && String(params.season_label).trim()) q.set('season_label', String(params.season_label).trim())
  if (params.color_class && String(params.color_class).trim()) q.set('color_class', String(params.color_class).trim())
  if (params.q && String(params.q).trim()) q.set('q', String(params.q).trim())
  if (params.sort_by && String(params.sort_by).trim()) q.set('sort_by', String(params.sort_by).trim())
  if (params.sort_dir && String(params.sort_dir).trim()) q.set('sort_dir', String(params.sort_dir).trim())
  if (params.limit != null) q.set('limit', String(params.limit))
  if (params.offset != null) q.set('offset', String(params.offset))
  const suffix = q.toString() ? `?${q.toString()}` : ''
  return apiFetch(`/masters/fluorescent-colors/page${suffix}`)
}

export function listFluorescentFormOptions() {
  return apiFetch('/masters/fluorescent-colors/form-options')
}

export function createFluorescentColor(body) {
  return apiFetch('/masters/fluorescent-colors', { method: 'POST', body: JSON.stringify(body) })
}

export function updateFluorescentColor(id, body) {
  return apiFetch(`/masters/fluorescent-colors/${id}`, { method: 'PUT', body: JSON.stringify(body) })
}

export function deleteFluorescentColor(id) {
  return apiFetch(`/masters/fluorescent-colors/${id}`, { method: 'DELETE' })
}

export function importFluorescentBundled() {
  return apiFetch('/masters/fluorescent-colors/import-bundled', { method: 'POST' })
}

export function importFluorescentCsv(file) {
  const fd = new FormData()
  fd.append('file', file)
  return apiFetch('/masters/fluorescent-colors/import-csv', { method: 'POST', body: fd })
}

/** Master color swatch (resep pabrik × buyer × material × emboss). */
export function listColorSwatchRecipesPage(params = {}) {
  const q = new URLSearchParams()
  if (params.factory_key && String(params.factory_key).trim()) q.set('factory_key', String(params.factory_key).trim())
  if (params.buyer_code && String(params.buyer_code).trim()) q.set('buyer_code', String(params.buyer_code).trim())
  if (params.material_name && String(params.material_name).trim()) q.set('material_name', String(params.material_name).trim())
  if (params.q && String(params.q).trim()) q.set('q', String(params.q).trim())
  if (params.sort_by && String(params.sort_by).trim()) q.set('sort_by', String(params.sort_by).trim())
  if (params.sort_dir && String(params.sort_dir).trim()) q.set('sort_dir', String(params.sort_dir).trim())
  if (params.limit != null) q.set('limit', String(params.limit))
  if (params.offset != null) q.set('offset', String(params.offset))
  const suffix = q.toString() ? `?${q.toString()}` : ''
  return apiFetch(`/masters/color-swatch-recipes/page${suffix}`)
}

export function lookupColorSwatchRecipes(params = {}) {
  const q = new URLSearchParams()
  const fk = String(params.factory_key || '').trim()
  if (fk) q.set('factory_key', fk)
  q.set('buyer_code', String(params.buyer_code || '').trim())
  if (params.customer_id != null && params.customer_id !== '') q.set('customer_id', String(params.customer_id))
  if (params.material_name && String(params.material_name).trim()) q.set('material_name', String(params.material_name).trim())
  if (params.color_name && String(params.color_name).trim()) q.set('color_name', String(params.color_name).trim())
  if (params.emboss && String(params.emboss).trim()) q.set('emboss', String(params.emboss).trim())
  if (params.include_all_materials) q.set('include_all_materials', 'true')
  if (params.q && String(params.q).trim()) q.set('q', String(params.q).trim())
  if (params.limit != null) q.set('limit', String(params.limit))
  return apiFetch(`/masters/color-swatch-recipes/lookup?${q}`)
}

export function getColorSwatchPoFill(recipeId) {
  return apiFetch(`/masters/color-swatch-recipes/${recipeId}/po-fill`)
}

export function listColorSwatchFormOptions() {
  return apiFetch('/masters/color-swatch-recipes/form-options')
}

export function createColorSwatchRecipe(body) {
  return apiFetch('/masters/color-swatch-recipes', { method: 'POST', body: JSON.stringify(body) })
}

export function updateColorSwatchRecipe(id, body) {
  return apiFetch(`/masters/color-swatch-recipes/${id}`, { method: 'PUT', body: JSON.stringify(body) })
}

export function deleteColorSwatchRecipe(id) {
  return apiFetch(`/masters/color-swatch-recipes/${id}`, { method: 'DELETE' })
}

export function importColorSwatchCsv(file) {
  const fd = new FormData()
  fd.append('file', file)
  return apiFetch('/masters/color-swatch-recipes/import-csv', { method: 'POST', body: fd })
}

export function importColorSwatchBundled() {
  return apiFetch('/masters/color-swatch-recipes/import-bundled', { method: 'POST' })
}

// --- Production ---
export function listProduction() {
  return apiFetch('/production')
}

export function getProduction(id) {
  return apiFetch(`/production/${id}`)
}

export function listProductionDetails(productionId) {
  return apiFetch(`/production/${productionId}/details`)
}

export function createProduction(body) {
  return apiFetch('/production', { method: 'POST', body: JSON.stringify(body) })
}

// --- QC ---
export function listQc() {
  return apiFetch('/qc')
}

export function listQcDetails(qcId) {
  return apiFetch(`/qc/${qcId}/details`)
}

export function createQc(body) {
  return apiFetch('/qc', { method: 'POST', body: JSON.stringify(body) })
}

export function addQcDetail(qcId, body) {
  return apiFetch(`/qc/${qcId}/details`, { method: 'POST', body: JSON.stringify(body) })
}

// --- Delivery ---
export function listDelivery() {
  return apiFetch('/delivery')
}

export function getDelivery(id) {
  return apiFetch(`/delivery/${id}`)
}

export function listDeliveryDetails(deliveryId) {
  return apiFetch(`/delivery/${deliveryId}/details`)
}

export function createDelivery(body) {
  return apiFetch('/delivery', { method: 'POST', body: JSON.stringify(body) })
}

export function listReadyToShip(params = {}) {
  const q = new URLSearchParams()
  if (params.packing_id != null) q.set('packing_id', String(params.packing_id))
  if (params.lot_keyword) q.set('lot_keyword', String(params.lot_keyword).trim())
  if (params.customer_id != null) q.set('customer_id', String(params.customer_id))
  if (params.limit != null) q.set('limit', String(params.limit))
  const suffix = q.toString() ? `?${q.toString()}` : ''
  return apiFetch(`/delivery-shipments/ready${suffix}`)
}

export function createDeliveryFromPackingLines(body) {
  return apiFetch('/delivery-shipments/from-packing-lines', { method: 'POST', body: JSON.stringify(body) })
}

export function updateDelivery(id, body) {
  return apiFetch(`/delivery/${id}`, { method: 'PUT', body: JSON.stringify(body) })
}

export function markSuratJalanPrinted(deliveryId) {
  return apiFetch(`/delivery/${deliveryId}/mark-surat-jalan-printed`, { method: 'POST' })
}

export function addDeliveryDetail(deliveryId, body, opts = {}) {
  const q = opts.bypass_qc ? '?bypass_qc=true' : ''
  return apiFetch(`/delivery/${deliveryId}/details${q}`, { method: 'POST', body: JSON.stringify(body) })
}

// --- Packing ---
export function listPacking() {
  return apiFetch('/packing')
}

export function getPacking(id) {
  return apiFetch(`/packing/${id}`)
}

export function createPacking(body) {
  return apiFetch('/packing', { method: 'POST', body: JSON.stringify(body) })
}

export function updatePacking(id, body) {
  return apiFetch(`/packing/${id}`, { method: 'PUT', body: JSON.stringify(body) })
}

export function markInvplPrinted(packingId) {
  return apiFetch(`/packing/${packingId}/mark-invpl-printed`, { method: 'POST' })
}

export function listPackingCandidateLines(packingId) {
  return apiFetch(`/packing/${packingId}/candidate-lines`)
}

export function savePackingDetailsBatch(packingId, lines) {
  return apiFetch(`/packing/${packingId}/details/batch`, {
    method: 'POST',
    body: JSON.stringify({ lines }),
  })
}

// --- Invoice ---
export function listInvoice() {
  return apiFetch('/invoice')
}

export function listOutstandingInvoice(params = {}) {
  const q = new URLSearchParams()
  if (params.overdue_only) q.set('overdue_only', 'true')
  if (params.due_within_days != null) q.set('due_within_days', String(params.due_within_days))
  if (params.hide_po) q.set('hide_po', 'true')
  const suffix = q.toString() ? `?${q}` : ''
  return apiFetch(`/invoice/outstanding${suffix}`)
}

export function updateInvoice(id, body) {
  return apiFetch(`/invoice/${id}`, { method: 'PUT', body: JSON.stringify(body) })
}

export async function importMasterZip(file) {
  const fd = new FormData()
  fd.append('file', file)
  return apiFetch('/masters/import-zip', { method: 'POST', body: fd })
}

export function createInvoice(body) {
  return apiFetch('/invoice', { method: 'POST', body: JSON.stringify(body) })
}

// --- Customs ---
export function listCustomsDeclarations() {
  return apiFetch('/customs/declarations')
}

export function getCustomsDeclaration(id) {
  return apiFetch(`/customs/declarations/${id}`)
}

export function createCustomsDeclaration(body) {
  return apiFetch('/customs/declarations', { method: 'POST', body: JSON.stringify(body) })
}

export function updateCustomsDeclaration(id, body) {
  return apiFetch(`/customs/declarations/${id}`, { method: 'PUT', body: JSON.stringify(body) })
}

/** Simpan semua sheet (kolom + baris) untuk satu deklarasi AJU. */
export function saveCustomsSheetsData(id, body) {
  return apiFetch(`/customs/declarations/${id}/sheets-data`, { method: 'PUT', body: JSON.stringify(body) })
}

export function deleteCustomsDeclaration(id) {
  return apiFetch(`/customs/declarations/${id}`, { method: 'DELETE' })
}

export function importCustomsZip(file, sourceLabel) {
  const fd = new FormData()
  fd.append('file', file)
  if (sourceLabel) fd.append('source_label', sourceLabel)
  return apiFetch('/customs/declarations/import-zip', { method: 'POST', body: fd })
}

export function importCustomsCsvFiles(files, sourceLabel) {
  const fd = new FormData()
  for (const f of files) fd.append('files', f)
  if (sourceLabel) fd.append('source_label', sourceLabel)
  return apiFetch('/customs/declarations/import-upload', { method: 'POST', body: fd })
}

export function generateCustomsFromDelivery(deliveryId) {
  return apiFetch(`/customs/generate-from-delivery/${deliveryId}`, { method: 'POST' })
}

/** Unduh ZIP CSV BC 3.0 untuk unggah ke CEISA / Core Customs. */
export function exportCustomsZip(declarationId) {
  return fetchAuthenticatedDocument(`/customs/declarations/${declarationId}/export-zip`, {
    mode: 'download',
    downloadFallbackName: `customs-${declarationId}.zip`,
  })
}

// --- Buyer prices ---
export function listBuyerPriceLists() {
  return apiFetch('/buyer-prices/lists')
}

export function getBuyerPriceList(id) {
  return apiFetch(`/buyer-prices/lists/${id}`)
}

/**
 * Resolusi harga satuan dari sheet list harga buyer (logika di server).
 * @param {object} body - buyer_code, material_name?, color?, style_article?, thickness_text?, color_family?
 */
export function resolveBuyerUnitPrice(body) {
  return apiFetch('/buyer-prices/resolve-unit-price', { method: 'POST', body: JSON.stringify(body) })
}

export function deleteBuyerPriceList(id) {
  return apiFetch(`/buyer-prices/lists/${id}`, { method: 'DELETE' })
}

export function createBuyerPriceList(body) {
  return apiFetch('/buyer-prices/lists', { method: 'POST', body: JSON.stringify(body) })
}

export function updateBuyerPriceList(id, body) {
  return apiFetch(`/buyer-prices/lists/${id}`, { method: 'PUT', body: JSON.stringify(body) })
}

/** Simpan urutan kolom + seluruh baris sheet (master data). */
export function saveBuyerPriceSheet(id, body) {
  return apiFetch(`/buyer-prices/lists/${id}/sheet`, { method: 'PUT', body: JSON.stringify(body) })
}

// --- Reports (export) ---
export function reportSalesOrdersExportUrl() {
  return '/api/v1/reports/sales-orders-export.csv'
}

export function reportSalesOrderLinesExportUrl() {
  return '/api/v1/reports/sales-order-lines-export.csv'
}

/** JSON untuk halaman Reports (revisi ketebalan, produksi, sample). */
export function fetchReportPoOrderDescription(params = {}) {
  const q = new URLSearchParams()
  if (params.date_from) q.set('date_from', params.date_from)
  if (params.date_to) q.set('date_to', params.date_to)
  if (params.customer) q.set('customer', params.customer)
  if (params.date_field) q.set('date_field', params.date_field)
  const suffix = q.toString() ? `?${q}` : ''
  return apiFetch(`/reports/po-order-description${suffix}`)
}

/** CSV LAPORAN PO HARIAN MARKETING (UTF-8 BOM); path relatif untuk fetch + Authorization. */
export function reportPoDailyMarketingCsvPath(params = {}) {
  const q = new URLSearchParams()
  if (params.date_from) q.set('date_from', params.date_from)
  if (params.date_to) q.set('date_to', params.date_to)
  if (params.customer) q.set('customer', params.customer)
  if (params.date_field) q.set('date_field', params.date_field)
  const suffix = q.toString() ? `?${q}` : ''
  return `/api/v1/reports/po-daily-marketing.csv${suffix}`
}

/** XLSX LAPORAN PO HARIAN MARKETING; path relatif untuk fetch + Authorization. */
export function reportPoDailyMarketingXlsxPath(params = {}) {
  const q = new URLSearchParams()
  if (params.date_from) q.set('date_from', params.date_from)
  if (params.date_to) q.set('date_to', params.date_to)
  if (params.customer) q.set('customer', params.customer)
  if (params.date_field) q.set('date_field', params.date_field)
  const suffix = q.toString() ? `?${q}` : ''
  return `/api/v1/reports/po-daily-marketing.xlsx${suffix}`
}

// --- Special Prices ---
export async function listSpecialPrices(params = {}) {
  const q = new URLSearchParams()
  if (params.buyer_code) q.set('buyer_code', params.buyer_code)
  const suffix = q.toString() ? `?${q}` : ''
  return apiFetch(`/pricing/special-prices${suffix}`)
}

export async function createSpecialPrice(body) {
  return apiFetch('/pricing/special-prices', { method: 'POST', body: JSON.stringify(body) })
}

export async function updateSpecialPrice(id, body) {
  return apiFetch(`/pricing/special-prices/${id}`, { method: 'PUT', body: JSON.stringify(body) })
}

export async function deleteSpecialPrice(id) {
  return apiFetch(`/pricing/special-prices/${id}`, { method: 'DELETE' })
}

export async function listCustomerPrices(params = {}) {
  const q = new URLSearchParams()
  if (params.customer_id) q.set('customer_id', params.customer_id)
  const suffix = q.toString() ? `?${q}` : ''
  return apiFetch(`/pricing/customer-prices${suffix}`)
}

export async function createCustomerPrice(body) {
  return apiFetch('/pricing/customer-prices', { method: 'POST', body: JSON.stringify(body) })
}

export async function updateCustomerPrice(id, body) {
  return apiFetch(`/pricing/customer-prices/${id}`, { method: 'PUT', body: JSON.stringify(body) })
}

export async function deleteCustomerPrice(id) {
  return apiFetch(`/pricing/customer-prices/${id}`, { method: 'DELETE' })
}

export async function bulkUpdatePrices(updates) {
  return apiFetch('/pricing/bulk-update', { method: 'POST', body: JSON.stringify({ updates }) })
}

export async function bulkUpdatePricesCsv(file) {
  const fd = new FormData()
  fd.append('file', file)
  return apiFetch('/pricing/bulk-update-csv', { method: 'POST', body: fd })
}


/** Rekap laporan PO (filter tanggal order atau input) — CSV arsip saja */
export function reportPoDailyRecapUrl(dateStr, poId) {
  const q = new URLSearchParams()
  if (dateStr) q.set('date', dateStr)
  if (poId != null && poId !== '') q.set('po_id', String(poId))
  const suffix = q.toString() ? `?${q}` : ''
  return `/api/v1/reports/po-daily-recap.csv${suffix}`
}

/** Data JSON rekap PO/SO untuk dialog cetak HTML (tidak stamp status). */
export function getPoDailyRecap({ date, poId } = {}) {
  const q = new URLSearchParams()
  if (date) q.set('date', date)
  if (poId != null && poId !== '') q.set('po_id', String(poId))
  const suffix = q.toString() ? `?${q}` : ''
  return apiFetch(`/reports/po-daily-recap${suffix}`)
}

/** Konfirmasi setelah MKT mencetak rekap dari dialog HTML → stamp rekap_printed. */
export function confirmPoDailyRecapPrint(body = {}) {
  return apiFetch('/reports/po-daily-recap/confirm-print', {
    method: 'POST',
    body: JSON.stringify(body),
  })
}

// --- Customer Brand Mappings ---
export function listCustomerBrandMappings(customerId) {
  return apiFetch(`/customers/${customerId}/brand-mappings`)
}

export function createCustomerBrandMapping(customerId, body) {
  return apiFetch(`/customers/${customerId}/brand-mappings`, { method: 'POST', body: JSON.stringify(body) })
}

export function updateCustomerBrandMapping(customerId, mappingId, body) {
  return apiFetch(`/customers/${customerId}/brand-mappings/${mappingId}`, { method: 'PUT', body: JSON.stringify(body) })
}

export function deleteCustomerBrandMapping(customerId, mappingId) {
  return apiFetch(`/customers/${customerId}/brand-mappings/${mappingId}`, { method: 'DELETE' })
}

export function getAllowedBrands(customerId) {
  return apiFetch(`/customers/${customerId}/allowed-brands`)
}

export function getBrandConstraint(customerId) {
  return apiFetch(`/customers/${customerId}/brand-constraint`)
}

export function upsertBrandConstraint(customerId, body) {
  return apiFetch(`/customers/${customerId}/brand-constraint`, { method: 'PUT', body: JSON.stringify(body) })
}

// --- Subcon Invoices ---
export function listSubconInvoices(params = {}) {
  const q = new URLSearchParams()
  if (params.po_id) q.set('po_id', String(params.po_id))
  if (params.status) q.set('status', params.status)
  if (params.invoice_type) q.set('invoice_type', params.invoice_type)
  const suffix = q.toString() ? `?${q}` : ''
  return apiFetch(`/subcon-invoices${suffix}`)
}

export function createSubconInvoice(body) {
  return apiFetch('/subcon-invoices', { method: 'POST', body: JSON.stringify(body) })
}

export function updateSubconInvoice(id, body) {
  return apiFetch(`/subcon-invoices/${id}`, { method: 'PUT', body: JSON.stringify(body) })
}

export function deleteSubconInvoice(id) {
  return apiFetch(`/subcon-invoices/${id}`, { method: 'DELETE' })
}

export function generateSubconInvoicesFromPo(poId) {
  return apiFetch(`/subcon-invoices/generate-from-po/${poId}`, { method: 'POST' })
}

// --- PPIC Workflow ---
export function assignPoToPpic(poId, body) {
  return apiFetch(`/workflow/po/${poId}/assign-to-ppic`, { method: 'POST', body: JSON.stringify(body) })
}

export function getPpicDashboard(params = {}) {
  const q = new URLSearchParams()
  if (params.user_id) q.set('user_id', String(params.user_id))
  if (params.status) q.set('status', params.status)
  const suffix = q.toString() ? `?${q}` : ''
  return apiFetch(`/workflow/ppic/dashboard${suffix}`)
}

export function updatePpicAssignmentStatus(assignmentId, body) {
  return apiFetch(`/workflow/ppic/assignments/${assignmentId}/status`, { method: 'PUT', body: JSON.stringify(body) })
}

export function listPpicUsers() {
  return apiFetch('/workflow/ppic/users')
}

// --- Outstanding Materials ---
export function listOutstandingMaterials(params = {}) {
  const q = new URLSearchParams()
  if (params.customer_id) q.set('customer_id', String(params.customer_id))
  if (params.status) q.set('status', params.status)
  const suffix = q.toString() ? `?${q}` : ''
  return apiFetch(`/workflow/outstanding-materials${suffix}`)
}

export function deliverOutstandingMaterial(materialId, deliveredQty) {
  return apiFetch(`/workflow/outstanding-materials/${materialId}/deliver`, {
    method: 'PUT',
    body: JSON.stringify({ delivered_qty: deliveredQty }),
  })
}

// --- Accounting Mappings ---
export function listAccountingMappings(params = {}) {
  const q = new URLSearchParams()
  if (params.transaction_type) q.set('transaction_type', params.transaction_type)
  if (params.status) q.set('status', params.status)
  const suffix = q.toString() ? `?${q}` : ''
  return apiFetch(`/accounting/mappings${suffix}`)
}

export function createAccountingMapping(body) {
  return apiFetch('/accounting/mappings', { method: 'POST', body: JSON.stringify(body) })
}

export function updateAccountingMapping(id, body) {
  return apiFetch(`/accounting/mappings/${id}`, { method: 'PUT', body: JSON.stringify(body) })
}

export function deleteAccountingMapping(id) {
  return apiFetch(`/accounting/mappings/${id}`, { method: 'DELETE' })
}

// --- Inventory - Warehouse ---
export function listWarehouses() {
  return apiFetch('/inventory/warehouses')
}

export function createWarehouse(body) {
  return apiFetch('/inventory/warehouses', { method: 'POST', body: JSON.stringify(body) })
}

export function updateWarehouse(id, body) {
  return apiFetch(`/inventory/warehouses/${id}`, { method: 'PUT', body: JSON.stringify(body) })
}

// --- Inventory - Materials ---
export function listMaterials() {
  return apiFetch('/inventory/materials')
}

export function createMaterial(body) {
  return apiFetch('/inventory/materials', { method: 'POST', body: JSON.stringify(body) })
}

export function updateMaterial(id, body) {
  return apiFetch(`/inventory/materials/${id}`, { method: 'PUT', body: JSON.stringify(body) })
}

// --- Inventory - Stock ---
export function listStocks(params = {}) {
  const q = new URLSearchParams()
  if (params.warehouse_id) q.set('warehouse_id', String(params.warehouse_id))
  if (params.material_id) q.set('material_id', String(params.material_id))
  const suffix = q.toString() ? `?${q}` : ''
  return apiFetch(`/inventory/stocks${suffix}`)
}

export function getStockSummary() {
  return apiFetch('/inventory/stocks/summary')
}

// --- Inventory - Receipt ---
export function listReceipts(params = {}) {
  const q = new URLSearchParams()
  if (params.status) q.set('status', params.status)
  const suffix = q.toString() ? `?${q}` : ''
  return apiFetch(`/inventory/receipts${suffix}`)
}

export function createReceipt(body) {
  return apiFetch('/inventory/receipts', { method: 'POST', body: JSON.stringify(body) })
}

// --- Journal Entries ---
export function listJournalEntries(params = {}) {
  const q = new URLSearchParams()
  if (params.date_from) q.set('date_from', params.date_from)
  if (params.date_to) q.set('date_to', params.date_to)
  if (params.transaction_type) q.set('transaction_type', params.transaction_type)
  const suffix = q.toString() ? `?${q}` : ''
  return apiFetch(`/journal/entries${suffix}`)
}

export function generateJournalFromTransaction(transaction_type, transaction_id) {
  return apiFetch('/journal/entries/generate-from-transaction', {
    method: 'POST',
    body: JSON.stringify({ transaction_type, transaction_id }),
  })
}

export function getTrialBalance(params = {}) {
  const q = new URLSearchParams()
  if (params.date_from) q.set('date_from', params.date_from)
  if (params.date_to) q.set('date_to', params.date_to)
  const suffix = q.toString() ? `?${q}` : ''
  return apiFetch(`/journal/entries/trial-balance${suffix}`)
}

/* ---- MRP shopfloor (Flask via FastAPI gateway /api/v1/mrp) ---- */
export function mrpListRencana() {
  return apiFetch('/mrp/rencana-produksi')
}

export function mrpGetRencana(id) {
  return apiFetch(`/mrp/rencana-produksi/${id}`)
}

export function mrpCreateRencana(body) {
  return apiFetch('/mrp/rencana-produksi', { method: 'POST', body: JSON.stringify(body) })
}

export function mrpSyncPo() {
  return apiFetch('/mrp/sync/po', { method: 'POST', body: JSON.stringify({}) })
}

export function mrpListMasterPo(params = {}) {
  const q = new URLSearchParams()
  if (params.status) q.set('status', params.status)
  const suffix = q.toString() ? `?${q}` : ''
  return apiFetch(`/mrp/masters/po${suffix}`)
}

export function mrpPaletOut(body) {
  return apiFetch('/mrp/palet/out', { method: 'POST', body: JSON.stringify(body) })
}

export function mrpErpOptions() {
  return apiFetch('/mrp/masters/erp/options')
}

export function mrpListMasterErp() {
  return apiFetch('/mrp/masters/erp')
}

export function mrpListMasterKulit() {
  return apiFetch('/mrp/masters/kulit')
}

export function mrpCreateMasterKulit(body) {
  return apiFetch('/mrp/masters/kulit', { method: 'POST', body: JSON.stringify(body) })
}

export function mrpListMasterKimia() {
  return apiFetch('/mrp/masters/kimia')
}

export function mrpCreateMasterKimia(body) {
  return apiFetch('/mrp/masters/kimia', { method: 'POST', body: JSON.stringify(body) })
}

export function mrpListMasterRp() {
  return apiFetch('/mrp/masters/rp')
}

export function mrpCreateMasterRp(body) {
  return apiFetch('/mrp/masters/rp', { method: 'POST', body: JSON.stringify(body) })
}

export function mrpListPaletMovements() {
  return apiFetch('/mrp/palet/movements')
}

export function mrpPaletIn(body) {
  return apiFetch('/mrp/palet/in', { method: 'POST', body: JSON.stringify(body) })
}

export function mrpPaletYl(kodePalet) {
  return apiFetch(`/mrp/palet/${encodeURIComponent(kodePalet)}/yl`)
}

export function mrpListYl() {
  return apiFetch('/mrp/yl')
}

export function mrpListProses() {
  return apiFetch('/mrp/proses')
}

export function mrpCreateProses(body) {
  return apiFetch('/mrp/proses', { method: 'POST', body: JSON.stringify(body) })
}

export function mrpGetProses(id) {
  return apiFetch(`/mrp/proses/${id}`)
}

export function mrpProsesAction(id, body) {
  return apiFetch(`/mrp/proses/${id}/actions`, { method: 'POST', body: JSON.stringify(body) })
}

export function mrpProsesScanRencana(q) {
  const suffix = q ? `?q=${encodeURIComponent(q)}` : ''
  return apiFetch(`/mrp/proses/scan-rencana${suffix}`)
}

export function mrpProsesLabel(id) {
  return apiFetch(`/mrp/proses/${id}/label`)
}

export function mrpListTreatment() {
  return apiFetch('/mrp/masters/treatment')
}

export function mrpCreateTreatment(body) {
  return apiFetch('/mrp/masters/treatment', { method: 'POST', body: JSON.stringify(body) })
}

export function mrpUpdateTreatment(id, body) {
  return apiFetch(`/mrp/masters/treatment/${id}`, { method: 'PUT', body: JSON.stringify(body) })
}

export function mrpDeleteTreatment(id) {
  return apiFetch(`/mrp/masters/treatment/${id}`, { method: 'DELETE' })
}

export function mrpListLab() {
  return apiFetch('/mrp/lab')
}

export function mrpLabOptions() {
  return apiFetch('/mrp/lab/options')
}

export function mrpCreateLab(body) {
  return apiFetch('/mrp/lab', { method: 'POST', body: JSON.stringify(body) })
}

export function mrpListPacking(params = {}) {
  const q = new URLSearchParams()
  if (params.all) q.set('all', '1')
  const suffix = q.toString() ? `?${q}` : ''
  return apiFetch(`/mrp/packing${suffix}`)
}

export function mrpPackingScanWip(q) {
  return apiFetch(`/mrp/packing/scan-wip?q=${encodeURIComponent(q || '')}`)
}

export function mrpStartPacking(body) {
  return apiFetch('/mrp/packing', { method: 'POST', body: JSON.stringify(body) })
}

export function mrpGetPacking(id) {
  return apiFetch(`/mrp/packing/${id}`)
}

export function mrpPackingAction(id, body) {
  return apiFetch(`/mrp/packing/${id}/actions`, { method: 'POST', body: JSON.stringify(body) })
}

export function mrpPackingPrint(id) {
  return apiFetch(`/mrp/packing/${id}/print`)
}

export function mrpListGudangFg() {
  return apiFetch('/mrp/gudang-fg')
}

export function mrpGetGudangFg(id) {
  return apiFetch(`/mrp/gudang-fg/${id}`)
}

export function mrpGudangFgOut(body) {
  return apiFetch('/mrp/gudang-fg/out', { method: 'POST', body: JSON.stringify(body) })
}

export function mrpStokKimia() {
  return apiFetch('/mrp/stok-kimia')
}

export function mrpStokKimiaAction(body) {
  return apiFetch('/mrp/stok-kimia', { method: 'POST', body: JSON.stringify(body) })
}

export function mrpStokRp() {
  return apiFetch('/mrp/stok-rp')
}

export function mrpStokRpAction(body) {
  return apiFetch('/mrp/stok-rp', { method: 'POST', body: JSON.stringify(body) })
}

export function mrpUsageColor() {
  return apiFetch('/mrp/usage-color')
}

export function mrpUsageColorScanLot(q) {
  return apiFetch(`/mrp/usage-color/scan-lot?q=${encodeURIComponent(q || '')}`)
}

export function mrpUsageColorCreate(body) {
  return apiFetch('/mrp/usage-color', { method: 'POST', body: JSON.stringify(body) })
}

export function mrpUsageRp() {
  return apiFetch('/mrp/usage-rp')
}

export function mrpUsageRpScan(q) {
  return apiFetch(`/mrp/usage-rp/scan-rp?q=${encodeURIComponent(q || '')}`)
}

export function mrpUsageRpCreate(body) {
  return apiFetch('/mrp/usage-rp', { method: 'POST', body: JSON.stringify(body) })
}

export function mrpListMasterMaterialLain() {
  return apiFetch('/mrp/masters/material-lain')
}

export function mrpCreateMasterMaterialLain(body) {
  return apiFetch('/mrp/masters/material-lain', { method: 'POST', body: JSON.stringify(body) })
}

export function mrpDeleteMasterMaterialLain(id) {
  return apiFetch(`/mrp/masters/material-lain/${id}`, { method: 'DELETE' })
}

export function mrpStokMaterialLain() {
  return apiFetch('/mrp/stok-material-lain')
}

export function mrpStokMaterialLainAction(body) {
  return apiFetch('/mrp/stok-material-lain', { method: 'POST', body: JSON.stringify(body) })
}

export function mrpUsageMaterial() {
  return apiFetch('/mrp/usage-material-lain')
}

export function mrpUsageMaterialScan(q) {
  return apiFetch(`/mrp/usage-material-lain/scan?q=${encodeURIComponent(q || '')}`)
}

export function mrpUsageMaterialCreate(body) {
  return apiFetch('/mrp/usage-material-lain', { method: 'POST', body: JSON.stringify(body) })
}

export function mrpUpdateMasterKulit(id, body) {
  return apiFetch(`/mrp/masters/kulit/${id}`, { method: 'PUT', body: JSON.stringify(body) })
}

export function mrpDeleteMasterKulit(id) {
  return apiFetch(`/mrp/masters/kulit/${id}`, { method: 'DELETE' })
}

export function mrpUpdateMasterKimia(id, body) {
  return apiFetch(`/mrp/masters/kimia/${id}`, { method: 'PUT', body: JSON.stringify(body) })
}

export function mrpDeleteMasterKimia(id) {
  return apiFetch(`/mrp/masters/kimia/${id}`, { method: 'DELETE' })
}

export function mrpUpdateMasterRp(id, body) {
  return apiFetch(`/mrp/masters/rp/${id}`, { method: 'PUT', body: JSON.stringify(body) })
}

export function mrpDeleteMasterRp(id) {
  return apiFetch(`/mrp/masters/rp/${id}`, { method: 'DELETE' })
}

export function mrpYlMovement(body) {
  return apiFetch('/mrp/yl/movement', { method: 'POST', body: JSON.stringify(body) })
}

export function mrpErpFields(params = {}) {
  const q = new URLSearchParams()
  Object.entries(params).forEach(([k, v]) => {
    if (v) q.set(k, v)
  })
  const suffix = q.toString() ? `?${q}` : ''
  return apiFetch(`/mrp/erp/fields${suffix}`)
}

export function mrpErpCombination(params = {}) {
  const q = new URLSearchParams(params)
  return apiFetch(`/mrp/erp/combination?${q}`)
}

export function mrpRencanaPoByCombination(params = {}) {
  const q = new URLSearchParams(params)
  return apiFetch(`/mrp/rencana/po/by-combination?${q}`)
}

export function mrpRencanaPrint(id) {
  return apiFetch(`/mrp/rencana-produksi/${id}/print`)
}

export function mrpGetRencanaItem(itemId) {
  return apiFetch(`/mrp/rencana-produksi/item/${itemId}`)
}

export function mrpRencanaItemBarcode(itemId) {
  return apiFetch(`/mrp/rencana-produksi/item/${itemId}/barcode`)
}

export function mrpRencanaItemListPo(itemId) {
  return apiFetch(`/mrp/rencana-produksi/item/${itemId}/list-po`)
}

export function mrpRencanaItemSavePo(itemId, body) {
  return apiFetch(`/mrp/rencana-produksi/item/${itemId}/list-po`, {
    method: 'POST',
    body: JSON.stringify(body),
  })
}

export function mrpReportPacking(params = {}) {
  const q = new URLSearchParams()
  if (params.start_date) q.set('start_date', params.start_date)
  if (params.end_date) q.set('end_date', params.end_date)
  const suffix = q.toString() ? `?${q}` : ''
  return apiFetch(`/mrp/reports/packing${suffix}`)
}

export function mrpReportPersiapan(params = {}) {
  const q = new URLSearchParams()
  if (params.start_date) q.set('start_date', params.start_date)
  if (params.end_date) q.set('end_date', params.end_date)
  const suffix = q.toString() ? `?${q}` : ''
  return apiFetch(`/mrp/reports/persiapan${suffix}`)
}
