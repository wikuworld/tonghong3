import QRCode from 'qrcode'

/** Ukuran fisik sticker lab (mm). */
export const LAB_LABEL_SIZE_MM = 40

function esc(v) {
  return String(v ?? '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
}

function dash(v) {
  const s = String(v ?? '').trim()
  return s || '—'
}

const MONTHS_EN = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

/** @param {string|Date|null|undefined} v */
export function formatLabProdDate(v) {
  if (v == null || v === '') return '—'
  let d
  if (v instanceof Date) {
    d = v
  } else {
    const s = String(v).trim()
    d = new Date(s.includes('T') ? s : `${s.slice(0, 10)}T12:00:00`)
  }
  if (Number.isNaN(d.getTime())) return dash(v)
  const day = String(d.getDate()).padStart(2, '0')
  const mon = MONTHS_EN[d.getMonth()] || '—'
  const yr = String(d.getFullYear()).slice(-2)
  return `${day}-${mon}-${yr}`
}

/** @param {number|string|null|undefined} totalQty */
export function formatLabWeightKg(totalQty) {
  const n = Number(totalQty)
  if (!Number.isFinite(n)) return '—'
  const text = Number.isInteger(n) ? String(n) : String(Math.round(n * 100) / 100)
  return `${text} KG`
}

/**
 * @param {Record<string, unknown>} lot
 * @param {{ dibuatOleh?: string }} [extra]
 */
export function labLabelFieldsFromLot(lot, extra = {}) {
  const prodDate = lot?.date_created || lot?.tanggal_rencana
  return {
    headerLeft: dash(lot?.nama_lot_warna),
    headerRight: formatLabWeightKg(lot?.total_qty),
    customer: dash(lot?.nama_customer),
    warna: dash(lot?.color),
    emboss: dash(lot?.emboss),
    tglProd: formatLabProdDate(prodDate),
    dibuatOleh: dash(extra.dibuatOleh),
    kode: dash(lot?.kode_lot_warna),
  }
}

export async function lotQrDataUrl(kodeLot) {
  const code = String(kodeLot || '').trim()
  if (!code) return ''
  try {
    return await QRCode.toDataURL(code, {
      width: 160,
      margin: 0,
      errorCorrectionLevel: 'M',
    })
  } catch {
    return ''
  }
}

function metaRow(label, value) {
  return `<tr>
    <td class="meta-lbl">${esc(label)}</td>
    <td class="meta-val">${esc(value)}</td>
  </tr>`
}

function buildPrintHtml({ fields, qrDataUrl, docTitle }) {
  const qrImg = qrDataUrl
    ? `<img class="lab-qr-img" src="${qrDataUrl}" alt="${esc(fields.kode)}" />`
    : `<div class="lab-qr-img lab-qr-img--missing">${esc(fields.kode)}</div>`

  return `<!DOCTYPE html>
<html lang="id"><head><meta charset="UTF-8"/>
<title>${esc(docTitle)} - ${esc(fields.kode)}</title>
<style>
  @page { size: ${LAB_LABEL_SIZE_MM}mm ${LAB_LABEL_SIZE_MM}mm; margin: 0; }
  * { box-sizing: border-box; }
  body {
    font-family: Arial, Helvetica, sans-serif;
    margin: 0;
    padding: 4mm;
    background: #f0f0f0;
    color: #000;
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
  }
  .lab-label {
    width: ${LAB_LABEL_SIZE_MM}mm;
    height: ${LAB_LABEL_SIZE_MM}mm;
    margin: 0 auto;
    border: 0.35mm solid #000;
    background: #fff;
    page-break-inside: avoid;
    overflow: hidden;
  }
  .lab-grid {
    width: 100%;
    height: 100%;
    border-collapse: collapse;
    table-layout: fixed;
  }
  .lab-grid td {
    border: 0.25mm solid #000;
    vertical-align: middle;
    padding: 0;
  }
  .lab-head-left,
  .lab-head-right {
    text-align: center;
    font-weight: 700;
    font-size: 7pt;
    line-height: 1.05;
    padding: 0.4mm 0.3mm;
    height: 8.5mm;
    overflow: hidden;
    word-break: break-word;
  }
  .lab-head-left { width: 50%; }
  .lab-head-right { width: 50%; }
  .lab-body-left {
    width: 50%;
    vertical-align: top;
    height: 31.5mm;
  }
  .lab-body-right {
    width: 50%;
    vertical-align: top;
    height: 31.5mm;
  }
  .meta-table {
    width: 100%;
    height: 100%;
    border-collapse: collapse;
    table-layout: fixed;
    font-size: 4.2pt;
  }
  .meta-table td {
    border: 0.25mm solid #000;
    padding: 0.15mm 0.35mm;
    vertical-align: middle;
    line-height: 1.1;
    overflow: hidden;
  }
  .meta-lbl {
    width: 44%;
    font-weight: 400;
  }
  .meta-val {
    font-weight: 700;
    word-break: break-word;
  }
  .lab-kode-bar {
    text-align: center;
    font-weight: 700;
    font-size: 4.5pt;
    line-height: 1.05;
    padding: 0.2mm 0.3mm;
    border-bottom: 0.25mm solid #000;
    height: 6.3mm;
    max-height: 6.3mm;
    overflow: hidden;
    display: flex;
    align-items: center;
    justify-content: center;
    word-break: break-all;
  }
  .lab-qr-wrap {
    display: flex;
    align-items: center;
    justify-content: center;
    height: 25.2mm;
    padding: 0.4mm;
  }
  .lab-qr-img {
    width: 17mm;
    height: 17mm;
    max-width: 100%;
    max-height: 100%;
    display: block;
    object-fit: contain;
  }
  .lab-qr-img--missing {
    width: 17mm;
    height: 17mm;
    display: flex;
    align-items: center;
    justify-content: center;
    border: 0.25mm dashed #666;
    font-size: 4pt;
    text-align: center;
    word-break: break-all;
  }
  .no-print { text-align: center; margin-top: 10px; }
  @media print {
    html, body {
      width: ${LAB_LABEL_SIZE_MM}mm;
      height: ${LAB_LABEL_SIZE_MM}mm;
      padding: 0;
      margin: 0;
      background: #fff;
    }
    .no-print { display: none; }
    .lab-label {
      margin: 0;
      border-width: 0.35mm;
    }
  }
</style></head><body>
  <div class="lab-label">
    <table class="lab-grid">
      <tr>
        <td class="lab-head-left" colspan="1">${esc(fields.headerLeft)}</td>
        <td class="lab-head-right" colspan="1">${esc(fields.headerRight)}</td>
      </tr>
      <tr>
        <td class="lab-body-left">
          <table class="meta-table">
            ${metaRow('Customer', fields.customer)}
            ${metaRow('Warna', fields.warna)}
            ${metaRow('Emboss', fields.emboss)}
            ${metaRow('Tgl Prod', fields.tglProd)}
            ${metaRow('Dibuat Oleh:', fields.dibuatOleh)}
          </table>
        </td>
        <td class="lab-body-right">
          <div class="lab-kode-bar">${esc(fields.kode)}</div>
          <div class="lab-qr-wrap">${qrImg}</div>
        </td>
      </tr>
    </table>
  </div>
  <p class="no-print"><button type="button" onclick="window.print()">Print</button></p>
</body></html>`
}

/** Buka jendela cetak label lot warna (layout grid + QR). */
export async function printLabLotQr(lot, t, options = {}) {
  const kode = String(lot?.kode_lot_warna || '').trim()
  if (!kode) {
    throw new Error(t?.('pages.mrpLab.kodeLotRequired') || 'Kode lot kosong')
  }
  const fields = labLabelFieldsFromLot(lot, { dibuatOleh: options.dibuatOleh })
  const qrDataUrl = await lotQrDataUrl(kode)
  const html = buildPrintHtml({
    fields,
    qrDataUrl,
    docTitle: t?.('pages.mrpLab.printQrTitle') || 'LOT WARNA',
  })
  const w = window.open('', '_blank')
  if (!w) {
    throw new Error(t?.('pages.mrpProses.popupBlocked') || 'Popup diblokir')
  }
  w.document.write(html)
  w.document.close()
  try {
    w.focus()
    w.print()
  } catch {
    /* ignore */
  }
}
