/** Parse pesan error dari respons API FastAPI. */

export function parseApiErrorMessage(err, fallback) {
  const raw = String(err?.message || '').trim()
  if (!raw) return fallback
  try {
    const parsed = JSON.parse(raw)
    if (typeof parsed?.detail === 'string') return parsed.detail
  } catch {
    // gunakan raw
  }
  return raw
}
