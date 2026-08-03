/** Jadwal kirim (ETD) per baris PO — UI wizard: 1 jadwal per baris; backend/outstanding tetap mendukung hingga 21 slot. */

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

export function normalizeSchedulesFromApi(rows) {
  return (rows || []).map((s) => ({
    sequence_no: Number(s.sequence_no),
    qty: s.qty != null ? Number(s.qty) : null,
    delivery_date: s.delivery_date ? String(s.delivery_date).slice(0, 10) : null,
  }))
}

export function syncSingleEtdScheduleQty(rows, orderQtyRaw) {
  const row = (rows || [])[0]
  if (!row) return
  const orderQty = Number(orderQtyRaw)
  row.qty = orderQty > 0 ? orderQty : null
}

export function etdScheduleRowsToPayload(rows, orderQtyRaw = null) {
  const row = (rows || [])[0]
  if (!row) return []
  const hasDate = Boolean(row.date)
  const hasQty = row.qty != null && row.qty !== ''
  const orderQty = Number(orderQtyRaw)
  if (!hasDate && !hasQty) return []

  let qty = hasQty ? Number(row.qty) : null
  if ((qty == null || Number.isNaN(qty)) && orderQty > 0) {
    qty = orderQty
  }

  return [
    {
      sequence_no: 1,
      qty: qty != null && !Number.isNaN(qty) ? qty : null,
      delivery_date: row.date || null,
    },
  ]
}

export function loadEtdScheduleRowsFromApi(schedules) {
  const filled = (schedules || [])
    .filter((s) => (s.qty != null && s.qty !== '') || s.delivery_date)
    .sort((a, b) => Number(a.sequence_no) - Number(b.sequence_no))
  if (!filled.length) return emptyEtdScheduleRows()

  const totalQty = filled.reduce((sum, s) => sum + (Number(s.qty) || 0), 0)
  const firstDate = filled.find((s) => s.delivery_date)?.delivery_date

  return [
    {
      sequence_no: 1,
      qty: totalQty > 0 ? totalQty : null,
      date: firstDate ? String(firstDate).slice(0, 10) : '',
    },
  ]
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

  if (!dates.length) return empty

  const first = dates[0]
  const uniqueDates = [...new Set(dates)]
  if (uniqueDates.length === 1) return first
  return `${first} +${uniqueDates.length - 1}`
}
