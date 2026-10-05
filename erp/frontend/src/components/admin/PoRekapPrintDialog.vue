<template>
  <el-dialog
    :model-value="modelValue"
    :title="dialogTitle"
    width="960px"
    top="4vh"
    destroy-on-close
    align-center
    class="po-rekap-dialog"
    @update:model-value="$emit('update:modelValue', $event)"
  >
    <div v-loading="loading" class="po-rekap-dialog__body">
      <p class="po-rekap-dialog__hint">
        {{
          poId
            ? t('pages.marketingFlow.rekapPrintHintPerSo')
            : t('pages.marketingFlow.rekapPrintHint')
        }}
      </p>

      <div v-if="payload" id="po-rekap-print-root" class="po-rekap-sheet">
        <header class="po-rekap-sheet__head">
          <h2>{{ payload.report_title }}</h2>
          <p>
            {{ t('pages.marketingFlow.rekapPrintDate') }}:
            <strong>{{ payload.report_date }}</strong>
            · {{ t('common.total') }} SO: <strong>{{ payload.order_count }}</strong>
            · {{ t('pages.marketingFlow.rekapPrintLines') }}: <strong>{{ payload.line_count }}</strong>
          </p>
          <p v-if="payload.pending_print_count > 0" class="po-rekap-sheet__pending">
            {{ t('pages.marketingFlow.rekapPrintPending', { n: payload.pending_print_count }) }}
          </p>
          <p v-else-if="payload.order_count > 0" class="po-rekap-sheet__done">
            {{ t('pages.marketingFlow.rekapPrintAlreadyDone') }}
          </p>
        </header>

        <section v-if="!(payload.orders || []).length" class="po-rekap-empty">
          {{ t('pages.marketingFlow.rekapPrintEmpty') }}
        </section>

        <template v-else>
          <h3 class="po-rekap-sheet__section">{{ t('pages.marketingFlow.rekapPrintOrders') }}</h3>
          <table class="po-rekap-table">
            <thead>
              <tr>
                <th>#</th>
                <th>{{ t('common.poNo') }}</th>
                <th>{{ t('common.customer') }}</th>
                <th>{{ t('common.buyer') }}</th>
                <th>{{ t('pages.marketingFlow.rekapColBrand') }}</th>
                <th>{{ t('common.orderDate') }}</th>
                <th>{{ t('common.etd') }}</th>
                <th>{{ t('common.status') }}</th>
                <th>{{ t('pages.marketingFlow.rekapPrintCol') }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(o, idx) in payload.orders" :key="o.po_id">
                <td>{{ idx + 1 }}</td>
                <td>{{ o.so_number }}</td>
                <td>{{ o.customer }}</td>
                <td>{{ o.buyer || '—' }}</td>
                <td>{{ o.brand || '—' }}</td>
                <td>{{ o.order_date || '—' }}</td>
                <td>{{ o.etd || '—' }}</td>
                <td>{{ o.status }}</td>
                <td>{{ o.rekap_printed_at ? t('common.yes') : t('common.no') }}</td>
              </tr>
            </tbody>
          </table>

          <h3 class="po-rekap-sheet__section">{{ t('pages.marketingFlow.rekapPrintLineDetails') }}</h3>
          <table class="po-rekap-table po-rekap-table--lines">
            <thead>
              <tr>
                <th>#</th>
                <th>{{ t('common.poNo') }}</th>
                <th>{{ t('common.customer') }}</th>
                <th>THI/Lot</th>
                <th>{{ t('common.material') }}</th>
                <th>{{ t('common.thickness') }}</th>
                <th>{{ t('common.color') }}</th>
                <th>{{ t('common.softness') }}</th>
                <th>{{ t('common.quantity') }}</th>
                <th>{{ t('common.etd') }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(ln, idx) in payload.lines" :key="`${ln.po_id}-${ln.detail_id || idx}`">
                <td>{{ idx + 1 }}</td>
                <td>{{ ln.poNo }}</td>
                <td>{{ ln.customer }}</td>
                <td>{{ ln.thi_line_ref || '—' }}</td>
                <td>{{ ln.material }}</td>
                <td>{{ ln.thickness }}</td>
                <td>{{ ln.color || '—' }}</td>
                <td>{{ ln.softness || '—' }}</td>
                <td>{{ formatQty(ln.qty) }}</td>
                <td>{{ ln.line_etd || '—' }}</td>
              </tr>
            </tbody>
          </table>
        </template>
      </div>
    </div>

    <template #footer>
      <div class="po-rekap-dialog__footer">
        <el-button :icon="Close" @click="$emit('update:modelValue', false)">{{ t('common.close') }}</el-button>
        <el-button
          :icon="Download"
          :disabled="!payload || !(payload.orders || []).length"
          @click="downloadCsv"
        >
          {{ t('pages.marketingFlow.rekapDownloadCsvOnly') }}
        </el-button>
        <el-button
          type="primary"
          :icon="Printer"
          :disabled="!payload || !(payload.orders || []).length"
          :loading="printing"
          @click="doPrint"
        >
          {{ t('common.print') }}
        </el-button>
        <el-button
          type="success"
          :disabled="!canConfirm"
          :loading="confirming"
          @click="confirmPrinted"
        >
          {{ t('pages.marketingFlow.rekapConfirmPrinted') }}
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { Close, Download, Printer } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useI18n } from 'vue-i18n'

import {
  confirmPoDailyRecapPrint,
  fetchAuthenticatedDocument,
  getPoDailyRecap,
  reportPoDailyRecapUrl,
} from '../../api/client'

const props = defineProps({
  modelValue: { type: Boolean, default: false },
  reportDate: { type: String, default: '' },
  /** Bila diisi: rekap satu SO (dari kolom Aksi). */
  poId: { type: [Number, String], default: null },
  poNumber: { type: String, default: '' },
})

const emit = defineEmits(['update:modelValue', 'confirmed'])

const { t } = useI18n()
const loading = ref(false)
const printing = ref(false)
const confirming = ref(false)
const printedAttempted = ref(false)
const payload = ref(null)

const dialogTitle = computed(() => {
  if (props.poNumber) {
    return `${t('pages.marketingFlow.rekapPrintDialogTitle')} — ${props.poNumber}`
  }
  return t('pages.marketingFlow.rekapPrintDialogTitle')
})

const canConfirm = computed(() => {
  const p = payload.value
  if (!p || !(p.orders || []).length) return false
  return (p.pending_print_count || 0) > 0 && printedAttempted.value
})

function formatQty(n) {
  if (n === null || n === undefined || n === '') return '—'
  return Number(n).toLocaleString()
}

async function load() {
  loading.value = true
  printedAttempted.value = false
  payload.value = null
  try {
    payload.value = await getPoDailyRecap({
      date: props.poId ? undefined : props.reportDate || undefined,
      poId: props.poId || undefined,
    })
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  } finally {
    loading.value = false
  }
}

watch(
  () => [props.modelValue, props.reportDate, props.poId],
  ([open]) => {
    if (open) load()
  },
)

function doPrint() {
  if (!payload.value) return
  printing.value = true
  const onAfter = () => {
    window.removeEventListener('afterprint', onAfter)
    printing.value = false
    printedAttempted.value = true
    if ((payload.value?.pending_print_count || 0) > 0) {
      ElMessage.info(t('pages.marketingFlow.rekapPrintAfterHint'))
    }
  }
  window.addEventListener('afterprint', onAfter)
  // Fallback bila afterprint tidak terpanggil (beberapa browser)
  window.setTimeout(() => {
    if (printing.value) {
      printing.value = false
      printedAttempted.value = true
    }
  }, 1500)
  window.print()
}

async function confirmPrinted() {
  if (!canConfirm.value) return
  try {
    await ElMessageBox.confirm(
      t('pages.marketingFlow.rekapConfirmPrintedAsk'),
      t('pages.marketingFlow.rekapConfirmPrinted'),
      { type: 'warning', confirmButtonText: t('common.yes'), cancelButtonText: t('common.cancel') },
    )
  } catch {
    return
  }
  confirming.value = true
  try {
    const pending = payload.value?.pending_po_ids?.length
      ? payload.value.pending_po_ids
      : props.poId
        ? [Number(props.poId)]
        : undefined
    const day = props.reportDate || payload.value?.report_date
    const res = await confirmPoDailyRecapPrint({
      report_date: day || undefined,
      po_ids: pending,
    })
    ElMessage.success(
      t('pages.marketingFlow.rekapConfirmPrintedDone', { n: res.stamped_count ?? 0 }),
    )
    emit('confirmed', res)
    await load()
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  } finally {
    confirming.value = false
  }
}

async function downloadCsv() {
  const day = props.reportDate || payload.value?.report_date || new Date().toISOString().slice(0, 10)
  const path = reportPoDailyRecapUrl(day, props.poId || undefined).replace(/^\/api\/v1/, '')
  const name = props.poNumber
    ? `rekap-${props.poNumber}.csv`
    : `po-daily-recap-${day}.csv`
  try {
    await fetchAuthenticatedDocument(path, {
      mode: 'download',
      downloadFallbackName: name,
    })
    ElMessage.success(t('pages.marketingFlow.rekapCsvOnlyDone'))
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  }
}
</script>

<style scoped>
.po-rekap-dialog__hint {
  margin: 0 0 12px;
  font-size: 13px;
  line-height: 1.45;
  color: #64748b;
}

.po-rekap-sheet {
  background: #fff;
  color: #0f172a;
}

.po-rekap-sheet__head h2 {
  margin: 0 0 6px;
  font-size: 1.25rem;
  font-weight: 700;
  letter-spacing: 0.02em;
}

.po-rekap-sheet__head p {
  margin: 0 0 4px;
  font-size: 13px;
  color: #334155;
}

.po-rekap-sheet__pending {
  color: #b45309 !important;
  font-weight: 600;
}

.po-rekap-sheet__done {
  color: #047857 !important;
  font-weight: 600;
}

.po-rekap-sheet__section {
  margin: 16px 0 8px;
  font-size: 0.95rem;
  font-weight: 650;
}

.po-rekap-empty {
  padding: 24px;
  text-align: center;
  color: #64748b;
  border: 1px dashed #cbd5e1;
  border-radius: 8px;
}

.po-rekap-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 12px;
}

.po-rekap-table th,
.po-rekap-table td {
  border: 1px solid #cbd5e1;
  padding: 5px 7px;
  text-align: left;
  vertical-align: top;
}

.po-rekap-table th {
  background: #f1f5f9;
  font-weight: 650;
}

.po-rekap-table--lines {
  font-size: 11px;
}

.po-rekap-dialog__footer {
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-end;
  gap: 8px;
}
</style>

<style>
@media print {
  body * {
    visibility: hidden !important;
  }
  #po-rekap-print-root,
  #po-rekap-print-root * {
    visibility: visible !important;
  }
  #po-rekap-print-root {
    position: absolute !important;
    left: 0 !important;
    top: 0 !important;
    width: 100% !important;
    padding: 8mm !important;
    background: #fff !important;
  }
  .el-overlay,
  .el-dialog__header,
  .el-dialog__footer,
  .po-rekap-dialog__hint {
    display: none !important;
  }
}
</style>
