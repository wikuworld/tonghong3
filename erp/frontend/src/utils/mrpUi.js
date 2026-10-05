/** Origin UI MRP shopfloor (UAT default :8082). */
function isLoopbackHost(hostname) {
  const h = String(hostname || '').toLowerCase()
  return h === '127.0.0.1' || h === 'localhost' || h === '::1'
}

export function mrpUiOrigin() {
  const fromEnv = String(import.meta.env.VITE_MRP_UI_ORIGIN || '')
    .trim()
    .replace(/\/$/, '')

  if (typeof window !== 'undefined' && window.location?.hostname) {
    const { protocol, hostname } = window.location
    const sameHost = `${protocol}//${hostname}:8082`

    if (fromEnv) {
      try {
        const envHost = new URL(fromEnv).hostname
        // Env localhost tidak dipakai saat user buka ERP lewat IP/domain remote.
        if (isLoopbackHost(envHost) && !isLoopbackHost(hostname)) {
          return sameHost
        }
      } catch {
        /* ignore invalid env URL */
      }
      return fromEnv
    }
    return sameHost
  }

  return fromEnv || 'http://127.0.0.1:8082'
}

export function mrpUiUrl(path = '/') {
  const p = path.startsWith('/') ? path : `/${path}`
  return `${mrpUiOrigin()}${p}`
}
