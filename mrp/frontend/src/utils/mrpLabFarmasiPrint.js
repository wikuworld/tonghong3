/** Cetak Instruksi Farmasi / Bahan Kimia (satu lembar per lot warna). */

const MIN_BODY_ROWS = 14

const STYLES = `
  @page { size: A4 portrait; margin: 10mm; }
  * { box-sizing: border-box; }
  body {
    font-family: Arial, Helvetica, "Microsoft YaHei", sans-serif;
    font-size: 11px;
    color: #000;
    margin: 0;
    padding: 8px;
  }
  .farmasi-sheet {
    page-break-after: always;
    max-width: 190mm;
    margin: 0 auto 12px;
  }
  .farmasi-sheet:last-child { page-break-after: auto; }
  .farmasi-title {
    text-align: center;
    font-weight: 700;
    font-size: 14px;
    border: 1px solid #000;
    padding: 6px 4px;
    margin-bottom: -1px;
  }
  .farmasi-meta {
    width: 100%;
    border-collapse: collapse;
    table-layout: fixed;
    margin-bottom: -1px;
  }
  .farmasi-meta td {
    border: 1px solid #000;
    padding: 4px 6px;
    vertical-align: top;
    line-height: 1.35;
  }
  .farmasi-meta .lbl { font-size: 10px; white-space: nowrap; }
  .farmasi-meta .val { font-weight: 700; font-size: 12px; min-height: 18px; }
  .farmasi-meta .date-cell { text-align: right; }
  .farmasi-table {
    width: 100%;
    border-collapse: collapse;
    table-layout: fixed;
    font-size: 11px;
  }
  .farmasi-table th,
  .farmasi-table td {
    border: 1px solid #000;
    padding: 3px 4px;
    vertical-align: middle;
    word-wrap: break-word;
  }
  .farmasi-table th {
    text-align: center;
    font-weight: 700;
    font-size: 10px;
    line-height: 1.25;
  }
  .col-cara { width: 8%; }
  .col-lot { width: 12%; }
  .col-nama { width: 28%; }
  .col-resep { width: 12%; }
  .col-berat { width: 10%; }
  .col-remarks { width: 30%; }
  .num { text-align: right; }
  .center { text-align: center; }
  .farmasi-foot td { font-weight: 700; }
  .farmasi-sign {
    width: 100%;
    border-collapse: collapse;
    margin-top: -1px;
  }
  .farmasi-sign td {
    border: 1px solid #000;
    padding: 6px 8px;
    height: 36px;
    vertical-align: bottom;
  }
  .farmasi-sign .lbl { font-weight: 700; width: 22%; }
  .no-print { text-align: center; margin: 12px; }
  @media print {
    body { padding: 0; }
    .no-print { display: none; }
  }
`

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

function formatResepQty(v) {
  const n = Number(v)
  if (!Number.isFinite(n)) return ''
  return n.toFixed(2)
}

function formatUnit(u) {
  const s = String(u || 'kg').trim().toLowerCase()
  if (s === 'kg' || s === 'kilogram') return 'Kg'
  return s ? s.charAt(0).toUpperCase() + s.slice(1) : 'Kg'
}

function formatPrintDate(d = new Date()) {
  const dt = d instanceof Date && !Number.isNaN(d.getTime()) ? d : new Date()
  const y = dt.getFullYear()
  const m = String(dt.getMonth() + 1).padStart(2, '0')
  const day = String(dt.getDate()).padStart(2, '0')
  return `${y}-${m}-${day}`
}

function refBarcode(kodeLot) {
  const raw = String(kodeLot || '').trim()
  const digits = raw.replace(/\D/g, '')
  return digits || raw || '—'
}

