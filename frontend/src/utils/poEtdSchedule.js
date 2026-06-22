/** Jadwal kirim (ETD) per baris PO — maks. 21 gelombang (PROD outstanding manual); UI mulai dari 1 baris. */

export const ETD_SCHEDULE_SLOTS = 21

export function createEtdScheduleRow(sequenceNo = 1) {
  return {
    sequence_no: sequenceNo,
    qty: null,
    date: '',
  }
}

export function emptyEtdScheduleRows() {
  return [createEtdScheduleRow(1)]
}

export function resequenceEtdScheduleRows(rows) {
  return (rows || []).map((r, i) => ({
    ...r,
    sequence_no: i + 1,
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
  const filled = (schedules || [])
    .filter((s) => (s.qty != null && s.qty !== '') || s.delivery_date)
    .sort((a, b) => Number(a.sequence_no) - Number(b.sequence_no))
    .map((s) => ({
      sequence_no: Number(s.sequence_no),
      qty: s.qty != null ? Number(s.qty) : null,
      date: s.delivery_date ? String(s.delivery_date).slice(0, 10) : '',
    }))
  if (!filled.length) return emptyEtdScheduleRows()
  return resequenceEtdScheduleRows(filled)
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

/** Ringkasan singkat jadwal ETD baris untuk tabel draft / review. */
export function formatLineEtdScheduleDisplay(schedules, empty = '—') {
  const rows = (schedules || []).filter(
    (s) => (s.qty != null && s.qty !== '') || s.delivery_date || s.date,
  )
  if (!rows.length) return empty

  const dates = rows
    .map((s) => {
      const raw = s.delivery_date || s.date
      return raw ? String(raw).slice(0, 10) : null
    })
    .filter(Boolean)
    .sort()

  if (!dates.length) {
    return rows.length > 1 ? `${rows.length} gelombang` : empty
  }

  const first = dates[0]
  const uniqueDates = [...new Set(dates)]
  if (uniqueDates.length === 1) {
    return rows.length > 1 ? `${first} (${rows.length}×)` : first
  }
  return `${first} +${uniqueDates.length - 1}`
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
