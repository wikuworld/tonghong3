/** Jadwal kirim (ETD) per baris PO — 8 gelombang. */

export const ETD_SCHEDULE_SLOTS = 8

export function emptyEtdScheduleRows() {
  return Array.from({ length: ETD_SCHEDULE_SLOTS }, (_, i) => ({
    sequence_no: i + 1,
    qty: null,
    date: '',
  }))
}

export function normalizeSchedulesFromApi(rows) {
  return (rows || []).map((s) => ({
    sequence_no: Number(s.sequence_no),
    qty: s.qty != null ? Number(s.qty) : null,
    delivery_date: s.delivery_date ? String(s.delivery_date).slice(0, 10) : null,
  }))
}

export function etdScheduleRowsToPayload(rows) {
  return (rows || [])
    .filter((r) => (r.qty != null && r.qty !== '') || r.date)
    .map((r, i) => ({
      sequence_no: r.sequence_no ?? i + 1,
      qty: r.qty != null && r.qty !== '' ? Number(r.qty) : null,
      delivery_date: r.date || null,
    }))
}

export function loadEtdScheduleRowsFromApi(schedules) {
  const rows = emptyEtdScheduleRows()
  for (const s of schedules || []) {
    const idx = Number(s.sequence_no) - 1
    if (idx >= 0 && idx < rows.length) {
      rows[idx].qty = s.qty != null ? Number(s.qty) : null
      rows[idx].date = s.delivery_date ? String(s.delivery_date).slice(0, 10) : ''
    }
  }
  return rows
}

export function schedulePayloadTotal(schedules) {
  return (schedules || []).reduce((sum, s) => sum + (Number(s.qty) || 0), 0)
}

export function lineHasScheduleMismatch(line, fallbackRows = null) {
  const orderQty = Number(line?.quantity_order)
  if (!orderQty) return false
  const schedules = line.delivery_schedules?.length
    ? line.delivery_schedules
    : etdScheduleRowsToPayload(fallbackRows || [])
  if (!schedules.length) return false
  const total = schedulePayloadTotal(schedules)
  if (!total) return false
  return Math.abs(total - orderQty) > 0.001
}

export function buildEvenEtdScheduleRows(qty, startDateRaw) {
  const base = Math.floor(qty / ETD_SCHEDULE_SLOTS)
  const rem = qty % ETD_SCHEDULE_SLOTS
  const startRaw = startDateRaw ? String(startDateRaw).slice(0, 10) : ''
  return Array.from({ length: ETD_SCHEDULE_SLOTS }, (_, i) => {
    let date = ''
    if (startRaw) {
      const d = new Date(startRaw)
      d.setDate(d.getDate() + i * 7)
      date = d.toISOString().slice(0, 10)
    }
    return {
      sequence_no: i + 1,
      qty: base + (i < rem ? 1 : 0),
      date,
    }
  })
}
