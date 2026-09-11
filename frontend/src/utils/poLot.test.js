import { describe, expect, it } from 'vitest'
import { collectReservedLots, nextLotAfterReserved, parseLotNumber } from './poLot.js'

describe('parseLotNumber', () => {
  it('parses stem + seq', () => {
    expect(parseLotNumber('PUMCS004260604006')).toEqual({
      stem: 'PUMCS004260604',
      seq: 6,
      raw: 'PUMCS004260604006',
    })
  })

  it('returns null for empty', () => {
    expect(parseLotNumber('')).toBeNull()
  })
})

describe('nextLotAfterReserved', () => {
  it('returns peek when no reserved', () => {
    expect(nextLotAfterReserved('PUMCS004260604001', [])).toBe('PUMCS004260604001')
  })

  it('bumps past reserved same stem', () => {
    expect(
      nextLotAfterReserved('PUMCS004260604001', [
        'PUMCS004260604001',
        'PUMCS004260604002',
      ]),
    ).toBe('PUMCS004260604003')
  })

  it('ignores other stems', () => {
    expect(
      nextLotAfterReserved('PUMCS004260604001', ['MYCCS004260604001', 'PUMCS004260604001']),
    ).toBe('PUMCS004260604002')
  })
})

describe('collectReservedLots', () => {
  it('excludes editing index', () => {
    const lines = [{ thi_line_ref: 'A001' }, { thi_line_ref: 'A002' }, { thi_line_ref: 'A003' }]
    expect(collectReservedLots(lines, { excludeIndex: 1 })).toEqual(['A001', 'A003'])
  })
})
