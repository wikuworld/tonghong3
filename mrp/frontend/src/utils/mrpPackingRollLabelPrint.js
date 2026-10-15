function esc(v) {
  return String(v ?? '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
}

function dash(v) {
  const s = (v == null ? '' : String(v)).trim()
  return s || ''
}

function show(v) {
  return esc(dash(v) || '-')
}

export function formatIdQty(v) {
  const n = Number(v)
  if (!Number.isFinite(n)) return ''
  const rounded = Math.round(n * 100) / 100
  const text = Number.isInteger(rounded) ? String(rounded) : String(rounded)
  return text.replace('.', ',')
}

export function formatMoisture(v) {
  const raw = String(v ?? '').trim()
  if (!raw) return ''
  const num = Number(raw.replace('%', '').replace(/\s/g, '').replace(',', '.'))
  if (!Number.isFinite(num)) return raw
  return `${num.toFixed(2).replace('.', ',')}%`
}

function buildSizesText(label) {
  if (label.sizes_text) return label.sizes_text
  const sizes = Array.isArray(label.sizes) ? label.sizes : []
  return sizes
    .map((v) => {
      const n = Number(v)
      if (!Number.isFinite(n)) return ''
      if (Math.abs(n - Math.round(n)) < 1e-9) return String(Math.round(n))
      return String(n)
        .replace(/(\.\d*?[1-9])0+$/, '$1')
        .replace(/\.0+$/, '')
    })
    .filter(Boolean)
    .join('+')
}

function cellPair(labelText, valueHtml, labelText2, valueHtml2) {
  return `<tr>
    <td class="lbl">${esc(labelText)}</td>
    <td class="val">${valueHtml}</td>
    <td class="lbl">${esc(labelText2)}</td>
    <td class="val">${valueHtml2}</td>
  </tr>`
}

export function buildMrpPackingRollLabelHtml(label) {
  if (!label) throw new Error('Label data kosong')
  const sizesText = buildSizesText(label)
  const barcodeValue = dash(label.kode_packing)
  const qty = formatIdQty(label.ukuran)
  const moisture = formatMoisture(label.moisture)
  const emboss = dash(label.emboss) || '-'
  return `<!DOCTYPE html><html><head><meta charset="utf-8"><title>Roll Label - ${esc(barcodeValue)}</title>
<style>
@page { size: 148mm 105mm; margin: 4mm; }
* { box-sizing: border-box; }
body {
  font-family: Arial, Helvetica, sans-serif;
  font-size: 11px;
  color: #111;
  margin: 0;
}
.label-wrap { width: 140mm; margin: 0 auto; border: 1.5px solid #111; }
.company {
  text-align: center;
  font-size: 13px;
  font-weight: 700;
  letter-spacing: 0.2px;
  padding: 3px 6px;
  border-bottom: 1px solid #111;
}
.grid { width: 100%; border-collapse: collapse; table-layout: fixed; }
.grid td { border: 1px solid #111; padding: 2px 5px; vertical-align: middle; height: 6.2mm; }
.grid .lbl { width: 24%; font-weight: 700; }
.grid .val { width: 26%; font-weight: 700; }
.foot {
  display: flex;
  align-items: stretch;
  gap: 6mm;
  padding: 2mm 3mm 1.5mm;
  border-top: 1px solid #111;
  min-height: 28mm;
}
.barcode-box { flex: 1; min-width: 0; display: flex; flex-direction: column; }
.barcode-box svg { width: 100%; max-width: 78mm; height: 22mm; }
.barcode-fallback {
  font-family: "Libre Barcode 128", "Courier New", monospace;
  font-size: 32px;
  line-height: 1;
  letter-spacing: 0;
}
.sizes {
  margin-top: 1mm;
  font-size: 11px;
  font-weight: 700;
  word-break: break-word;
}
.halal {
  width: 28mm;
  display: flex;
  align-items: center;
  justify-content: center;
}
.halal img {
  height: 22mm;
  width: auto;
  max-width: 28mm;
  object-fit: contain;
}
@media print { body { padding: 0; } }
</style>
<link href="https://fonts.googleapis.com/css2?family=Libre+Barcode+128&display=swap" rel="stylesheet">
</head><body>
<div class="label-wrap">
  <div class="company">PT TONG HONG TANNERY INDONESIA</div>
  <table class="grid">
    ${cellPair('Lot No', show(label.lot_no), 'Roll No.', show(label.roll_no))}
    ${cellPair('Customer', show(label.customer), 'Quantity (SF)', show(qty))}
    ${cellPair('Packing No.', show(barcodeValue), 'No. of Piece', show(label.lembar))}
    ${cellPair('PO No.', show(label.no_po), '', '')}
    ${cellPair('Material Name', show(label.material_name), 'Thickness', show(label.thickness))}
    ${cellPair('Color', show(label.color), 'Emboss', esc(emboss))}
    ${cellPair('Production Date', show(label.producing_date), '', '')}
    ${cellPair('Anti Moldy', show(label.anti_moldy || 'TCMTB'), 'Moisture', show(moisture))}
    <tr>
      <td class="lbl">Remark</td>
      <td class="val">${esc(dash(label.impactiva_grading))}</td>
      <td class="val" colspan="2">${esc(dash(label.so_remark))}</td>
    </tr>
  </table>
  <div class="foot">
    <div class="barcode-box">
      <svg id="pack-barcode"></svg>
      <div id="pack-barcode-fallback" class="barcode-fallback" style="display:none">${esc(barcodeValue)}</div>
      <div class="sizes">${esc(sizesText)}</div>
    </div>
    <div class="halal">
      <img src="/logo-halal.png" alt="Halal Indonesia" />
    </div>
  </div>
</div>
<script src="https://cdn.jsdelivr.net/npm/jsbarcode@3.11.6/dist/JsBarcode.all.min.js"><\/script>
<script>
(function(){
  var code = ${JSON.stringify(barcodeValue)};
  var svg = document.getElementById('pack-barcode');
  var fb = document.getElementById('pack-barcode-fallback');
  try {
    if (window.JsBarcode && code) {
      JsBarcode(svg, code, { format: 'CODE128', width: 1.6, height: 64, displayValue: false, margin: 0 });
    } else { throw new Error('no lib'); }
  } catch (e) {
    if (svg) svg.style.display = 'none';
    if (fb) fb.style.display = 'block';
  }
  window.onload = function(){ window.print(); setTimeout(function(){ window.close(); }, 400); };
})();
<\/script>
</body></html>`
}

export function printMrpPackingRollLabel(label, t) {
  const html = buildMrpPackingRollLabelHtml(label)
  const w = window.open('', '_blank')
  if (!w) {
    throw new Error(t?.('pages.mrpPacking.popupBlocked') || 'Popup diblokir')
  }
  w.document.write(html)
  w.document.close()
}
