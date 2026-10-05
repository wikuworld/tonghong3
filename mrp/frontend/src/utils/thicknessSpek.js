/** Parity dengan mrp/backend/legacy/spek_match.py (YL vs spek rencana). */

const THICKNESS_RANGE_RE = /^\s*([\d.]+)\s*[-–]\s*([\d.]+)\s*$/

export function canonicalThickness(text) {
  const raw = String(text ?? '')
    .trim()
    .replace(/mm/gi, '')
    .trim()
  if (!raw || raw === '-' || raw === '—' || raw === '–') return ''
  const m = THICKNESS_RANGE_RE.exec(raw)
  if (m) return `${m[1]}-${m[2]}`
  return raw
}

export function thicknessMatches(a, b) {
  const ca = canonicalThickness(a)
  const cb = canonicalThickness(b)
  if (!ca || !cb) return false
  const norm = (s) => s.toLowerCase().replace(/\s+/g, ' ')
  return norm(ca) === norm(cb) || ca.replace(/\s/g, '') === cb.replace(/\s/g, '')
}

function parseThicknessPoint(text) {
  const raw = String(text ?? '')
    .trim()
    .replace(/mm/gi, '')
    .trim()
  if (!raw || raw === '-' || raw === '—' || raw === '–' || THICKNESS_RANGE_RE.test(raw)) return null
  const n = Number.parseFloat(raw)
  return Number.isFinite(n) ? n : null
}

/** Titik (1.2) atau rentang identik vs spek rencana (1.2 - 1.4). */
export function thicknessPointInRange(point, spec) {
  if (thicknessMatches(point, spec)) return true
  const val = parseThicknessPoint(point)
  const rawSpec = String(spec ?? '')
    .trim()
    .replace(/mm/gi, '')
    .trim()
  const match = THICKNESS_RANGE_RE.exec(rawSpec)
  if (val == null || !match) return false
  let lo = Number.parseFloat(match[1])
  let hi = Number.parseFloat(match[2])
  if (!Number.isFinite(lo) || !Number.isFinite(hi)) return false
  if (lo > hi) [lo, hi] = [hi, lo]
  return lo - 1e-9 <= val && val <= hi + 1e-9
}

export function ylThicknessMatchesAnySpec(ylThickness, specs) {
  const list = (specs || []).map((s) => String(s || '').trim()).filter(Boolean)
  if (!list.length) return true
  const tebal = String(ylThickness ?? '').trim()
  if (!tebal) return false
  return list.some((spec) => thicknessPointInRange(tebal, spec))
}
