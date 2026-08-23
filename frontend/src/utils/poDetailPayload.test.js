import { describe, expect, it } from 'vitest'
import { detailPayloadForUpdate } from './poDetailPayload.js'

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
