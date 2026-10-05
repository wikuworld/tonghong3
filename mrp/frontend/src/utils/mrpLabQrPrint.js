import QRCode from 'qrcode'

function esc(v) {
  return String(v ?? '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
}

export async function lotQrDataUrl(kodeLot) {
  const code = String(kodeLot || '').trim()
  if (!code) return ''
  try {
    return await QRCode.toDataURL(code, {
      width: 220,
      margin: 1,
      errorCorrectionLevel: 'M',
    })
  } catch {
    return ''
  }
}

function buildPrintHtml({ kode, nama, qrDataUrl, title }) {
  const qrImg = qrDataUrl
    ? `<img class="lab-qr" src="${qrDataUrl}" alt="${esc(kode)}" />`
    : `<div class="lab-qr lab-qr--missing">${esc(kode)}</div>`
  const namaLine = nama ? `<div class="lab-nama">${esc(nama)}</div>` : ''
  return `<!DOCTYPE html>
<html lang="id"><head><meta charset="UTF-8"/>
<title>${esc(title)} - ${esc(kode)}</title>
<style>
  @page { size: 60mm 60mm; margin: 0; }
  * { box-sizing: border-box; }
  body {
    font-family: Arial, Helvetica, sans-serif;
    margin: 0;
    padding: 6mm;
    background: #f5f5f5;
  }
  .lab-label {
    width: 48mm;
    margin: 0 auto;
    padding: 4mm 3mm 3mm;
    border: 1px solid #111;
    background: #fff;
    text-align: center;
    page-break-inside: avoid;
  }
  .lab-title {
    font-size: 9px;
    font-weight: 700;
    letter-spacing: 0.04em;
    margin-bottom: 3mm;
    color: #333;
  }
  .lab-qr {
    width: 36mm;
    height: 36mm;
    display: block;
    margin: 0 auto 3mm;
  }
  .lab-qr--missing {
    display: flex;
    align-items: center;
    justify-content: center;
    border: 1px dashed #999;
    font-size: 10px;
    word-break: break-all;
  }
  .lab-kode {
    font-size: 13px;
    font-weight: 700;
    letter-spacing: 0.02em;
    word-break: break-all;
    line-height: 1.25;
  }
  .lab-nama {
    margin-top: 2mm;
    font-size: 9px;
    color: #444;
    line-height: 1.2;
    word-break: break-word;
  }
  .no-print { text-align: center; margin-top: 10px; }
  @media print {
    body { padding: 0; background: #fff; }
    .no-print { display: none; }
    .lab-label { margin: 0; border-width: 1px; }
  }
</style></head><body>
  <div class="lab-label">
    <div class="lab-title">${esc(title)}</div>
    ${qrImg}
    <div class="lab-kode">${esc(kode)}</div>
    ${namaLine}
  </div>
  <p class="no-print"><button type="button" onclick="window.print()">Print</button></p>
</body></html>`
}

/** Buka jendela cetak QR lot warna (isi QR = kode lot). */
export async function printLabLotQr(lot, t) {
  const kode = String(lot?.kode_lot_warna || '').trim()
  if (!kode) {
    throw new Error(t?.('pages.mrpLab.kodeLotRequired') || 'Kode lot kosong')
  }
  const qrDataUrl = await lotQrDataUrl(kode)
  const html = buildPrintHtml({
    kode,
    nama: String(lot?.nama_lot_warna || '').trim(),
    qrDataUrl,
    title: t?.('pages.mrpLab.printQrTitle') || 'LOT WARNA',
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
