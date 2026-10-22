import { afterEach, describe, expect, it, vi } from 'vitest'

import {
  fetchAuthenticatedDocument,
  proformaInvoiceBatchDocxPath,
  proformaInvoiceBatchPdfPath,
} from './client.js'

function stubDownloadEnv(fetchImpl) {
  vi.stubGlobal('fetch', fetchImpl)
  vi.stubGlobal('localStorage', { getItem: () => 'tok' })
  vi.stubGlobal('URL', {
    createObjectURL: () => 'blob:pi',
    revokeObjectURL: () => {},
  })
  vi.stubGlobal('document', {
    createElement: () => ({
      href: '',
      download: '',
      click: () => {},
    }),
  })
}

describe('proforma invoice batch paths', () => {
  it('uses API-relative paths (bukan /api/v1 ganda)', () => {
    expect(proformaInvoiceBatchPdfPath()).toBe('/documents/proforma-invoice/batch/pdf')
    expect(proformaInvoiceBatchDocxPath()).toBe('/documents/proforma-invoice/batch/docx')
  })
})

describe('fetchAuthenticatedDocument', () => {
  afterEach(() => {
    vi.unstubAllGlobals()
    vi.restoreAllMocks()
  })

  it('mengirim POST + JSON body untuk cetak PI batch', async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      blob: async () => new Blob(['%PDF'], { type: 'application/pdf' }),
      headers: {
        get: (k) => (String(k).toLowerCase() === 'content-disposition' ? 'attachment; filename="pi.pdf"' : ''),
      },
    })
    stubDownloadEnv(fetchMock)

    await fetchAuthenticatedDocument(proformaInvoiceBatchPdfPath(), {
      mode: 'download',
      method: 'POST',
      body: { po_ids: [12], po_detail_ids: [34] },
      downloadFallbackName: 'pi.pdf',
    })

    expect(fetchMock).toHaveBeenCalledTimes(1)
    const [url, init] = fetchMock.mock.calls[0]
    expect(url).toBe('/api/v1/documents/proforma-invoice/batch/pdf')
    expect(init.method).toBe('POST')
    expect(init.body).toBe(JSON.stringify({ po_ids: [12], po_detail_ids: [34] }))
    expect(init.headers['Content-Type']).toBe('application/json')
    expect(init.headers.Authorization).toBe('Bearer tok')
  })

  it('tetap GET tanpa body untuk dokumen tunggal', async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      blob: async () => new Blob(['%PDF'], { type: 'application/pdf' }),
      headers: { get: () => '' },
    })
    stubDownloadEnv(fetchMock)

    await fetchAuthenticatedDocument('/documents/proforma-invoice/12/pdf', {
      mode: 'download',
      downloadFallbackName: 'pi.pdf',
    })

    const [url, init] = fetchMock.mock.calls[0]
    expect(url).toBe('/api/v1/documents/proforma-invoice/12/pdf')
    expect(init.method).toBe('GET')
    expect(init.body).toBeUndefined()
    expect(init.headers['Content-Type']).toBeUndefined()
  })

  it('membuka tab sebelum fetch selesai', async () => {
    let fetchStarted = false
    const popup = { closed: false, location: { href: '' } }
    const open = vi.fn(() => {
      if (fetchStarted) throw new Error('tab dibuka setelah fetch')
      return popup
    })
    const fetchMock = vi.fn().mockImplementation(async () => {
      fetchStarted = true
      return {
        ok: true,
        blob: async () => new Blob(['<html></html>'], { type: 'text/html' }),
        headers: { get: () => '' },
      }
    })
    stubDownloadEnv(fetchMock)
    vi.stubGlobal('window', { open })

    await fetchAuthenticatedDocument('/documents/surat-jalan/13', { mode: 'open' })

    expect(open).toHaveBeenCalledWith('about:blank', '_blank')
    expect(popup.location.href).toBe('blob:pi')
  })
})
