/** Status kerja baris outstanding — sisa kirim vs jadwal slot. */

function num(v) {
  const n = Number(v)
  return Number.isFinite(n) ? n : 0
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
