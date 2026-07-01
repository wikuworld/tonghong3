import { computed, ref } from 'vue'
import { ElMessage } from 'element-plus'

import {
  createEtdScheduleRow,
  emptyEtdScheduleRows,
  ETD_SCHEDULE_SLOTS,
  etdScheduleRowsToPayload,
  buildEvenEtdScheduleRows,
  resequenceEtdScheduleRows,
  lineHasScheduleMismatch,
} from '../utils/poEtdSchedule.js'

/** Step 3: jadwal kirim ETD & ringkasan baris. */
export function usePoStepReview({ t, formModel }) {
  const etdScheduleOpen = ref(['schedule'])
  const etdScheduleRows = ref(emptyEtdScheduleRows())

  function clearEtdScheduleRows() {
    etdScheduleRows.value = emptyEtdScheduleRows()
  }

  const etdScheduleCanAdd = computed(
    () => etdScheduleRows.value.length < ETD_SCHEDULE_SLOTS,
  )

  function addEtdScheduleRow() {
    if (!etdScheduleCanAdd.value) {
      ElMessage.warning(t('pages.po.scheduleMaxWaves', { max: ETD_SCHEDULE_SLOTS }))
      return
    }
    etdScheduleRows.value = resequenceEtdScheduleRows([
      ...etdScheduleRows.value,
      createEtdScheduleRow(etdScheduleRows.value.length + 1),
    ])
  }

  function removeEtdScheduleRow(index) {
    if (etdScheduleRows.value.length <= 1) return
    const next = [...etdScheduleRows.value]
    next.splice(index, 1)
    etdScheduleRows.value = resequenceEtdScheduleRows(next)
  }

  const etdScheduleTotal = computed(() =>
    etdScheduleRows.value.reduce((sum, r) => sum + (Number(r.qty) || 0), 0),
  )

  const etdScheduleTotalDisplay = computed(() => {
    const total = etdScheduleTotal.value
    return total ? String(total) : '0'
  })

  const etdScheduleMismatch = computed(() =>
    lineHasScheduleMismatch(
      {
        quantity_order: formModel.quantity_order,
        delivery_schedules: etdScheduleRowsToPayload(etdScheduleRows.value),
      },
      etdScheduleRows.value,
    ),
  )

  function autoFillEtdScheduleWave1() {
    const qty = Number(formModel.quantity_order)
    if (!qty) {
      ElMessage.warning(t('pages.po.scheduleNeedQty'))
      return
    }
    clearEtdScheduleRows()
    etdScheduleRows.value[0].qty = qty
    etdScheduleRows.value[0].date = formModel.etd ? String(formModel.etd).slice(0, 10) : ''
  }

  function autoFillEtdScheduleEvenly() {
    const qty = Number(formModel.quantity_order)
    if (!qty) {
      ElMessage.warning(t('pages.po.scheduleNeedQty'))
      return
    }
    etdScheduleRows.value = buildEvenEtdScheduleRows(qty, formModel.etd)
  }

  return {
    etdScheduleOpen,
    etdScheduleRows,
    clearEtdScheduleRows,
    etdScheduleCanAdd,
    addEtdScheduleRow,
    removeEtdScheduleRow,
    etdScheduleTotal,
    etdScheduleTotalDisplay,
    etdScheduleMismatch,
    autoFillEtdScheduleWave1,
    autoFillEtdScheduleEvenly,
  }
}
