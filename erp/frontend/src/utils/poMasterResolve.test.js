import { describe, expect, it } from 'vitest'
import {
  applyReferenceDefaults,
  detailMasterSnapshot,
  hydrateFormFromMasterItemRow,
  inferColorFamilyFromColor,
  inferItemCategory,
  ITEM_CATEGORY_PU,
  ITEM_CATEGORY_SUEDE,
  normalizeItemCategory,
  resolveMaterialGroupLabel,
} from './poMasterResolve.js'

describe('hydrateFormFromMasterItemRow', () => {
  it('copies color_code into color_reference', () => {
    const formModel = { color_reference: '', color_standard: '', backing: '' }
    const autoFieldMeta = { color_reference: false, color_standard: false, backing: false, softness: false, model: false }
    hydrateFormFromMasterItemRow(
      {
        material_name: 'ACTION LEATHER',
        thickness_range: '1.2-1.4',
        color: 'CORE BLACK (A0QM)',
        emboss: 'AW-44 SG',
        color_code: 'A0QM',
        color_reference: null,
        color_standard: null,
        backing: null,
      },
      { formModel, autoFieldMeta, colorFamilyAutoMode: { value: true } },
    )
    expect(formModel.color_reference).toBe('A0QM')
    expect(formModel.material_name).toBe('ACTION LEATHER')
    expect(formModel.color).toBe('CORE BLACK (A0QM)')
    expect(autoFieldMeta.color_reference).toBe(true)
  })
})

describe('inferColorFamilyFromColor', () => {
  it('treats white / putih as no color addon', () => {
    expect(inferColorFamilyFromColor('WHITE (00A)')).toBeNull()
    expect(inferColorFamilyFromColor('Putih')).toBeNull()
    expect(inferColorFamilyFromColor('snow white')).toBeNull()
  })

  it('detects black and fluorescent', () => {
    expect(inferColorFamilyFromColor('BLACK (00A)')).toBe('black')
    expect(inferColorFamilyFromColor('HITAM')).toBe('black')
    expect(inferColorFamilyFromColor('UNIVERSITY RED (65N) FLUORESCENT')).toBe('fluorescent')
  })

  it('defaults other names to color', () => {
    expect(inferColorFamilyFromColor('UNIVERSITY RED (65N)')).toBe('color')
    expect(inferColorFamilyFromColor('DARK GREY')).toBe('color')
  })

  it('returns null when empty', () => {
    expect(inferColorFamilyFromColor('')).toBeNull()
    expect(inferColorFamilyFromColor(null)).toBeNull()
  })
})

describe('detailMasterSnapshot', () => {
  it('includes emboss so edit re-resolves when emboss changes', () => {
    const a = detailMasterSnapshot({
      material_name: 'GENERIC PU COATED',
      thickness_text: '1.2-1.6',
      color: 'WHITE (00A)',
      emboss: 'UM-34',
      master_item_id: 9,
    })
    const b = detailMasterSnapshot({
      material_name: 'GENERIC PU COATED',
      thickness_text: '1.2-1.6',
      color: 'WHITE (00A)',
      emboss: 'AR-140',
      master_item_id: 9,
    })
    expect(a).toContain('UM-34')
    expect(a).not.toBe(b)
  })
})

describe('applyReferenceDefaults', () => {
  it('does not copy color standard or color reference from a similar item', () => {
    const form = {
      master_item_id: null,
      material_name: 'GENERIC PU COATED',
      color_standard: '',
      color_reference: '',
      backing: '',
    }
    const meta = { color_standard: false, color_reference: false, backing: false }
    applyReferenceDefaults(
      form,
      [
        {
          id: 1,
          material_name: 'GENERIC PU COATED',
          color_standard: 'CSI',
          color_reference: 'BLACK (00A)',
          backing: 'BRUSHED',
        },
      ],
      meta,
    )
    expect(form.color_standard).toBe('')
    expect(form.color_reference).toBe('')
    expect(form.backing).toBe('BRUSHED')
  })
})

describe('item category PU | Suede', () => {
  it('normalizes aliases', () => {
    expect(normalizeItemCategory('suede')).toBe(ITEM_CATEGORY_SUEDE)
    expect(normalizeItemCategory('Suide')).toBe(ITEM_CATEGORY_SUEDE)
    expect(normalizeItemCategory('pu')).toBe(ITEM_CATEGORY_PU)
  })

  it('prefers explicit item_category over material name', () => {
    expect(
      inferItemCategory({
        item_category: 'Suide',
        material_name: 'VIRGIN HYDRO PU',
      }),
    ).toBe(ITEM_CATEGORY_SUEDE)
  })

  it('reads master item category', () => {
    expect(
      inferItemCategory({ master_item_id: 4, material_name: 'X' }, [
        { id: 4, category: 'Suide', material_name: 'SPLIT SUEDE' },
      ]),
    ).toBe(ITEM_CATEGORY_SUEDE)
  })

  it('labels draft rows from item_category', () => {
    expect(resolveMaterialGroupLabel({ item_category: 'PU' })).toBe('PU')
    expect(resolveMaterialGroupLabel({ item_category: 'Suide' })).toBe('Suede')
  })
})
