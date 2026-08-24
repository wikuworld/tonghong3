import { describe, expect, it } from 'vitest'
import { normalizePoOrderCategory, poOrderCategoryLabel } from './poList.js'

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
