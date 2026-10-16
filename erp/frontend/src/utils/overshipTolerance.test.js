import { describe, expect, it } from 'vitest'
import { overshipAllowance, withinOvershipTolerance } from './overshipTolerance.js'

describe('overshipTolerance', () => {
  it('allows max(2, 0.5% of order)', () => {
    expect(overshipAllowance(100)).toBe(2)
    expect(overshipAllowance(1200)).toBe(6)
  })

  it('allows 1205 vs balance 1200 when order is 1200', () => {
    expect(withinOvershipTolerance(1205, 1200, 1200)).toBe(true)
  })

  it('rejects large overage', () => {
    expect(withinOvershipTolerance(1210, 1200, 1200)).toBe(false)
  })

  it('allows qty within remaining', () => {
    expect(withinOvershipTolerance(1100, 1200, 1200)).toBe(true)
  })
})
