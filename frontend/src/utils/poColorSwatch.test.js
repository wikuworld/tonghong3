import { describe, expect, it } from 'vitest'
import {
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
})
