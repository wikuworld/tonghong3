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
  const suffix = q.toString() ? `?${q}` : ''
  return apiFetch(`/po${suffix}`)
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

/** Baris outstanding format marketing (join PO header + detail). @param {{ balance_filter?: 'all'|'exclude_zero'|'positive_only', po_q?: string, shipment_status?: 'all'|'sent'|'not_sent' }} params */
export function listMarketingOutstandingLines(params = {}) {
  const q = new URLSearchParams()
  if (params.balance_filter) q.set('balance_filter', params.balance_filter)
  if (params.computed_balance != null) q.set('computed_balance', String(params.computed_balance))
  if (params.po_q && String(params.po_q).trim()) q.set('po_q', String(params.po_q).trim())
  if (params.shipment_status) q.set('shipment_status', params.shipment_status)
  const suffix = q.toString() ? `?${q}` : ''
  return apiFetch(`/marketing/outstanding-lines${suffix}`)
}

export function marketingOutstandingCsvUrl(params = {}) {
  const q = new URLSearchParams()
  if (params.balance_filter) q.set('balance_filter', params.balance_filter)
  if (params.computed_balance != null) q.set('computed_balance', String(params.computed_balance))
  if (params.po_q && String(params.po_q).trim()) q.set('po_q', String(params.po_q).trim())
  if (params.shipment_status) q.set('shipment_status', params.shipment_status)
  const suffix = q.toString() ? `?${q}` : ''
  return `/api/v1/marketing/outstanding-lines.csv${suffix}`
}

/** Path unduhan Excel outstanding (Bearer di frontend saat fetch). */
export function marketingOutstandingXlsxPath(params = {}) {
  const q = new URLSearchParams()
  if (params.balance_filter) q.set('balance_filter', params.balance_filter)
  if (params.computed_balance != null) q.set('computed_balance', String(params.computed_balance))
  if (params.po_q && String(params.po_q).trim()) q.set('po_q', String(params.po_q).trim())
  if (params.shipment_status) q.set('shipment_status', params.shipment_status)
  const suffix = q.toString() ? `?${q}` : ''
  return `/api/v1/marketing/outstanding-lines.xlsx${suffix}`
}

/** Baris delivery list (join surat jalan + produksi + PO) — format lembar marketing. */
export function listMarketingDeliveryLines(params = {}) {
  const q = new URLSearchParams()
  if (params.q && String(params.q).trim()) q.set('q', String(params.q).trim())
  const suffix = q.toString() ? `?${q}` : ''
  return apiFetch(`/marketing/delivery-lines${suffix}`)
}

export function marketingDeliveryCsvUrl(params = {}) {
  const q = new URLSearchParams()
  if (params.q && String(params.q).trim()) q.set('q', String(params.q).trim())
  const suffix = q.toString() ? `?${q}` : ''
  return `/api/v1/marketing/delivery-lines.csv${suffix}`
}

/** Path unduhan Excel delivery list (Bearer lewat fetchAuthenticatedDocument). */
export function marketingDeliveryXlsxPath(params = {}) {
  const q = new URLSearchParams()
  if (params.q && String(params.q).trim()) q.set('q', String(params.q).trim())
  const suffix = q.toString() ? `?${q}` : ''
  return `/api/v1/marketing/delivery-lines.xlsx${suffix}`
}

