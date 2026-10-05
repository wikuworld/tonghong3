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

function formatWeight(v) {
  if (v == null || v === '') return ''
  const n = Number(v)
  if (!Number.isFinite(n)) return dash(v)
  return String(n)
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

export function printMrpPackingRollLabel(label, t) {
  if (!label) throw new Error('Label data kosong')
  const sizesText = buildSizesText(label)
  const barcodeValue = dash(label.kode_packing)
  const w = window.open('', '_blank')
  if (!w) {
    throw new Error(t?.('pages.mrpPacking.popupBlocked') || 'Popup diblokir')
  }

  w.document.write(`<!DOCTYPE html><html><head><meta charset="utf-8"><title>Roll Label - ${esc(barcodeValue)}</title>
<style>
@page { size: 100mm 72mm; margin: 3mm; }
* { box-sizing: border-box; }
body {
  font-family: Arial, Helvetica, "Microsoft YaHei", sans-serif;
  font-size: 9px;
  color: #111;
  margin: 0;
  padding: 4px;
}
.label-wrap { width: 94mm; margin: 0 auto; border: 1px solid #111; }
.brand-row {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 4px 6px;
  border-bottom: 1px solid #111;
}
.brand-row img {
  height: 14mm;
  width: auto;
  max-width: 36mm;
  object-fit: contain;
}
.brand-row .brand-text {
  font-size: 9px;
  font-weight: 700;
  line-height: 1.2;
  color: #b91c1c;
}
.label-table { width: 100%; border-collapse: collapse; table-layout: fixed; }
.label-table td {
  border: 1px solid #111;
  padding: 2px 4px;
  vertical-align: middle;
  line-height: 1.15;
  word-break: break-word;
}
.label-head { font-size: 8px; line-height: 1.1; }
.label-head .en { font-size: 8px; }
.label-val { font-size: 10px; font-weight: 700; min-height: 14px; }
.label-val--normal { font-weight: 400; font-size: 9px; }
.col-lbl { width: 22%; }
.col-val { width: 28%; }
.col-lbl-r { width: 18%; }
.col-val-r { width: 32%; }
.lot-row td { padding: 3px 4px; }
.lot-row .label-head { font-size: 9px; }
.lot-row .label-val { font-size: 11px; }
.roll-inline { display: flex; align-items: baseline; gap: 8px; flex-wrap: wrap; }
.roll-inline .sub { font-size: 8px; font-weight: 400; }
.barcode-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 6px;
  padding: 4px 6px 2px;
  border-top: 1px solid #111;
}
.barcode-box { flex: 1; min-width: 0; text-align: center; }
.barcode-box svg { width: 100%; max-width: 62mm; height: 14mm; }
.barcode-fallback {
  font-family: "Libre Barcode 128", "Courier New", monospace;
  font-size: 28px;
  letter-spacing: 0;
  line-height: 1;
}
.md-box { font-size: 8px; white-space: nowrap; padding-right: 2px; }
.sizes-row {
  border-top: 1px solid #111;
  padding: 3px 6px 4px;
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.2px;
  text-align: left;
  min-height: 16px;
}
@media print {
  body { padding: 0; }
}
</style>
<link href="https://fonts.googleapis.com/css2?family=Libre+Barcode+128&display=swap" rel="stylesheet">
</head><body>
<div class="label-wrap">
  <div class="brand-row">
    <img src="/logo-tonghong.png" alt="Tong Hong Tannery" />
    <div class="brand-text">Tong Hong Tannery<br/>PT. TONG HONG TANNERY INDONESIA</div>
  </div>
  <table class="label-table">
    <tr class="lot-row">
      <td colspan="2" class="col-lbl">
        <div class="label-head">工作制令號</div>
        <div class="label-head en">Lot.No.</div>
      </td>
      <td colspan="2" class="col-val-r">
        <div class="label-val">${esc(dash(label.lot_no))}</div>
      </td>
    </tr>
    <tr>
      <td class="col-lbl">
        <div class="label-head">客戶名稱</div>
        <div class="label-head en">Customer</div>
      </td>
      <td class="col-val"><div class="label-val label-val--normal">${esc(dash(label.customer))}</div></td>
      <td class="col-lbl-r">
        <div class="label-head">數量</div>
        <div class="label-head en">Quantity</div>
      </td>
      <td class="col-val-r"><div class="label-val">${esc(dash(label.qty_text || `${label.ukuran || ''} ${label.qty_unit || 'SF'}`.trim()))}</div></td>
    </tr>
    <tr>
      <td class="col-lbl">
        <div class="label-head">包裝單號</div>
        <div class="label-head en">Packing No.</div>
      </td>
      <td class="col-val"><div class="label-val label-val--normal">${esc(dash(label.kode_packing))}</div></td>
      <td class="col-lbl-r">
        <div class="label-head">毛重</div>
        <div class="label-head en">GrossWeight</div>
      </td>
      <td class="col-val-r"><div class="label-val label-val--normal">${esc(formatWeight(label.gross_weight))}</div></td>
    </tr>
    <tr>
      <td class="col-lbl">
        <div class="label-head">訂單指令號</div>
        <div class="label-head en">FactoryProd.Code</div>
      </td>
      <td class="col-val"><div class="label-val label-val--normal">${esc(dash(label.factory_prod_code || label.no_so))}</div></td>
      <td class="col-lbl-r">
        <div class="label-head">淨重</div>
        <div class="label-head en">Net</div>
      </td>
      <td class="col-val-r"><div class="label-val label-val--normal">${esc(formatWeight(label.net_weight))}</div></td>
    </tr>
    <tr>
      <td class="col-lbl">
        <div class="label-head">品名</div>
        <div class="label-head en">Description</div>
      </td>
      <td class="col-val"><div class="label-val label-val--normal">${esc(dash(label.description))}</div></td>
      <td class="col-lbl-r">
        <div class="label-head">量產材料</div>
        <div class="label-head en">Mass</div>
      </td>
      <td class="col-val-r"><div class="label-val label-val--normal">${esc(dash(label.mass_material || label.softness || 'SOFT'))}</div></td>
    </tr>
    <tr>
      <td class="col-lbl">
        <div class="label-head">顏色</div>
        <div class="label-head en">Color</div>
      </td>
      <td class="col-val"><div class="label-val label-val--normal">${esc(dash(label.color))}</div></td>
      <td class="col-lbl-r">
        <div class="label-head">厚度</div>
        <div class="label-head en">Thickness</div>
      </td>
      <td class="col-val-r"><div class="label-val label-val--normal">${esc(dash(label.thickness))}</div></td>
    </tr>
    <tr>
      <td colspan="2">
        <div class="label-head">Roll.No.</div>
        <div class="roll-inline">
          <span class="label-val">${esc(label.roll_no)}</span>
          <span class="sub">張數 ${esc(label.lembar)}</span>
        </div>
      </td>
      <td class="col-lbl-r">
        <div class="label-head">紋路</div>
        <div class="label-head en">Emboss</div>
      </td>
      <td class="col-val-r"><div class="label-val label-val--normal">${esc(dash(label.emboss || '-'))}</div></td>
    </tr>
    <tr>
      <td class="col-lbl">
        <div class="label-head">生產日期</div>
        <div class="label-head en">Producing</div>
      </td>
      <td class="col-val"><div class="label-val label-val--normal">${esc(dash(label.producing_date))}</div></td>
      <td class="col-lbl-r">
        <div class="label-head">有效日期</div>
        <div class="label-head en">Expiration Date</div>
      </td>
      <td class="col-val-r"><div class="label-val label-val--normal">${esc(dash(label.expiration_text || '1 年 (One Year)'))}</div></td>
    </tr>
    <tr>
      <td class="col-lbl">
        <div class="label-head">anti moldy</div>
      </td>
      <td class="col-val"><div class="label-val label-val--normal">${esc(dash(label.anti_moldy))}</div></td>
      <td class="col-lbl-r">
        <div class="label-head">Moisture</div>
      </td>
      <td class="col-val-r"><div class="label-val label-val--normal">${esc(dash(label.moisture))}</div></td>
    </tr>
    <tr>
      <td class="col-lbl">
        <div class="label-head">Remark</div>
      </td>
      <td colspan="3"><div class="label-val label-val--normal">${esc(dash(label.remark))}</div></td>
    </tr>
  </table>
  <div class="barcode-row">
    <div class="barcode-box">
      <svg id="pack-barcode"></svg>
      <div id="pack-barcode-fallback" class="barcode-fallback" style="display:none">${esc(barcodeValue)}</div>
    </div>
    <div class="md-box">□□(MD)=${esc(label.md_code || 'ND')}</div>
  </div>
  <div class="sizes-row">${esc(sizesText)}</div>
</div>
<script src="https://cdn.jsdelivr.net/npm/jsbarcode@3.11.6/dist/JsBarcode.all.min.js"><\/script>
<script>
(function(){
  var code = ${JSON.stringify(barcodeValue)};
  var svg = document.getElementById('pack-barcode');
  var fb = document.getElementById('pack-barcode-fallback');
  try {
    if (window.JsBarcode && code) {
      JsBarcode(svg, code, { format: 'CODE128', width: 1.4, height: 42, displayValue: false, margin: 0 });
    } else { throw new Error('no lib'); }
  } catch (e) {
    if (svg) svg.style.display = 'none';
    if (fb) fb.style.display = 'block';
  }
  window.onload = function(){ window.print(); setTimeout(function(){ window.close(); }, 400); };
})();
<\/script>
</body></html>`)
  w.document.close()
}
