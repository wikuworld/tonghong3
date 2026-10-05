import { computed, ref } from 'vue'

import { emptyEtdScheduleRows } from '../utils/poEtdSchedule.js'

/** Step 2: Reply ETD baris (bukan slot rencana kirim Outstanding). */
export function usePoStepReview({ formModel }) {
  const etdScheduleOpen = ref(['schedule'])
  const etdScheduleRows = ref(emptyEtdScheduleRows())

  function clearEtdScheduleRows() {
    etdScheduleRows.value = emptyEtdScheduleRows()
  }

  /** No-op: qty rencana kirim tidak lagi diisi dari wizard SO. */
  function syncEtdQtyFromOrder() {}

  function copyEtdDateFromHeader() {
    const header = formModel.etd ? String(formModel.etd).slice(0, 10) : ''
    if (!header) return
    etdScheduleRows.value[0].date = header
  }

  const etdScheduleMismatch = computed(() => false)

  return {
    etdScheduleOpen,
    etdScheduleRows,
    clearEtdScheduleRows,
    copyEtdDateFromHeader,
    syncEtdQtyFromOrder,
    etdScheduleMismatch,
  }
}
