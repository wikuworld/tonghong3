import { describe, expect, it } from 'vitest'
import { mergeExtraBuyerCodes, normalizePoOrderCategory, poOrderCategoryLabel } from './poList.js'

describe('normalizePoOrderCategory', () => {
  it('maps legacy suede header to production', () => {
    expect(normalizePoOrderCategory('suede')).toBe('production')
    expect(normalizePoOrderCategory('SUEDE')).toBe('production')
    expect(normalizePoOrderCategory('')).toBe('production')
  })

  it('keeps real order types', () => {
    expect(normalizePoOrderCategory('sample')).toBe('sample')
    expect(normalizePoOrderCategory('subcont')).toBe('subcont')
    expect(normalizePoOrderCategory('production')).toBe('production')
  })
})

describe('poOrderCategoryLabel', () => {
  it('labels legacy suede as production', () => {
    const t = (k) => ({ 'status.production': 'Produksi' }[k] || k)
    const te = (k) => k === 'status.production'
    expect(poOrderCategoryLabel('suede', t, te)).toBe('Produksi')
  })
})

describe('mergeExtraBuyerCodes', () => {
  it('merges from array', () => {
    expect(mergeExtraBuyerCodes(['NB'], [{ buyer_code: 'NIKE' }, { buyer_code: 'NB' }])).toEqual([
      'NB',
      'NIKE',
    ])
  })

  it('merges from paginated { items } response', () => {
    expect(
      mergeExtraBuyerCodes(['NB'], { items: [{ buyer_code: 'ADIDAS' }], total: 1 }),
    ).toEqual(['NB', 'ADIDAS'])
  })

  it('tolerates null / non-array', () => {
    expect(mergeExtraBuyerCodes(['NB'], null)).toEqual(['NB'])
    expect(mergeExtraBuyerCodes(['NB'], {})).toEqual(['NB'])
  })
})
