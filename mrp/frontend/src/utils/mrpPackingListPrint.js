const ROWS_PER_SIDE = 25
const ROLLS_PER_PAGE = ROWS_PER_SIDE * 2

function esc(v) {
  return String(v ?? '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
}

function blank(v) {
  const s = (v == null ? '' : String(v)).trim()
  return s && s !== '-' ? s : ''
}

export function formatIdQty(v) {
  const n = Number(v)
  if (!Number.isFinite(n)) return ''
  const rounded = Math.round(n * 100) / 100
  const text = Number.isInteger(rounded) ? String(rounded) : String(rounded)
  return text.replace('.', ',')
}

export function formatIdWeight(v) {
  if (v == null || v === '') return ''
  const n = Number(v)
  if (!Number.isFinite(n)) return ''
  return n.toFixed(2).replace('.', ',')
}

function roundKg(n) {
  return Math.round(n * 100) / 100
}

/** NW = total SF × 0,11 kg. GW = NW + jumlah roll × 0,3 kg. */
export function packingListWeights(totalQty, totalRolls) {
  const qty = Number(totalQty)
  const rolls = Number(totalRolls)
  const nw = roundKg((Number.isFinite(qty) ? qty : 0) * 0.11)
  const gw = roundKg(nw + (Number.isFinite(rolls) ? rolls : 0) * 0.3)
  return { nw, gw }
}

export function packingListColor(packing) {
  const color = blank(packing?.color)
  const swatch = blank(packing?.color_swatch)
  if (!color && !swatch) return '-'
  if (!color) return swatch
  if (!swatch || color.includes(`(${swatch})`)) return color
  return `${color} (${swatch})`
}

function formatDate(v) {
  const s = blank(v)
  const match = s.match(/^(\d{4}-\d{2}-\d{2})/)
  return match ? match[1] : s || '-'
}

function show(v) {
  return esc(blank(v) || '-')
}

function rollCells(roll) {
  if (!roll) return '<td></td><td></td><td></td>'
  return (
    `<td class="num">${esc(roll.roll_no ?? '')}</td>` +
    `<td class="num">${esc(roll.lembar ?? '')}</td>` +
    `<td class="qty">${esc(formatIdQty(roll.ukuran))}</td>`
  )
}

function pagesOf(rolls) {
  const list = Array.isArray(rolls) ? rolls : []
  if (!list.length) return [[]]
  const pages = []
  for (let i = 0; i < list.length; i += ROLLS_PER_PAGE) {
    pages.push(list.slice(i, i + ROLLS_PER_PAGE))
  }
  return pages
}

function sheetHtml(packing, spec, pageRolls, { withTotal, totalRolls, totalPieces, totalQty, nw, gw }) {
  const lot = blank(spec?.lot_no)
  const rows = []
  for (let i = 0; i < ROWS_PER_SIDE; i += 1) {
    const left = pageRolls[i]
    const right = pageRolls[i + ROWS_PER_SIDE]
    rows.push(`<tr>${rollCells(left)}${rollCells(right)}</tr>`)
  }
  const totalRow = withTotal
    ? `<tr class="total">
        <td>TOTAL</td>
        <td>${esc(totalRolls)} ROLL</td>
        <td>${esc(totalPieces)} PIECES</td>
        <td class="qty">${esc(formatIdQty(totalQty))} SF</td>
        <td>NW: ${esc(formatIdWeight(nw))} KG</td>
        <td>GW: ${esc(formatIdWeight(gw))} KG</td>
      </tr>`
    : ''
  return `<section class="sheet">
    <div class="company">PT TONG HONG TANNERY INDONESIA</div>
    <div class="doc-title">PACKING LIST</div>
    <table class="meta">
      <tr><td class="lbl">CUSTOMER</td><td class="val">${show(packing.customer)}</td><td class="lbl">DATE</td><td class="val">${esc(formatDate(packing.date_created))}</td></tr>
      <tr><td class="lbl">LOT NO.</td><td class="val">${show(lot)}</td><td class="lbl">PO NO.</td><td class="val">${show(packing.no_po)}</td></tr>
      <tr><td class="lbl">THICKNESS</td><td class="val" colspan="3">${show(packing.thickness)}</td></tr>
      <tr><td class="lbl">MATERIAL NAME</td><td class="val" colspan="3">${show(packing.material_name)}</td></tr>
      <tr><td class="lbl">EMBOSS</td><td class="val" colspan="3">${show(packing.emboss)}</td></tr>
      <tr><td class="lbl">COLOR</td><td class="val" colspan="3">${esc(packingListColor(packing))}</td></tr>
    </table>
    <table class="rolls">
      <thead>
        <tr>
          <th>ART. NO</th><th>PIECES</th><th>QUANTITY</th>
          <th>ART. NO</th><th>PIECES</th><th>QUANTITY</th>
        </tr>
      </thead>
      <tbody>${rows.join('')}</tbody>
    </table>
    <table class="totals">${totalRow}</table>
  </section>`
}

export function buildPackingListHtml({ packing = {}, rolls = [], spec = {} } = {}) {
  const pages = pagesOf(rolls)
  const totalRolls = packing.total_rolls ?? rolls.length
  const totalPieces = packing.total_pieces ?? packing.total_lembar ?? rolls.reduce((sum, row) => sum + Number(row.lembar || 0), 0)
  const totalQty = packing.total_quantity ?? packing.total_ukuran ?? rolls.reduce((sum, row) => sum + Number(row.ukuran || 0), 0)
  const { nw, gw } = packingListWeights(totalQty, totalRolls)
  const kode = blank(packing.kode_packing) || 'Packing List'
  const body = pages
    .map((pageRolls, index) =>
      sheetHtml(packing, spec, pageRolls, {
        withTotal: index === pages.length - 1,
        totalRolls,
        totalPieces,
        totalQty,
        nw,
        gw,
      }),
    )
    .join('')
  return `<!DOCTYPE html><html><head><meta charset="utf-8"><title>Packing List - ${esc(kode)}</title>
<style>
@page { size: A4; margin: 10mm; }
* { box-sizing: border-box; }
body { font-family: Arial, Helvetica, sans-serif; font-size: 11px; color: #111; margin: 0; }
.sheet { page-break-after: always; }
.sheet:last-child { page-break-after: auto; }
.company { text-align: center; font-size: 18px; font-weight: 700; letter-spacing: 0.3px; }
.doc-title { text-align: center; font-size: 16px; font-weight: 700; margin: 6px 0 10px; }
table { width: 100%; border-collapse: collapse; }
.meta td { border: 1px solid #111; padding: 3px 6px; vertical-align: middle; }
.meta .lbl { width: 16%; font-weight: 700; white-space: nowrap; }
.meta .val { width: 34%; }
.rolls { margin-top: 8px; }
.rolls th, .rolls td { border: 1px solid #111; padding: 2px 4px; height: 18px; }
.rolls th { text-align: center; font-weight: 700; }
.rolls td.num { text-align: center; width: 10%; }
.rolls td.qty { text-align: right; width: 16%; }
.totals { margin-top: 0; }
.totals td { border: 1px solid #111; padding: 4px 6px; font-weight: 700; }
.totals td.qty { text-align: right; }
</style></head><body>
${body}
<script>window.onload=function(){window.print()}<\/script>
</body></html>`
}

export function printPackingList(data, t) {
  const html = buildPackingListHtml(data)
  const w = window.open('', '_blank')
  if (!w) {
    throw new Error(t?.('pages.mrpPacking.popupBlocked') || 'Popup diblokir')
  }
  w.document.write(html)
  w.document.close()
}
