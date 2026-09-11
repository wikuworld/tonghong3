/** Helpers nomor lot draft (prefix+factory+YYMMDD+seq 3 digit). */

const LOT_SEQ_RE = /^(.*?)(\d{3})$/

export function parseLotNumber(lot) {
  const raw = String(lot || '').trim()
  if (!raw) return null
  const m = raw.match(LOT_SEQ_RE)
  if (!m) return null
  return { stem: m[1], seq: Number(m[2]), raw }
}

/**
 * Naikkan seq lot preview agar tidak bentrok dengan lot yang sudah di-reserve di draft.
 * `baseLot` biasanya hasil peek DB (next sequence tanpa commit).
 */
export function nextLotAfterReserved(baseLot, reservedLots = []) {
  const base = parseLotNumber(baseLot)
  if (!base) return String(baseLot || '').trim()

  let maxSeq = base.seq - 1
  for (const item of reservedLots || []) {
    const parsed = parseLotNumber(item)
    if (!parsed || parsed.stem !== base.stem) continue
    if (parsed.seq > maxSeq) maxSeq = parsed.seq
  }
  const next = Math.max(base.seq, maxSeq + 1)
  return `${base.stem}${String(next).padStart(3, '0')}`
}

export function collectReservedLots(lines, { excludeIndex = -1 } = {}) {
  const out = []
  ;(lines || []).forEach((line, idx) => {
    if (excludeIndex >= 0 && idx === excludeIndex) return
    const lot = String(line?.thi_line_ref || '').trim()
    if (lot) out.push(lot)
  })
  return out
}
