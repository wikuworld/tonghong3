import { describe, expect, it } from 'vitest'
import { toIsoDate } from '../api/client.js'
import { detailPayloadForUpdate, sanitizeNewDetailBody } from './poDetailPayload.js'

describe('toIsoDate', () => {
  it('drops the empty-value dash so SO header etd is omitted', () => {
    expect(toIsoDate('—')).toBeNull()
    expect(toIsoDate('2026-09-22')).toBe('2026-09-22')
    expect(toIsoDate('2026-09-22T00:00:00')).toBe('2026-09-22')
  })
})

describe('detailPayloadForUpdate', () => {
  it('keeps unit_price so edit can send the resolved price', () => {
    const out = detailPayloadForUpdate({
      id: 88,
      material_name: 'GENERIC PU COATED',
      unit_price: 1.13,
      color_family: null,
    })
    expect(out.id).toBeUndefined()
    expect(out.unit_price).toBe(1.13)
    expect(out.material_name).toBe('GENERIC PU COATED')
  })
})

describe('sanitize strips item_category', () => {
  it('removes UI-only item_category from create payload', () => {
    const out = sanitizeNewDetailBody({
      id: 1,
      item_category: 'PU',
      _uid: 'draft-1',
      material_name: 'VIRGIN HYDRO PU',
      line_etd: '2026-09-22',
    })
    expect(out.item_category).toBeUndefined()
    expect(out._uid).toBeUndefined()
    expect(out.material_name).toBe('VIRGIN HYDRO PU')
    expect(out.line_etd).toBe('2026-09-22')
  })
})