function buildMetaRows(header) {
  const customer = dash(header.nama_customer).toUpperCase()
  const qtyOrder = header.total_qty_so ?? header.total_size ?? ''
  const qtyStr =
    qtyOrder !== '' && qtyOrder != null && Number.isFinite(Number(qtyOrder))
      ? String(Number(qtyOrder))
      : dash(qtyOrder)
  return `
    <table class="farmasi-meta">
      <tr>
        <td colspan="2">
          <div class="lbl">客戶 Customer</div>
          <div class="val">${esc(customer)}</div>
        </td>
        <td colspan="2">
          <div class="lbl">顏色 warna</div>
          <div class="val">${esc(dash(header.color))}</div>
        </td>
        <td class="date-cell" colspan="2">
          <div class="lbl">Tgl 日期：</div>
          <div class="val">${esc(formatPrintDate(header.printDate))}</div>
        </td>
      </tr>
      <tr>
        <td colspan="2">
          <div class="lbl">訂單尺量 Quantity Order</div>
          <div class="val">${esc(qtyStr)}</div>
        </td>
        <td colspan="2">
          <div class="lbl">紋路 Emboss</div>
          <div class="val">${esc(dash(header.emboss))}</div>
        </td>
        <td colspan="2">
          <div class="lbl">Nama lot warna</div>
          <div class="val">${esc(dash(header.nama_lot_warna))}</div>
        </td>
      </tr>
      <tr>
        <td colspan="3">
          <div class="lbl">色卡編號 Nomor Colour Swatch</div>
          <div class="val">${esc(dash(header.color_swatch))}</div>
        </td>
        <td colspan="2">
          <div class="lbl">粘度 Kelekatan</div>
          <div class="val">${esc(dash(header.kelekatan))}</div>
        </td>
        <td>
          <div class="lbl">Kode LW</div>
          <div class="val">${esc(dash(header.kode_lot_warna))}</div>
        </td>
      </tr>
    </table>`
}

function buildItemRows(items, lotRemarks) {
  const rows = (items || []).map((it, idx) => {
    const remarks =
      (it.remarks || '').trim() ||
      (idx === 0 && lotRemarks ? String(lotRemarks).trim() : '')
    return `
      <tr>
        <td class="center">${esc(it.cara || '')}</td>
        <td class="center">${esc(dash(it.lot_number))}</td>
        <td>${esc(dash(it.nama_kimia || it.kode_kimia))}</td>
        <td class="num">${esc(formatResepQty(it.qty))}</td>
        <td class="center">${esc(formatUnit(it.satuan))}</td>
        <td>${esc(dash(remarks))}</td>
      </tr>`
  })
  const empty = Math.max(0, MIN_BODY_ROWS - rows.length)
  for (let i = 0; i < empty; i += 1) {
    rows.push('<tr><td></td><td></td><td></td><td></td><td></td><td></td></tr>')
  }
  rows.push(`
    <tr>
      <td class="center"><strong>TUANG:</strong></td>
      <td></td><td></td><td></td><td></td><td></td>
    </tr>
    <tr>
      <td class="center"><strong>TGL:</strong></td>
      <td></td><td></td><td></td><td></td><td></td>
    </tr>
    <tr>
      <td class="center"><strong>MIX TGL:</strong></td>
      <td></td><td></td><td></td><td></td><td></td>
    </tr>`)
  return rows.join('')
}

function sumQty(items) {
  let total = 0
  let unit = 'kg'
  for (const it of items || []) {
    const q = Number(it.qty)
    if (Number.isFinite(q)) total += q
    if (it.satuan) unit = it.satuan
  }
  return { total, unit }
}

