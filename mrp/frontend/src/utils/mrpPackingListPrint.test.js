import { describe, expect, it } from 'vitest'
import { buildPackingListHtml, formatIdQty, formatIdWeight, packingListColor } from './mrpPackingListPrint.js'

function sampleRolls(n) {
  return Array.from({ length: n }, (_, i) => ({
    roll_no: i + 1,
    lembar: 10,
    ukuran: 154.9,
    remark: 'secret-remark',
  }))
}

const packing = {
  kode_packing: 'FG-1',
  customer: 'LONG RICH NB',
  date_created: '2026-09-18T08:00:00',
  no_po: 'ABO2609160003',
  thickness: '1.2-1.4',
  material_name: 'SPLIT SUEDE',
  emboss: '',
  color: 'CAMBRIDGE BURGUNDY',
  color_swatch: '004-23-16',
  total_rolls: 30,
  total_pieces: 300,
  total_quantity: 4647,
  net_weight: 607.02,
  gross_weight: 617.82,
  softness: 'SOFT',
  kode_wip: 'WIP-1',
  form_code: 'QER-48-A/0',
}

describe('packing list FG', () => {
  it('formats quantity with a comma decimal and weight with two decimals', () => {
    expect(formatIdQty(154.9)).toBe('154,9')
    expect(formatIdQty(10539.1)).toBe('10539,1')
    expect(formatIdWeight(607.02)).toBe('607,02')
  })

  it('appends the color swatch once', () => {
    expect(packingListColor(packing)).toBe('CAMBRIDGE BURGUNDY (004-23-16)')
    expect(packingListColor({ color: 'BLACK (004)', color_swatch: '004' })).toBe('BLACK (004)')
    expect(packingListColor({ color: '-', color_swatch: '-' })).toBe('-')
  })

  it('lays out 30 rolls down the left side then the right, without remarks', () => {
    const html = buildPackingListHtml({
      packing,
      rolls: sampleRolls(30),
      spec: { lot_no: 'SYCLR028260917001' },
    })
    expect(html).toContain('PT TONG HONG TANNERY INDONESIA')
    expect(html).toContain('PACKING LIST')
    expect(html).toContain('LONG RICH NB')
    expect(html).toContain('2026-09-18')
    expect(html).toContain('SYCLR028260917001')
    expect(html).toContain('ABO2609160003')
    expect(html).toContain('1.2-1.4')
    expect(html).toContain('SPLIT SUEDE')
    expect(html).toContain('>EMBOSS</td><td class="val" colspan="3">-</td>')
    expect(html).toContain('CAMBRIDGE BURGUNDY (004-23-16)')
    expect(html).not.toContain('Remark')
    expect(html).not.toContain('secret-remark')
    expect(html).not.toContain('QER-48-A/0')
    expect(html).not.toContain('裝貨單')
    expect(html).not.toContain('SOFT')
    expect(html).not.toContain('WIP-1')

    const body = html.split('<tbody>')[1].split('</tbody>')[0]
    const rows = [...body.matchAll(/<tr>([\s\S]*?)<\/tr>/g)].map((m) => m[1])
    expect(rows).toHaveLength(25)
    expect(rows[0]).toContain('>1</td>')
    expect(rows[0]).toContain('>26</td>')
    expect(rows[4]).toContain('>5</td>')
    expect(rows[4]).toContain('>30</td>')
    expect(rows[24]).toContain('>25</td>')
    expect(rows[24]).not.toContain('>50</td>')

    expect(html).toContain('30 ROLL')
    expect(html).toContain('300 PIECES')
    expect(html).toContain('4647 SF')
    expect(html).toContain('NW: 511,17 KG')
    expect(html).toContain('GW: 520,17 KG')
    expect(html).not.toContain('607,02')
    expect(html).not.toContain('617,82')
    expect(html.match(/TOTAL/g)).toHaveLength(1)
  })
})
