/** Toleransi ukur kecil otomatis: max(2 SF, 0.5% qty order). Harus selaras backend. */
export const OVERSHIP_ABS_SF = 2
export const OVERSHIP_PCT = 0.005

export function overshipAllowance(orderQty) {
  const order = Number(orderQty)
  if (!Number.isFinite(order) || order <= 0) return OVERSHIP_ABS_SF
  const pct = Math.round(order * OVERSHIP_PCT * 100) / 100
  return Math.max(OVERSHIP_ABS_SF, pct)
}

/** True jika qty <= remaining, atau overage masih dalam toleransi. */
export function withinOvershipTolerance(qty, remaining, orderQty = null) {
  const q = Number(qty)
  const rem = Number(remaining)
  if (!Number.isFinite(q) || !Number.isFinite(rem)) return false
  if (q <= rem + 1e-9) return true
  const overage = q - rem
  const base = orderQty != null && Number.isFinite(Number(orderQty)) ? Number(orderQty) : rem
  return overage <= overshipAllowance(base) + 1e-9
}