function buildSheetHtml(sheet) {
  const header = sheet.header || {}
  const items = sheet.items || []
  const { total, unit } = sumQty(items)
  const totalLabel = `${formatResepQty(total)} ${formatUnit(unit)}`
  const ref = refBarcode(header.kode_lot_warna || sheet.kode_lot_warna)

  return `
    <section class="farmasi-sheet">
      <div class="farmasi-title">配藥指令 / Instruksi Farmasi / Bahan Kimia</div>
      ${buildMetaRows({ ...header, nama_lot_warna: sheet.nama_lot_warna, kode_lot_warna: sheet.kode_lot_warna })}
      <table class="farmasi-table">
        <thead>
          <tr>
            <th class="col-cara">Cara<br/>做法</th>
            <th class="col-lot">Lot No.<br/>化料編號</th>
            <th class="col-nama">Nama Chemical<br/>化料名稱</th>
            <th class="col-resep">Resep<br/>配方</th>
            <th class="col-berat">Berat<br/>單位</th>
            <th class="col-remarks">Remarks<br/>備註</th>
          </tr>
        </thead>
        <tbody>
          ${buildItemRows(items, sheet.catatan)}
          <tr class="farmasi-foot">
            <td colspan="3" class="center">Total</td>
            <td class="num">${esc(formatResepQty(total))}</td>
            <td class="center">${esc(formatUnit(unit))}</td>
            <td class="num">${esc(ref)}</td>
          </tr>
        </tbody>
      </table>
      <table class="farmasi-sign">
        <tr>
          <td class="lbl">Pembuat<br/>配藥人 Pembuat</td>
          <td>${esc(dash(sheet.pembuat))}</td>
          <td class="lbl">disetujui<br/>核準人 disetujui</td>
          <td>${esc(dash(sheet.disetujui))}</td>
        </tr>
      </table>
    </section>`
}

function buildDocumentHtml(sheets, docTitle) {
  const body = (sheets || []).map((s) => buildSheetHtml(s)).join('')
  return `<!DOCTYPE html>
<html lang="id"><head><meta charset="UTF-8"/>
<title>${esc(docTitle)}</title>
<style>${STYLES}</style></head>
<body>
${body}
<p class="no-print"><button type="button" onclick="window.print()">Print</button></p>
</body></html>`
}

/**
 * @param {Array<{ kode_lot_warna, nama_lot_warna, catatan?, items, header?, pembuat?, disetujui? }>} sheets
 */
export function printLabFarmasiInstructions(sheets, options = {}) {
  const list = (sheets || []).filter((s) => s && (s.items?.length || s.nama_lot_warna))
  if (!list.length) return false
  const title = options.title || 'Instruksi Farmasi / Bahan Kimia'
  const html = buildDocumentHtml(list, title)
  const w = window.open('', '_blank')
  if (!w) {
    throw new Error(options.popupBlockedMessage || 'Popup diblokir — izinkan popup untuk cetak.')
  }
  w.document.write(html)
  w.document.close()
  try {
    w.focus()
    w.print()
  } catch {
    /* user can click Print */
  }
  return true
}

export function buildFarmasiSheetsFromCreate({
  colorLots,
  kodeList,
  rencanaItem,
  resolveKimiaName,
  resolveStockLot,
  pembuat,
}) {
  const rpi = rencanaItem || {}
  const headerBase = {
    nama_customer: rpi.nama_customer,
    color: rpi.color,
    emboss: rpi.emboss,
    color_swatch: rpi.color_swatch,
    total_qty_so: rpi.total_qty_so,
    total_size: rpi.total_size,
    kelekatan: rpi.treatment_jenis || rpi.keterangan || '—',
    printDate: new Date(),
  }
  return (colorLots || []).map((lot, index) => {
    const kode_lot_warna = (kodeList && kodeList[index]) || lot.kode_lot_warna || ''
    const items = (lot.items || []).map((row) => {
      const stock = resolveStockLot?.(row.stok_in_id, row)
      const kode = (row.kode_kimia || stock?.kode_kimia || '').trim()
      return {
        kode_kimia: kode,
        lot_number: (row.lot_number || stock?.lot_number || '').trim(),
        nama_kimia: (stock?.nama_kimia || resolveKimiaName?.(kode) || kode).trim(),
        qty: Number(row.qty),
        satuan: row.satuan || stock?.satuan || 'kg',
        remarks: row.remarks || '',
        cara: row.cara || row.resep || '',
      }
    })
    return {
      kode_lot_warna,
      nama_lot_warna: lot.nama_lot_warna,
      catatan: lot.catatan,
      pembuat: pembuat || '',
      disetujui: '—',
      header: { ...headerBase, kode_lot_warna },
      items,
    }
  })
}
