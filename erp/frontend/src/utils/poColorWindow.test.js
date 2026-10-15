import { describe, expect, it } from 'vitest'
import {
  colorWindowSearchQueries,
  fetchColorWindowOptionList,
  pickMatchingColorWindows,
} from './poColorWindow.js'

const collegiate = {
  id: 52,
  brand_code: 'ADIDAS',
  color_code: '024A',
  color_name: 'COLLEGIATE GREEN',
}

describe('color window lookup from line color', () => {
  it('searches the embedded code before the full NAME (CODE) label', () => {
    expect(colorWindowSearchQueries('COLLEGIATE GREEN (024A)')).toEqual([
      '024A',
      'COLLEGIATE GREEN',
    ])
  })

  it('matches master name when the line color includes the code', () => {
    const matched = pickMatchingColorWindows([collegiate], {
      color: 'COLLEGIATE GREEN (024A)',
      colorCode: '024A',
    })
    expect(matched.map((row) => row.id)).toEqual([52])
  })

  it('returns the Adidas window for FG color COLLEGIATE GREEN (024A)', async () => {
    const calls = []
    const items = await fetchColorWindowOptionList({
      formModel: { brand_id: 3, color: 'COLLEGIATE GREEN (024A)' },
      brands: [{ id: 3, code: 'ADIDAS' }],
      listColorWindowsPage: async (params) => {
        calls.push(params.q)
        if (params.brand_code === 'ADIDAS' && params.q === '024A') {
          return { items: [collegiate] }
        }
        return { items: [] }
      },
    })
    expect(calls).toEqual(['024A'])
    expect(items).toEqual([collegiate])
  })
})