export function advanceMktWorkflow(poId) {
  return apiFetch(`/po/${poId}/mkt-workflow/advance`, { method: 'POST' })
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

export function replaceBrandBuyers(brandId, buyer_codes) {
  return apiFetch(`/masters/brands/${brandId}/buyers`, {
    method: 'PUT',
    body: JSON.stringify({ buyer_codes }),
  })
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

export function seedBrandsFromBuyers() {
  return apiFetch('/masters/brands/seed-from-buyers', { method: 'POST' })
}

export function listMasterItems() {
  return apiFetch('/masters/items')
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
  const url = marketingOutstandingXlsxPath()
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

export function listMasterPrices() {
  return apiFetch('/masters/prices')
}

export function listCustomerPics() {
  return apiFetch('/masters/customer-pics')
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

export function addProductionDetail(productionId, body) {
  return apiFetch(`/production/${productionId}/details`, { method: 'POST', body: JSON.stringify(body) })
}

export function updateProductionDetail(detailId, body) {
  return apiFetch(`/production-detail/${detailId}`, { method: 'PUT', body: JSON.stringify(body) })
}

// --- QC ---
export function listQc() {
  return apiFetch('/qc')
}

export function getQc(id) {
  return apiFetch(`/qc/${id}`)
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

export function updateQcDetail(detailId, body) {
  return apiFetch(`/qc-detail/${detailId}`, { method: 'PUT', body: JSON.stringify(body) })
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

export function updateDelivery(id, body) {
  return apiFetch(`/delivery/${id}`, { method: 'PUT', body: JSON.stringify(body) })
}

export function markSuratJalanPrinted(deliveryId) {
  return apiFetch(`/delivery/${deliveryId}/mark-surat-jalan-printed`, { method: 'POST' })
}

export function addDeliveryDetail(deliveryId, body) {
  return apiFetch(`/delivery/${deliveryId}/details`, { method: 'POST', body: JSON.stringify(body) })
}

export function updateDeliveryDetail(detailId, body) {
  return apiFetch(`/delivery-detail/${detailId}`, { method: 'PUT', body: JSON.stringify(body) })
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

export function addPackingDetail(packingId, body) {
  return apiFetch(`/packing/${packingId}/details`, { method: 'POST', body: JSON.stringify(body) })
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

export function getInvoice(id) {
  return apiFetch(`/invoice/${id}`)
}

export function listInvoiceDetails(invoiceId) {
  return apiFetch(`/invoice/${invoiceId}/details`)
}

export function createInvoice(body) {
  return apiFetch('/invoice', { method: 'POST', body: JSON.stringify(body) })
}

export function addInvoiceDetail(invoiceId, body) {
  return apiFetch(`/invoice/${invoiceId}/details`, { method: 'POST', body: JSON.stringify(body) })
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

/** @param {File} file - ZIP berisi CSV NN_*.csv */
export function importCustomsZip(file, sourceLabel) {
  const fd = new FormData()
  fd.append('file', file)
  if (sourceLabel) fd.append('source_label', sourceLabel)
  return apiFetch('/customs/declarations/import-zip', { method: 'POST', body: fd })
}

/** @param {File[]} files - semua CSV satu AJU */
export function importCustomsCsvFiles(files, sourceLabel) {
  const fd = new FormData()
  files.forEach((f) => fd.append('files', f))
  if (sourceLabel) fd.append('source_label', sourceLabel)
  return apiFetch('/customs/declarations/import-upload', { method: 'POST', body: fd })
}

// --- Buyer prices ---
export function listBuyerPriceLists() {
  return apiFetch('/buyer-prices/lists')
}

export function getBuyerPriceList(id) {
  return apiFetch(`/buyer-prices/lists/${id}`)
}

/** Sheet list harga untuk buyer (sama struktur dengan GET lists/:id). */
export function getBuyerPriceByBuyer(buyerCode) {
  const code = encodeURIComponent(String(buyerCode || '').trim().toUpperCase())
  return apiFetch(`/buyer-prices/by-buyer/${code}`)
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

export function importBuyerPriceZip(file, sourceLabel) {
  const fd = new FormData()
  fd.append('file', file)
  if (sourceLabel) fd.append('source_label', sourceLabel)
  return apiFetch('/buyer-prices/import-zip', { method: 'POST', body: fd })
}

export function importBuyerPriceCsvFiles(files, sourceLabel) {
  const fd = new FormData()
  files.forEach((f) => fd.append('files', f))
  if (sourceLabel) fd.append('source_label', sourceLabel)
  return apiFetch('/buyer-prices/import-upload', { method: 'POST', body: fd })
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

/** Rekap laporan PO (filter tanggal order atau input) */
export function reportPoDailyRecapUrl(dateStr) {
  const q = dateStr ? `?date=${encodeURIComponent(dateStr)}` : ''
  return `/api/v1/reports/po-daily-recap.csv${q}`
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

export function getSubconInvoice(id) {
  return apiFetch(`/subcon-invoices/${id}`)
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

export function getPoPpicAssignment(poId) {
  return apiFetch(`/workflow/po/${poId}/ppic-assignment`)
}
