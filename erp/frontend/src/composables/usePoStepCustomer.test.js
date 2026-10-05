import { describe, expect, it } from 'vitest'
import { pickDefaultBrandId } from './usePoStepCustomer.js'

describe('pickDefaultBrandId', () => {
  it('picks default from array mappings', () => {
    expect(
      pickDefaultBrandId([10, 20], [
        { brand_id: 10, is_default: false },
        { brand_id: 20, is_default: true },
      ]),
    ).toBe(20)
  })

  it('accepts paginated mappings object', () => {
    expect(
      pickDefaultBrandId([10, 20], {
        items: [
          { brand_id: 10, is_default: false },
          { brand_id: 20, is_default: true },
        ],
        total: 2,
        page: 1,
        page_size: 20,
      }),
    ).toBe(20)
  })

  it('falls back to first allowed brand', () => {
    expect(pickDefaultBrandId([10, 20], { items: [] })).toBe(10)
    expect(pickDefaultBrandId([], { items: [] })).toBe(null)
  })
})
