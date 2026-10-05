/** Status kerja baris outstanding — sisa kirim vs jadwal slot. */

function num(v) {
  const n = Number(v)
  return Number.isFinite(n) ? n : 0
}

function isoDateOrNull(v) {
  if (v == null || v === '') return null
  const s = String(v).trim().slice(0, 10)
  return /^\d{4}-\d{2}-\d{2}$/.test(s) ? s : null
}

/** Tanggal rencana slot pertama (plan_slots saja — bukan Reply ETD). */
export function firstPlannedDeliveryDate(row = {}) {
  const planSlots = Array.isArray(row.plan_slots) ? row.plan_slots : []
  for (const slot of planSlots) {
    const d = isoDateOrNull(slot?.delivery_date)
    if (d) return d
  }
  return null
}

/** Slot rencana murni dari row outstanding (hanya plan_slots; default 1 slot). */
export function extractPlanSlots(row = {}, { maxSlots = 1 } = {}) {
  if (Array.isArray(row.plan_slots) && row.plan_slots.length) {
    return row.plan_slots
      .map((s, idx) => ({
        sequence_no: Number(s.sequence_no) || idx + 1,
        qty: s.qty != null && s.qty !== '' ? String(s.qty) : '',
        delivery_date: isoDateOrNull(s.delivery_date) || '',
      }))
      .filter((s) => s.delivery_date || s.qty)
      .slice(0, maxSlots)
  }
  return []
}

/** Tanggal default batch: yang paling sering muncul di rencana, atau null. */
export function mostCommonPlannedDeliveryDate(rows = []) {
  const counts = new Map()
  for (const row of rows || []) {
    const d = firstPlannedDeliveryDate(row)
    if (!d) continue
    counts.set(d, (counts.get(d) || 0) + 1)
  }
  let best = null
  let bestN = 0
  for (const [d, n] of counts) {
    if (n > bestN) {
      best = d
      bestN = n
    }
  }
  return best
}

/**
 * @returns {'need_schedule'|'partial_schedule'|'scheduled'|'partial_ship'|'shipped'|'closed'}
 */
export function outstandingWorkStatus(row = {}) {
  const balance = num(row.balance_qty)
  const delivered = num(row.delivered_qty)
  const scheduled = num(row.schedule_qty_total)
  const unalloc = row.schedule_unallocated_qty === '' || row.schedule_unallocated_qty == null
    ? (scheduled > 0 ? 0 : balance)
    : num(row.schedule_unallocated_qty)

  if (balance <= 0 && delivered > 0) return 'shipped'
  if (balance <= 0) return 'closed'
  if (delivered > 0) return 'partial_ship'
  if (scheduled > 0 && unalloc <= 0) return 'scheduled'
  if (scheduled > 0) return 'partial_schedule'
  return 'need_schedule'
}

/** Aksi utama di outstanding: jadwal slot, buat delivery, atau selesai. */
export function outstandingNextAction(row = {}) {
  const st = outstandingWorkStatus(row)
  if (st === 'shipped' || st === 'closed') return 'done'
  if (st === 'need_schedule' || st === 'partial_schedule') return 'schedule'
  return 'ship'
}
