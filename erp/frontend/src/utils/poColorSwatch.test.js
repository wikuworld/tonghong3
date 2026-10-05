import { describe, expect, it } from 'vitest'
import {
  applySwatchRecipeOption,
  compactSwatchColorName,
  normalizeSwatchColorName,
  pickBestSwatchRecipe,
  pickMatchingSwatchRecipes,
  swatchColorsMatch,
} from './poColorSwatch.js'

describe('poColorSwatch matrix match', () => {
  it('treats PINKSICLE fluorescent as PINK SICLE', () => {
    expect(normalizeSwatchColorName('PINKSICLE (6FS) FLUORESCENT')).toBe('pinksicle')
    expect(compactSwatchColorName('PINK SICLE')).toBe('pinksicle')
    expect(swatchColorsMatch('PINKSICLE (6FS) FLUORESCENT', 'PINK SICLE')).toBe(true)
  })

  it('picks factory recipe by CSI code even when emboss differs', () => {
    const options = [
      {
        id: 1,
        material_name: 'VIRGIN HYDRO PU',
        color_name: 'PINK SICLE',
        color_code: '6FS',
        emboss: 'AR-121',
        csi_color_master_id: 623,
        color_standard: 'TMSL0432020012901',
      },
      {
        id: 2,
        material_name: 'VIRGIN HYDRO PU',
        color_name: 'FIRE RED',
        color_code: '64D',
        emboss: 'R-53',
      },
    ]
    const ctx = {
      material: 'VIRGIN HYDRO PU',
      color: 'PINKSICLE (6FS) FLUORESCENT',
      emboss: 'AR-33 M',
    }
    expect(pickMatchingSwatchRecipes(options, { ...ctx, requireEmboss: true })).toEqual([])
    expect(pickBestSwatchRecipe(options, ctx)?.id).toBe(1)
  })

  it('does not attach a recipe when the line identity already differs', () => {
    const formModel = {
      material_name: 'ACTION LEATHER',
      color: 'CORE BLACK (A0QM)',
      emboss: 'AW-44 SG',
      color_standard: '',
      color_reference: '',
      backing: '',
    }
    const selectedSwatchId = { value: null }
    const applied = applySwatchRecipeOption(
      {
        id: 3584,
        material_name: 'GENERIC PU COATED LEATHER',
        color_name: 'ACTIVE PINK',
        color_code: '6HV',
        emboss: 'DE-73',
        color_standard: 'SSL0442024022801',
        backing: 'WHITE',
      },
      {
        formModel,
        autoFieldMeta: { color_standard: false, color_reference: false, backing: false },
        materialFieldOverride: { emboss: false },
        selectedSwatchId,
      },
    )
    expect(applied).toBe(false)
    expect(selectedSwatchId.value).toBeNull()
    expect(formModel.color).toBe('CORE BLACK (A0QM)')
    expect(formModel.emboss).toBe('AW-44 SG')
    expect(formModel.color_standard).toBe('')
    expect(formModel.color_reference).toBe('')
  })

  it('fills an empty form from the recipe', () => {
    const formModel = {
      material_name: '',
      color: '',
      emboss: '',
      color_standard: '',
      color_reference: '',
      backing: '',
    }
    const selectedSwatchId = { value: null }
    const applied = applySwatchRecipeOption(
      {
        id: 9,
        material_name: 'ACTION LEATHER',
        color_name: 'CORE BLACK',
        color_code: 'A0QM',
        emboss: 'AW-44 SG',
        color_standard: 'STD-BLACK',
        backing: 'WHITE',
      },
      {
        formModel,
        autoFieldMeta: { color_standard: false, color_reference: false, backing: false },
        materialFieldOverride: { emboss: false },
        selectedSwatchId,
      },
    )
    expect(applied).toBe(true)
    expect(selectedSwatchId.value).toBe(9)
    expect(formModel.material_name).toBe('ACTION LEATHER')
    expect(formModel.color).toBe('CORE BLACK')
    expect(formModel.emboss).toBe('AW-44 SG')
    expect(formModel.color_standard).toBe('STD-BLACK')
    expect(formModel.color_reference).toBe('A0QM')
  })

  it('keeps the master color code when the recipe code differs', () => {
    const formModel = {
      material_name: 'ACTION LEATHER',
      color: 'CORE BLACK (A0QM)',
      emboss: 'AW-44 SG',
      color_standard: '',
      color_reference: 'A0QM',
      backing: '',
    }
    const applied = applySwatchRecipeOption(
      {
        id: 11,
        material_name: 'ACTION LEATHER',
        color_name: 'CORE BLACK',
        color_code: '6HV',
        emboss: 'AW-44 SG',
        color_standard: 'STD-OTHER',
        backing: 'WHITE',
      },
      {
        formModel,
        autoFieldMeta: { color_standard: false, color_reference: false, backing: false },
        materialFieldOverride: { emboss: false },
        selectedSwatchId: { value: null },
      },
    )
    expect(applied).toBe(true)
    expect(formModel.color_reference).toBe('A0QM')
    expect(formModel.color_standard).toBe('STD-OTHER')
    expect(formModel.backing).toBe('WHITE')
  })
})
