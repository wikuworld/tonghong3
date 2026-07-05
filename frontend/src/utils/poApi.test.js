import { describe, expect, it } from 'vitest'
import { parseApiErrorMessage } from './poApi.js'

describe('parseApiErrorMessage', () => {
  it('returns fallback for empty error', () => {
    expect(parseApiErrorMessage(new Error(''), 'Gagal')).toBe('Gagal')
  })

  it('parses FastAPI detail JSON', () => {
    const err = new Error(JSON.stringify({ detail: 'Token tidak valid' }))
    expect(parseApiErrorMessage(err, 'Gagal')).toBe('Token tidak valid')
  })

  it('returns raw message when not JSON', () => {
    const err = new Error('Network error')
    expect(parseApiErrorMessage(err, 'Gagal')).toBe('Network error')
  })
})
