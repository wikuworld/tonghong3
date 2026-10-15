const MIN_ROWS = 18
const DAY_ID = ['SENIN', 'SELASA', 'RABU', 'KAMIS', 'JUMAT', 'SABTU', 'MINGGU']
const MONTH_SHORT = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

const PRINT_STYLES = `
  body { font-family: Arial, Helvetica, sans-serif; margin: 12px; font-size: 12px; color: #000; }
  .rp-plan-header { margin-bottom: 8px; }
  .rp-plan-header__row { display: flex; gap: 8px; align-items: baseline; margin-bottom: 2px; }
  .rp-plan-header__label { font-weight: 700; min-width: 170px; }
  .rp-plan-header__value { font-weight: 700; }
  .rp-date-row { display: flex; gap: 0; }
  .rp-date-box, .rp-day-box { border: 1px solid #000; padding: 6px 16px; font-weight: 700; min-width: 80px; text-align: center; }
  .rp-table { width: 100%; border-collapse: collapse; table-layout: fixed; font-size: 11px; margin-top: -1px; }
  .rp-table th, .rp-table td { border: 1px solid #000; padding: 3px 5px; vertical-align: middle; word-wrap: break-word; }
  .rp-table th { text-align: center; font-weight: 700; }
  .rp-col-rpi { width: 11%; } .rp-col-emboss { width: 8%; } .rp-col-customer { width: 13%; }
  .rp-col-color { width: 11%; } .rp-col-qty { width: 7%; } .rp-col-cs { width: 12%; }
  .rp-col-backer { width: 8%; } .rp-col-kode { width: 8%; }
  .rp-col-schedule { width: 11%; } .rp-col-remarks { width: 11%; }
  .rp-center { text-align: center; }
  .rp-sign { border-collapse: collapse; width: 220px; font-size: 11px; margin-top: 0; }
  .rp-sign td { border: 1px solid #000; padding: 4px 8px; height: 24px; }
  .rp-sign td:first-child { font-weight: 700; width: 70px; }
  @media print { @page { margin: 10mm; } }
`

function escapeHtml(value) {
  return String(value ?? '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
}

function parsePlanDate(rencana) {
  const raw = rencana?.tanggal_rencana || rencana?.date_created
  if (!raw) return null
  const d = new Date(raw)
  return Number.isNaN(d.getTime()) ? null : d
}

function formatCustomer(name) {
  return (name || '').toUpperCase()
}

function formatQtyCell(v) {
  if (v == null || v === '') return ''
  const n = Number(v)
  if (!Number.isFinite(n)) return ''
  return Number.isInteger(n) ? String(n) : String(n)
}

function buildTableRows(items) {
  const rows = (items || []).map((item) => {
    return `
      <tr>
        <td class="rp-center">${escapeHtml(item.kode_rencana_item || '')}</td>
        <td class="rp-center">${escapeHtml(item.emboss || '')}</td>
        <td>${escapeHtml(formatCustomer(item.nama_customer))}</td>
        <td>${escapeHtml(item.color || '')}</td>
        <td class="rp-center">${escapeHtml(formatQtyCell(item.print_qty))}</td>
        <td>${escapeHtml(item.color_swatch || '')}</td>
        <td class="rp-center">${escapeHtml(item.backer || '')}</td>
        <td class="rp-center">${escapeHtml(item.kode_kulit || '')}</td>
        <td class="rp-center">${escapeHtml((item.print_schedule || '').trim())}</td>
        <td>${escapeHtml((item.print_remarks || '').trim())}</td>
      </tr>`
  })
  const emptyCount = Math.max(0, MIN_ROWS - rows.length)
  for (let i = 0; i < emptyCount; i += 1) {
    rows.push('<tr><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td></tr>')
  }
  return rows.join('')
}

function dateBoxLabel(planDate) {
  if (!planDate) return '-'
  return `${planDate.getDate()}-${MONTH_SHORT[planDate.getMonth()]}`
}

function dayBoxLabel(planDate) {
  if (!planDate) return '-'
  const jsDay = planDate.getDay()
  const pyIdx = jsDay === 0 ? 6 : jsDay - 1
  return DAY_ID[pyIdx] || '-'
}

function buildPrintHtml(data, labels) {
  const rencana = data?.rencana || {}
  const planDate = parsePlanDate(rencana)
  const title = escapeHtml(rencana.nama_rencana || labels.title || 'Rencana Produksi')
  return `<!DOCTYPE html>
<html lang="id">
<head>
  <meta charset="UTF-8" />
  <title>${title}</title>
  <style>${PRINT_STYLES}</style>
</head>
<body>
  <div class="mrp-rp-print">
    <div class="rp-plan-header">
      <div class="rp-plan-header__row">
        <span class="rp-plan-header__label">${escapeHtml(labels.planName)}</span>
        <span class="rp-plan-header__value">${escapeHtml(rencana.nama_rencana || '—')}</span>
      </div>
      <div class="rp-plan-header__row">
        <span class="rp-plan-header__label">${escapeHtml(labels.planNo)}</span>
        <span class="rp-plan-header__value">${escapeHtml(rencana.kode_rencana || '—')}</span>
      </div>
    </div>
    <div class="rp-date-row">
      <div class="rp-date-box">${escapeHtml(dateBoxLabel(planDate))}</div>
      <div class="rp-day-box">${escapeHtml(dayBoxLabel(planDate))}</div>
    </div>
    <table class="rp-table">
      <thead>
        <tr>
          <th class="rp-col-rpi">${escapeHtml(labels.kodeRpi)}</th>
          <th class="rp-col-emboss">${escapeHtml(labels.emboss)}</th>
          <th class="rp-col-customer">${escapeHtml(labels.customer)}</th>
          <th class="rp-col-color">${escapeHtml(labels.color)}</th>
          <th class="rp-col-qty">${escapeHtml(labels.qty)}</th>
          <th class="rp-col-cs">${escapeHtml(labels.cs)}</th>
          <th class="rp-col-backer">${escapeHtml(labels.backer)}</th>
          <th class="rp-col-kode">${escapeHtml(labels.kode)}</th>
          <th class="rp-col-schedule">${escapeHtml(labels.schedule)}</th>
          <th class="rp-col-remarks">${escapeHtml(labels.remarks)}</th>
        </tr>
      </thead>
      <tbody>${buildTableRows(data?.items)}</tbody>
    </table>
    <table class="rp-sign">
      <tr><td>TTD</td><td></td></tr>
      <tr><td>PKULIT</td><td></td></tr>
      <tr><td>WARNA</td><td></td></tr>
      <tr><td>MPU</td><td></td></tr>
    </table>
  </div>
  <script>
    window.addEventListener('load', function () {
      window.focus();
      window.print();
    });
  <\/script>
</body>
</html>`
}

export function buildMrpRencanaPrintHtml(data, labels) {
  return buildPrintHtml(data, labels)
}

export async function printMrpRencana(data, labels) {
  const html = buildPrintHtml(data, labels)
  const printWindow = window.open('', '_blank')
  if (!printWindow) {
    throw new Error('Popup diblokir browser. Izinkan popup untuk cetak.')
  }
  printWindow.document.open()
  printWindow.document.write(html)
  printWindow.document.close()
}
