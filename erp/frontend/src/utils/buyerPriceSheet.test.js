import { describe, expect, it } from 'vitest'

import {
  applyItemSelection,
  missingAddonsForRow,
  missingRequiredPricesForRow,
  thicknessOptionsForMaterial,
  uniqueMaterialNames,
} from './buyerPriceSheet.js'

const items = [
  { material_name: 'VIRGIN HYDRO PU', thickness_range: '1.2-1.4' },
  { material_name: 'VIRGIN HYDRO PU', thickness_range: '1.4-1.6' },
  { material_name: 'VIRGIN HYDRO PU', thickness_range: '1.2-1.4' },
  { material_name: 'ECO TECH COMFORT', thickness_range: '1.0-1.2' },
]

describe('uniqueMaterialNames', () => {
  it('keeps one option per material name', () => {
    expect(uniqueMaterialNames(items)).toEqual(['ECO TECH COMFORT', 'VIRGIN HYDRO PU'])
  })
})

describe('thicknessOptionsForMaterial', () => {
  it('returns each range of that material once', () => {
    expect(thicknessOptionsForMaterial(items, 'VIRGIN HYDRO PU')).toEqual(['1.2-1.4', '1.4-1.6'])
  })
})

describe('missingAddonsForRow', () => {
  const flagged = [
    {
      material_name: 'VIRGIN HYDRO PU',
      thickness_range: '1.2-1.4',
      flag_color_black: true,
      flag_color: false,
    },
    {
      material_name: 'VIRGIN HYDRO PU',
      thickness_range: '1.2-1.4',
      flag_flourasent: true,
    },
  ]

  it('treats 0 as entered and only flags a blank add-on', () => {
    expect(
      missingAddonsForRow(
        { ITEM: 'virgin hydro pu', THICKNESS: '1.2-1.4', 'COLOR BLACK': 0, FLOURASENT: '' },
        flagged,
      ),
    ).toEqual(['FLOURASENT'])
  })

  it('returns nothing when flags are off or the thickness does not match', () => {
    expect(missingAddonsForRow({ ITEM: 'VIRGIN HYDRO PU', THICKNESS: '1.4-1.6' }, flagged)).toEqual([])
    expect(
      missingAddonsForRow({ ITEM: 'VIRGIN HYDRO PU', THICKNESS: '1.2-1.4', 'COLOR COLOR': '' }, [
        { material_name: 'VIRGIN HYDRO PU', thickness_range: '1.2-1.4' },
      ]),
    ).toEqual([])
  })
})

describe('missingRequiredPricesForRow', () => {
  it('requires only COLOR WHITE above 0 when the item is set', () => {
    expect(
      missingRequiredPricesForRow({
        ITEM: 'VIRGIN HYDRO PU',
        THICKNESS: '1.2-1.4',
        'COLOR WHITE': 0,
        'COLOR BLACK': 0,
      }),
    ).toEqual(['COLOR WHITE'])
    expect(
      missingRequiredPricesForRow({
        ITEM: 'VIRGIN HYDRO PU',
        'COLOR WHITE': 1.2,
        'COLOR BLACK': 0,
      }),
    ).toEqual([])
  })

  it('skips a blank row', () => {
    expect(missingRequiredPricesForRow({ ITEM: '', 'COLOR WHITE': '' }, [])).toEqual([])
  })
})

describe('applyItemSelection', () => {
  it('does not change COLOR and clears a thickness from another material', () => {
    const row = { ITEM: '', THICKNESS: '1.0-1.2', COLOR: 'SPECIAL' }
    const next = applyItemSelection(row, 'VIRGIN HYDRO PU', items)
    expect(next.ITEM).toBe('VIRGIN HYDRO PU')
    expect(next.THICKNESS).toBe('')
    expect(next.COLOR).toBe('SPECIAL')
    expect(row.COLOR).toBe('SPECIAL')
  })

  it('locks the only thickness range', () => {
    const next = applyItemSelection({ COLOR: '' }, 'ECO TECH COMFORT', items)
    expect(next.THICKNESS).toBe('1.0-1.2')
    expect(next.COLOR).toBe('')
  })
})
