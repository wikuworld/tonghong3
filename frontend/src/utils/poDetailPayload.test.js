import { describe, expect, it } from 'vitest'
import { detailPayloadForUpdate, sanitizeNewDetailBody } from './poDetailPayload.js'

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
    })
    expect(out.item_category).toBeUndefined()
    expect(out._uid).toBeUndefined()
    expect(out.material_name).toBe('VIRGIN HYDRO PU')
  })
})
