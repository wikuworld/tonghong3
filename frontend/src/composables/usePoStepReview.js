import { computed, ref, watch } from 'vue'

import {
  emptyEtdScheduleRows,
  etdScheduleRowsToPayload,
  lineHasScheduleMismatch,
  syncSingleEtdScheduleQty,
} from '../utils/poEtdSchedule.js'

/** Step 2: jadwal kirim ETD tunggal per baris (tanpa gelombang). */
export function usePoStepReview({ formModel }) {
  const etdScheduleOpen = ref(['schedule'])
  const etdScheduleRows = ref(emptyEtdScheduleRows())

  function clearEtdScheduleRows() {
    etdScheduleRows.value = emptyEtdScheduleRows()
  }

  function syncEtdQtyFromOrder() {
    syncSingleEtdScheduleQty(etdScheduleRows.value, formModel.quantity_order)
  }

  watch(
    () => formModel.quantity_order,
    () => syncEtdQtyFromOrder(),
    { immediate: true },
  )

  function copyEtdDateFromHeader() {
    const header = formModel.etd ? String(formModel.etd).slice(0, 10) : ''
    if (!header) return
    etdScheduleRows.value[0].date = header
    syncEtdQtyFromOrder()
  }

  const etdScheduleMismatch = computed(() =>
    lineHasScheduleMismatch(
      {
        quantity_order: formModel.quantity_order,
        delivery_schedules: etdScheduleRowsToPayload(
          etdScheduleRows.value,
          formModel.quantity_order,
        ),
      },
      etdScheduleRows.value,
    ),
  )

  return {
    etdScheduleOpen,
    etdScheduleRows,
    clearEtdScheduleRows,
    copyEtdDateFromHeader,
    syncEtdQtyFromOrder,
    etdScheduleMismatch,
  }
}
