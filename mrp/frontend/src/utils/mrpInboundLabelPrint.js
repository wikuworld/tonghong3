function esc(v) {
  return String(v ?? '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
}

function text(v) {
  const s = (v == null ? '' : String(v)).trim()
  return s
}

function row(label, value) {
  const shown = text(value)
  if (!shown) return ''
  return `<tr><th>${esc(label)}</th><td>${esc(shown)}</td></tr>`
}

export function buildInboundLabelHtml(labels) {
  const cards = (Array.isArray(labels) ? labels : [labels]).filter(Boolean)
  const pages = cards
    .map((label) => {
      const code = text(label.code) || text(label.kode_internal) || text(label.kode_palet)
      const item = text(label.itemCode) || text(label.kode_yl) || text(label.kode_material)
      const name = text(label.name) || text(label.nama_material)
      return `<section class="label">
        <p class="kicker">Label penerimaan</p>
        <h1>${esc(code || '-')}</h1>
        <table>
          ${row('Barang', [item, name].filter(Boolean).join(' — '))}
          ${row('Qty', label.qty)}
          ${row('Tebal', label.thickness)}
          ${row('Warna', label.color || label.warna)}
          ${row('Bentuk kulit', label.bentuk_kulit)}
          ${row('Skala', label.skala)}
          ${row('Lot', label.lot_number)}
          ${row('Tanggal', label.tanggal)}
          ${row('Supplier', label.supplier_name)}
        </table>
      </section>`
    })
    .join('')
  return `<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8" />
<title>Label penerimaan</title>
<style>
  @page { size: 80mm 50mm; margin: 4mm; }
  body { margin: 0; font-family: Arial, sans-serif; color: #111; }
  .label { page-break-after: always; }
  .label:last-child { page-break-after: auto; }
  .kicker { margin: 0; font-size: 10px; letter-spacing: 0.04em; text-transform: uppercase; }
  h1 { margin: 2px 0 6px; font-size: 18px; }
  table { width: 100%; border-collapse: collapse; font-size: 11px; }
  th { text-align: left; width: 34%; font-weight: 600; padding: 1px 6px 1px 0; vertical-align: top; }
  td { padding: 1px 0; }
</style>
</head>
<body>
${pages}
<script>window.onload = function(){ window.print(); };<\/script>
</body>
</html>`
}

export function optionalUnitPrice(value) {
  const raw = String(value ?? '').trim()
  if (!raw) return null
  const n = Number(raw)
  if (!Number.isFinite(n) || n < 0) return undefined
  return n
}

export function printInboundLabels(labels) {
  const html = buildInboundLabelHtml(labels)
  const w = window.open('', '_blank')
  if (!w) {
    throw new Error('Pop-up diblokir browser — izinkan pop-up untuk situs ini agar label terbuka.')
  }
  w.document.write(html)
  w.document.close()
  return w
}
