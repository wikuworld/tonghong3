import { describe, expect, it } from 'vitest'
import { buildMrpPackingRollLabelHtml, formatMoisture } from './mrpPackingRollLabelPrint.js'

describe('FG roll label', () => {
  it('prints the sample grid, packing-no barcode, and halal logo beside it', () => {
    const html = buildMrpPackingRollLabelHtml({
      kode_packing: 'PXP260918134101',
      lot_no: 'SYCLR028260917001',
      customer: 'LONG RICH NB',
      no_po: 'ABO2609160003',
      material_name: 'SPLIT SUEDE',
      color: 'CAMBRIDGE BURGUNDY (004-23-16)',
      thickness: '1.2-1.4',
      emboss: '',
      roll_no: 5,
      lembar: 7,
      ukuran: 114.5,
      producing_date: '2026-09-18',
      anti_moldy: 'TCMTB',
      moisture: '10.3',
      impactiva_grading: 'A',
      so_remark: 'REMARK SO',
      sizes_text: '17.6+17.4+20.7',
    })
    expect(html).toContain('PT TONG HONG TANNERY INDONESIA')
    expect(html).toContain('SYCLR028260917001')
    expect(html).toContain('LONG RICH NB')
    expect(html).toContain('PXP260918134101')
    expect(html).toContain('ABO2609160003')
    expect(html).toContain('SPLIT SUEDE')
    expect(html).toContain('CAMBRIDGE BURGUNDY (004-23-16)')
    expect(html).toContain('1.2-1.4')
    expect(html).toContain('2026-09-18')
    expect(html).toContain('TCMTB')
    expect(html).toContain('10,30%')
    expect(html).toContain('114,5')
    expect(html).toContain('>A</td>')
    expect(html).toContain('REMARK SO')
    expect(html).toContain('17.6+17.4+20.7')
    expect(html).toContain('src="/logo-halal.png"')
    expect(html).toContain('class="halal"')
    expect(html).toContain('"PXP260918134101"')
    expect(html).not.toContain('logo-tonghong.png')
    expect(html).not.toContain('工作制令號')
    expect(html).toContain('size: 148mm 105mm')
    const foot = html.split('class="foot"')[1]
    expect(foot.indexOf('pack-barcode')).toBeLessThan(foot.indexOf('logo-halal.png'))
  })

  it('formats moisture with a comma and a percent sign', () => {
    expect(formatMoisture('10,30%')).toBe('10,30%')
    expect(formatMoisture('')).toBe('')
  })
})