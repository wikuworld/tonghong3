/**
 * Panggilan API relatif ke origin (Nginx / Vite proxy → /api/v1).
 */
export async function apiFetch(path, options = {}) {
  const url = path.startsWith('/') ? `/api/v1${path}` : `/api/v1/${path}`
  const isForm = typeof FormData !== 'undefined' && options.body instanceof FormData
  const r = await fetch(url, {
    ...options,
    headers: isForm
      ? { ...options.headers }
      : { 'Content-Type': 'application/json', ...options.headers },
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

export function listPoMktStages() {
  return apiFetch('/po/mkt-workflow-stages')
}

/** Baris outstanding format marketing (join PO header + detail). @param {{ balance_filter?: 'all'|'exclude_zero'|'positive_only' }} params */
export function listMarketingOutstandingLines(params = {}) {
  const q = new URLSearchParams()
  if (params.balance_filter) q.set('balance_filter', params.balance_filter)
  const suffix = q.toString() ? `?${q}` : ''
  return apiFetch(`/marketing/outstanding-lines${suffix}`)
}

export function marketingOutstandingCsvUrl(params = {}) {
  const q = new URLSearchParams()
  if (params.balance_filter) q.set('balance_filter', params.balance_filter)
  const suffix = q.toString() ? `?${q}` : ''
  return `/api/v1/marketing/outstanding-lines.csv${suffix}`
}

/** Baris delivery list (join surat jalan + produksi + PO) — format lembar marketing. */
export function listMarketingDeliveryLines() {
  return apiFetch('/marketing/delivery-lines')
}

export function marketingDeliveryCsvUrl() {
  return '/api/v1/marketing/delivery-lines.csv'
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

// --- Masters ---
export function listBrands() {
  return apiFetch('/masters/brands')
}

export function listMasterItems() {
  return apiFetch('/masters/items')
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
  const suffix = q.toString() ? `?${q}` : ''
  return apiFetch(`/reports/po-order-description${suffix}`)
}

/** Rekap laporan PO (filter tanggal order atau input) */
export function reportPoDailyRecapUrl(dateStr) {
  const q = dateStr ? `?date=${encodeURIComponent(dateStr)}` : ''
  return `/api/v1/reports/po-daily-recap.csv${q}`
}
