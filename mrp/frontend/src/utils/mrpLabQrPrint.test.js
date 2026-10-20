import { describe, expect, it } from 'vitest'
import { formatLabProdDate, formatLabWeightKg, labLabelFieldsFromLot } from './mrpLabQrPrint'

describe('mrpLabQrPrint', () => {
  it('formats production date like wireframe', () => {
    expect(formatLabProdDate('2026-10-06')).toBe('06-Oct-26')
  })

  it('formats weight with KG suffix', () => {
    expect(formatLabWeightKg(68)).toBe('68 KG')
    expect(formatLabWeightKg(68.5)).toBe('68.5 KG')
  })

  it('maps lot row to label fields', () => {
    const fields = labLabelFieldsFromLot(
      {
        nama_lot_warna: 'TOP 3',
        total_qty: 68,
        nama_customer: 'Victory',
        color: '10J',
        emboss: 'AR-20',
        date_created: '2026-10-06',
        kode_lot_warna: 'KM20261006003/1',
      },
      { dibuatOleh: 'Yuni / Siti' },
    )
    expect(fields.headerLeft).toBe('TOP 3')
    expect(fields.headerRight).toBe('68 KG')
    expect(fields.customer).toBe('Victory')
    expect(fields.dibuatOleh).toBe('Yuni / Siti')
    expect(fields.kode).toBe('KM20261006003/1')
  })
})
