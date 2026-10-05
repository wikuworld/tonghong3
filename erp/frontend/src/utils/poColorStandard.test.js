import { describe, expect, it } from 'vitest'
import {
  CSI_STANDARD_LABEL,
  WAITING_CS_LABEL,
  applyCsiColorToForm,
  applyWaitingCsToForm,
  extractColorCodeFromReference,
  hasColorStandardValue,
  inferColorStandardSource,
  isWaitingColorRef,
  matchCsiOption,
} from './poColorStandard.js'

describe('poColorStandard', () => {
  it('detects waiting C/S variants', () => {
    expect(isWaitingColorRef('WAITING C/S')).toBe(true)
    expect(isWaitingColorRef('waiting cs')).toBe(true)
    expect(isWaitingColorRef('Wait C/S')).toBe(true)
    expect(isWaitingColorRef('BLACK (00A)')).toBe(false)
  })

  it('extracts code from NAME (CODE)', () => {
    expect(extractColorCodeFromReference('BLACK (00A)')).toBe('00A')
    expect(extractColorCodeFromReference('00A')).toBe('00A')
    expect(extractColorCodeFromReference('PINKSICLE (6FS) FLUORESCENT')).toBe('6FS')
  })

  it('infers source from persisted line fields', () => {
    expect(inferColorStandardSource({ color_swatch_recipe_id: 9 })).toBe('swatch')
    expect(inferColorStandardSource({ color_reference: 'WAITING C/S' })).toBe('waiting')
    expect(inferColorStandardSource({ color_standard: 'CSI', color_reference: 'BLACK (00A)' })).toBe('csi')
    expect(inferColorStandardSource({ color_reference: 'SAMPLE CUST' })).toBe('manual')
    expect(inferColorStandardSource({})).toBe('')
  })

  it('applies CSI and waiting into form fields', () => {
    const form = { color_reference: '', color_standard: '' }
    const meta = { color_reference: false, color_standard: false }
    applyCsiColorToForm({ color_name: 'BLACK', color_code: '00A' }, form, meta)
    expect(form.color_reference).toBe('BLACK (00A)')
    expect(form.color_standard).toBe(CSI_STANDARD_LABEL)
    applyWaitingCsToForm(form, meta)
    expect(form.color_reference).toBe(WAITING_CS_LABEL)
    expect(form.color_standard).toBe(WAITING_CS_LABEL)
  })

  it('matches CSI option by code or label', () => {
    const options = [
      { id: 1, color_code: '00A', color_name: 'BLACK' },
      { id: 2, color_code: '00C', color_name: 'DARK GREY' },
    ]
    expect(matchCsiOption(options, 'BLACK (00A)')?.id).toBe(1)
    expect(matchCsiOption(options, '00C')?.id).toBe(2)
    expect(matchCsiOption([{ id: 3, color_code: '6FS', color_name: 'PINKSICLE' }], 'PINKSICLE (6FS) FLUORESCENT')?.id).toBe(3)
  })

  it('treats waiting source as complete even before extra fields', () => {
    expect(hasColorStandardValue({}, { source: 'waiting' })).toBe(true)
    expect(hasColorStandardValue({ color_reference: '00A' }, { source: 'manual' })).toBe(false)
    expect(hasColorStandardValue({ color_standard: 'STD-1' }, { source: 'manual' })).toBe(true)
    expect(hasColorStandardValue({ color_standard: 'CSI' }, { source: 'csi' })).toBe(true)
    expect(hasColorStandardValue({}, { source: 'csi' })).toBe(false)
  })
})
