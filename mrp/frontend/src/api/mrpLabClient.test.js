import { afterEach, describe, expect, it, vi } from 'vitest'

import { mrpListLab } from './client.js'

describe('mrpListLab', () => {
  afterEach(() => {
    vi.unstubAllGlobals()
    vi.restoreAllMocks()
  })

  it('mengirim query tab supaya Utama, Terpakai, dan Sisa terpisah', async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      headers: { get: () => 'application/json' },
      json: async () => ({ ok: true, items: [], lots: [], total: 0 }),
    })
    vi.stubGlobal('fetch', fetchMock)
    vi.stubGlobal('localStorage', { getItem: () => null })

    await mrpListLab({ page: 1, page_size: 20, tab: 'terpakai' })

    const url = String(fetchMock.mock.calls[0][0])
    expect(url).toContain('/mrp/lab?')
    expect(url).toContain('tab=terpakai')
  })
})
