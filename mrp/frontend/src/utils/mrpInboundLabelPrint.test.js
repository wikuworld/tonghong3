import { describe, expect, it } from 'vitest'
import { buildInboundLabelHtml } from './mrpInboundLabelPrint.js'

describe('label penerimaan', () => {
  it('memuat kode dan supplier, tanpa harga', () => {
    const html = buildInboundLabelHtml({
      code: 'BC-R-261022001',
      itemCode: 'RP-01',
      name: 'Release Paper',
      qty: '120',
      lot_number: 'LOT-9',
      tanggal: '2026-10-22',
      supplier_name: 'PT Kulit Jaya',
      unit_price: '12345.67',
    })
    expect(html).toContain('BC-R-261022001')
    expect(html).toContain('PT Kulit Jaya')
    expect(html).toContain('RP-01')
    expect(html).not.toContain('12345.67')
    expect(html).not.toContain('unit_price')
  })

  it('mencetak bentuk kulit dan skala pada label crust', () => {
    const html = buildInboundLabelHtml({
      code: 'KY-1001',
      itemCode: 'MCL-2EP-102',
      qty: '10',
      thickness: '1.02',
      color: 'LIGHT BROWN',
      bentuk_kulit: 'Utuh',
      skala: 'A',
      supplier_name: 'Supplier A',
    })
    expect(html).toContain('KY-1001')
    expect(html).toContain('MCL-2EP-102')
    expect(html).toContain('Utuh')
    expect(html).toContain('>A</td>')
    expect(html).toContain('Supplier A')
  })
})
