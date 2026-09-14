<template>
  <AdminSection :title="t('pages.mrpProses.title')" :subtitle="t('pages.mrpProses.subtitle')">
    <template #actions>
      <el-button :icon="Refresh" :loading="loading" @click="reload">{{ t('common.refresh') }}</el-button>
      <el-button v-if="canCreate" type="primary" :icon="Plus" @click="openCreate">{{ t('common.create') }}</el-button>
    </template>

    <div class="admin-inner-card">
      <el-table
        :data="rows"
        v-loading="loading"
        border
        stripe
        size="small"
        class="admin-table"
        empty-text="—"
      >
        <el-table-column type="index" width="56" :label="t('common.noLabel')" align="center" />
        <el-table-column prop="kode_proses" :label="t('pages.mrpProses.kodeProses')" min-width="130" show-overflow-tooltip />
        <el-table-column prop="kode_rencana" :label="t('pages.mrpProses.kodeRpi')" min-width="120" show-overflow-tooltip />
        <el-table-column prop="kode_wip" label="WIP" min-width="120" show-overflow-tooltip />
        <el-table-column prop="no_po" :label="t('pages.mrpRencana.poCustomerRef')" width="110" show-overflow-tooltip />
        <el-table-column prop="no_so" :label="t('pages.mrpRencana.soRef')" min-width="120" show-overflow-tooltip />
        <el-table-column :label="t('common.color')" width="110" show-overflow-tooltip>
          <template #default="{ row }">{{ dash(row.warna) }}</template>
        </el-table-column>
        <el-table-column :label="t('pages.mrpProses.thickness')" width="90">
          <template #default="{ row }">{{ dash(row.tebal) }}</template>
        </el-table-column>
        <el-table-column :label="t('pages.mrpProses.treatmentJenis')" width="90">
          <template #default="{ row }">{{ dash(row.treatment_jenis) }}</template>
        </el-table-column>
        <el-table-column :label="t('common.status')" width="110" align="center">
          <template #default="{ row }">
            <el-tag :type="statusType(row.status)" size="small" effect="plain">
              {{ statusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column :label="t('pages.mrpProses.checkpointStatus')" min-width="150" show-overflow-tooltip>
          <template #default="{ row }">
            <el-tag v-if="row.checkpoint_status" size="small" effect="plain">
              {{ row.checkpoint_status }}
            </el-tag>
            <span v-else class="text-gray-400">—</span>
          </template>
        </el-table-column>
        <el-table-column :label="t('pages.mrpProses.totalSize')" width="100" align="right">
          <template #default="{ row }">{{ formatQty(row.total_size) }}</template>
        </el-table-column>
        <el-table-column :label="t('common.actions')" width="100" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="goDetail(row.id)">{{ t('common.detail') }}</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <el-dialog
      v-model="createOpen"
      :title="t('pages.mrpProses.createTitle')"
      width="1280px"
      destroy-on-close
      append-to-body
      class="mrp-proses-create-dialog"
    >
      <div class="mrp-proses-create-layout">
        <div class="mrp-proses-create-layout__main">
          <p class="text-sm text-slate-500 mb-3">{{ t('pages.mrpProses.createHint') }}</p>
          <el-form label-position="top">
        <el-form-item :label="t('pages.mrpProses.treatmentJenis')" required>
          <el-radio-group v-model="form.treatment_jenis" @change="onTreatmentJenisChange">
            <el-radio-button value="PU">PU</el-radio-button>
            <el-radio-button value="Suede">SUEDE</el-radio-button>
          </el-radio-group>
        </el-form-item>
        <el-form-item :label="t('pages.mrpProses.treatmentList')" required>
          <div class="mrp-proses-treatment-box">
            <template v-if="treatmentsFiltered.length">
              <el-checkbox-group v-model="form.treatment_list">
                <div
                  v-for="tr in treatmentsFiltered"
                  :key="tr.nama_treatment"
                  class="mrp-proses-treatment-item"
                >
                  <el-checkbox :label="tr.nama_treatment">{{ tr.nama_treatment }}</el-checkbox>
                </div>
              </el-checkbox-group>
            </template>
            <p v-else class="text-sm text-slate-400 mb-0">{{ t('pages.mrpProses.treatmentEmpty') }}</p>
          </div>
        </el-form-item>
          <div class="mrp-proses-wip-card mb-3">
            <span class="mrp-proses-wip-card__label">{{ t('pages.mrpProses.kodeWip') }}</span>
            <span class="mrp-proses-wip-card__value">{{ previewKodeWip || '—' }}</span>
            <span class="mrp-proses-wip-card__hint">{{ t('pages.mrpProses.kodeWipHint') }}</span>
          </div>
        <el-form-item :label="t('pages.mrpProses.scanRpi')">
          <div class="flex gap-2 w-full">
            <el-input
              v-model="form.kode_scan"
              :placeholder="t('pages.mrpProses.scanPlaceholder')"
              class="flex-1"
              @keyup.enter="doScan"
            />
            <el-button @click="doScan">{{ t('pages.mrpProses.scan') }}</el-button>
          </div>
        </el-form-item>
        <el-form-item :label="t('pages.mrpProses.pilihItem')">
          <el-select
            v-model="form.rencana_item_id"
            filterable
            clearable
            class="w-full"
            @change="onItemSelect"
          >
            <el-option
              v-for="it in rencanaItems"
              :key="it.id"
              :label="rencanaItemLabel(it)"
              :value="it.id"
            />
          </el-select>
        </el-form-item>
        <div v-if="scanned" class="mrp-proses-scan-card mb-3">
          <span class="mrp-proses-scan-card__label">{{ t('common.detail') }}</span>
          <span class="mrp-proses-scan-card__value">
            {{ scanned.kode_rencana }} · {{ dash(scanned.nama_rencana) }} ·
            {{ scanned.kode_rencana_item }}
          </span>
        </div>

        <template v-if="candidateRows.length">
          <div class="mrp-proses-section-title">{{ t('pages.mrpProses.candidateList') }}</div>
          <el-table
            :data="candidateRows"
            border
            stripe
            size="small"
            class="admin-table mb-3"
            empty-text="—"
          >
            <el-table-column width="48" align="center">
              <template #default="{ row }">
                <el-checkbox
                  :model-value="isRowChecked(row)"
                  @change="(val) => toggleRow(row, val)"
                />
              </template>
            </el-table-column>
            <el-table-column :label="t('common.material')" min-width="120" show-overflow-tooltip>
              <template #default="{ row }">{{ dash(row.material_name) }}</template>
            </el-table-column>
            <el-table-column :label="t('pages.mrpProses.thickness')" width="90">
              <template #default="{ row }">{{ dash(row.thickness) }}</template>
            </el-table-column>
            <el-table-column :label="t('common.color')" width="100" show-overflow-tooltip>
              <template #default="{ row }">{{ dash(row.color) }}</template>
            </el-table-column>
            <el-table-column label="Emboss" width="90" show-overflow-tooltip>
              <template #default="{ row }">{{ dash(row.emboss) }}</template>
            </el-table-column>
            <el-table-column :label="t('common.colorStandard')" min-width="110" show-overflow-tooltip>
              <template #default="{ row }">{{ dash(row.color_swatch) }}</template>
            </el-table-column>
            <el-table-column label="qty" width="80" align="right">
              <template #default="{ row }">{{ formatQty(row.qty) }}</template>
            </el-table-column>
            <el-table-column :label="t('pages.mrpProses.qtyProcess')" width="90" align="right">
              <template #default="{ row }">{{ formatQty(row.qty_proses) }}</template>
            </el-table-column>
            <el-table-column prop="no_po" :label="t('pages.mrpRencana.poCustomerRef')" width="110" show-overflow-tooltip />
          </el-table>
        </template>

        <template v-if="processRows.length">
          <div class="mrp-proses-section-title">{{ t('pages.mrpProses.processList') }}</div>
          <el-table
            :data="processRows"
            border
            stripe
            size="small"
            class="admin-table mb-3"
            empty-text="—"
          >
            <el-table-column :label="t('pages.mrpProses.kodeRpi')" min-width="130" show-overflow-tooltip>
              <template #default="{ row }">{{ dash(row.kode_rencana_item) }}</template>
            </el-table-column>
            <el-table-column :label="t('common.material')" min-width="120" show-overflow-tooltip>
              <template #default="{ row }">{{ dash(row.material_name) }}</template>
            </el-table-column>
            <el-table-column :label="t('pages.mrpProses.thickness')" width="90">
              <template #default="{ row }">{{ dash(row.thickness) }}</template>
            </el-table-column>
            <el-table-column :label="t('common.color')" width="100" show-overflow-tooltip>
              <template #default="{ row }">{{ dash(row.color) }}</template>
            </el-table-column>
            <el-table-column label="Emboss" width="90" show-overflow-tooltip>
              <template #default="{ row }">{{ dash(row.emboss) }}</template>
            </el-table-column>
            <el-table-column :label="t('common.colorStandard')" min-width="110" show-overflow-tooltip>
              <template #default="{ row }">{{ dash(row.color_swatch) }}</template>
            </el-table-column>
            <el-table-column label="qty" width="80" align="right">
              <template #default="{ row }">{{ formatQty(row.qty) }}</template>
            </el-table-column>
            <el-table-column :label="t('pages.mrpProses.qtyProcess')" width="90" align="right">
              <template #default="{ row }">{{ formatQty(row.qty_proses) }}</template>
            </el-table-column>
            <el-table-column prop="no_po" :label="t('pages.mrpRencana.poCustomerRef')" width="110" show-overflow-tooltip />
            <el-table-column :label="t('common.actions')" width="72" align="center" fixed="right">
              <template #default="{ row }">
                <el-button link type="danger" :title="t('common.delete')" @click="removeProcessRow(row)">
                  <el-icon><Delete /></el-icon>
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </template>

        <el-divider />

        <el-form-item :label="t('pages.mrpProses.pilihKy')">
          <el-select
            v-model="selectedKy"
            filterable
            clearable
            class="w-full"
            :placeholder="t('pages.mrpProses.pilihKyPlaceholder')"
            @change="onKySelect"
          >
            <el-option v-for="k in paletOptions" :key="k" :label="k" :value="k" />
          </el-select>
        </el-form-item>

        <template v-if="kyCandidateRows.length">
          <div class="mrp-proses-section-title">{{ t('pages.mrpProses.kyCandidateList') }}</div>
          <el-table
            :data="kyCandidateRows"
            border
            stripe
            size="small"
            class="admin-table mb-3"
            empty-text="—"
          >
            <el-table-column width="48" align="center">
              <template #default="{ row }">
                <el-checkbox
                  :model-value="isKyRowChecked(row)"
                  @change="(val) => toggleKyRow(row, val)"
                />
              </template>
            </el-table-column>
            <el-table-column prop="kode_yl" :label="t('pages.mrpProses.ylCode')" min-width="110" show-overflow-tooltip />
            <el-table-column :label="t('pages.mrpProses.thickness')" width="90">
              <template #default="{ row }">{{ dash(row.thickness) }}</template>
            </el-table-column>
            <el-table-column :label="t('common.color')" width="100" show-overflow-tooltip>
              <template #default="{ row }">{{ dash(row.warna || row.color) }}</template>
            </el-table-column>
            <el-table-column label="qty" width="90" align="right">
              <template #default="{ row }">{{ formatQty(row.stok_qty) }}</template>
            </el-table-column>
          </el-table>
        </template>

        <template v-if="processKyRows.length">
          <div class="mrp-proses-section-title">{{ t('pages.mrpProses.processKyList') }}</div>
          <el-table
            :data="processKyRows"
            border
            stripe
            size="small"
            class="admin-table mb-3"
            empty-text="—"
            :row-class-name="kyRowClassName"
          >
            <el-table-column prop="kode_palet" :label="t('pages.mrpPalet.kodePalet')" min-width="110" show-overflow-tooltip />
            <el-table-column prop="kode_yl" :label="t('pages.mrpProses.ylCode')" min-width="110" show-overflow-tooltip />
            <el-table-column :label="t('pages.mrpProses.thickness')" width="90">
              <template #default="{ row }">{{ dash(row.thickness) }}</template>
            </el-table-column>
            <el-table-column :label="t('common.color')" width="100" show-overflow-tooltip>
              <template #default="{ row }">{{ dash(row.warna || row.color) }}</template>
            </el-table-column>
            <el-table-column label="qty" width="90" align="right">
              <template #default="{ row }">{{ formatQty(row.qty) }}</template>
            </el-table-column>
            <el-table-column :label="t('pages.mrpProses.tidakAdaSisa')" width="110" align="center">
              <template #default="{ row }">
                <el-checkbox v-model="row.tidak_ada_sisa" />
              </template>
            </el-table-column>
            <el-table-column :label="t('pages.mrpProses.hasilPengukuran')" min-width="120" show-overflow-tooltip>
              <template #default="{ row }">{{ dash(row.hasil_ukur) }}</template>
            </el-table-column>
            <el-table-column :label="t('common.actions')" width="120" align="center" fixed="right">
              <template #default="{ row }">
                <el-button link type="primary" :title="t('pages.mrpProses.prosesUkur')" @click="startProsesUkur(row)">
                  <el-icon><VideoPlay /></el-icon>
                </el-button>
                <el-button
                  link
                  type="info"
                  :title="t('pages.mrpProses.ukurDetailTitle')"
                  :disabled="!row.ukur_rows?.length"
                  @click="openKyUkurDetail(row)"
                >
                  <el-icon><View /></el-icon>
                </el-button>
                <el-button link type="danger" :title="t('common.delete')" @click="removeProcessKyRow(row)">
                  <el-icon><Delete /></el-icon>
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </template>
          </el-form>
        </div>

        <MrpProsesUkurPanel
          :rows="activeUkurRows"
          :total-size="activeUkurTotalSize"
          :total-qty="activeUkurRows.length"
          :online="scaleOnline"
          :active="!!activeKyKey"
          :can-start="!!activeKyKey"
          :can-stop="scaleOnline && !!activeKyKey"
          :can-add="scaleOnline && !!activeKyKey"
          :can-print="false"
          :can-save="!!activeKyKey && activeUkurRows.length > 0"
          :can-delete="!!activeKyKey"
          :hint="activeKyKey ? '' : t('pages.mrpProses.ukurPickKyHint')"
          @start="panelStart"
          @stop="panelStop"
          @add="panelAddUkur"
          @save="saveKyUkur"
          @delete="panelDeleteUkur"
        />
      </div>

      <el-dialog
        v-model="kyUkurDetailOpen"
        :title="t('pages.mrpProses.ukurDetailTitle')"
        width="480px"
        destroy-on-close
        append-to-body
      >
        <p v-if="kyUkurDetailRow" class="text-sm text-slate-500 mb-3">
          {{ kyUkurDetailRow.kode_palet }} · {{ kyUkurDetailRow.kode_yl }}
        </p>
        <el-table :data="kyUkurDetailRow?.ukur_rows || []" border size="small" empty-text="—">
          <el-table-column type="index" width="56" :label="t('common.noLabel')" align="center" />
          <el-table-column :label="t('pages.mrpProses.sizeUkur')" align="right">
            <template #default="{ row }">{{ formatQty(row.size_val) }}</template>
          </el-table-column>
          <el-table-column :label="t('common.actions')" width="90" align="center">
            <template #default="{ row }">
              <el-button link type="danger" :title="t('common.delete')" @click="deleteKyUkurDetailRow(row)">
                <el-icon><Delete /></el-icon>
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-dialog>
      <template #footer>
        <el-button @click="createOpen = false">{{ t('common.cancel') }}</el-button>
        <el-button type="primary" :loading="saving" @click="submit">{{ t('common.save') }}</el-button>
      </template>
    </el-dialog>
  </AdminSection>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Delete, Plus, Refresh, VideoPlay, View } from '@element-plus/icons-vue'
import AdminSection from '../../../components/AdminSection.vue'
import MrpProsesUkurPanel from './MrpProsesUkurPanel.vue'
import { can } from '../../../security/permissions'
import {
  mrpCreateProses,
  mrpGetProses,
  mrpListProses,
  mrpListYl,
  mrpProsesAction,
  mrpProsesNextWip,
  mrpProsesScanRencana,
} from '../../../api/client'

const { t } = useI18n()
const router = useRouter()
const loading = ref(false)
const saving = ref(false)
const createOpen = ref(false)
const rows = ref([])
const rencanaItems = ref([])
const treatments = ref([])
const scanned = ref(null)
const candidateRows = ref([])
const processRows = ref([])
const ylStock = ref([])
const paletOptions = ref([])
const selectedKy = ref('')
const kyCandidateRows = ref([])
const processKyRows = ref([])
const activeKyKey = ref('')
const scaleOnline = ref(false)
const kyUkurDetailOpen = ref(false)
const kyUkurDetailRow = ref(null)
const previewKodeWip = ref('')
const canCreate = computed(() => can('mrpShopfloor', 'create'))

const activeKyRow = computed(() =>
  processKyRows.value.find((row) => kyRowKey(row) === activeKyKey.value) || null,
)
const activeUkurRows = computed(() => activeKyRow.value?.ukur_rows || [])
const activeUkurTotalSize = computed(() =>
  activeUkurRows.value.reduce((sum, row) => sum + (Number(row.size_val) || 0), 0),
)
const form = reactive({
  kode_scan: '',
  rencana_item_id: null,
  treatment_jenis: 'PU',
  treatment_list: [],
})

const treatmentsFiltered = computed(() =>
  treatments.value.filter((tr) => tr.jenis === form.treatment_jenis),
)

function rowKey(row) {
  const itemId = row.rencana_item_id ?? 'item'
  const poKey = row.po_link_id ?? row.po_id ?? row.no_po ?? 'item'
  return `${itemId}:${poKey}`
}

function isRowChecked(row) {
  return processRows.value.some((r) => rowKey(r) === rowKey(row))
}

function toggleRow(row, checked) {
  const key = rowKey(row)
  if (checked) {
    if (!processRows.value.some((r) => rowKey(r) === key)) {
      processRows.value.push({ ...row })
    }
  } else {
    removeProcessRowByKey(key)
  }
}

function removeProcessRow(row) {
  removeProcessRowByKey(rowKey(row))
}

function removeProcessRowByKey(key) {
  processRows.value = processRows.value.filter((r) => rowKey(r) !== key)
}

function kyRowKey(row) {
  return `${row.kode_palet}:${row.kode_yl}`
}

function isKyRowChecked(row) {
  return processKyRows.value.some((r) => kyRowKey(r) === kyRowKey(row))
}

function toggleKyRow(row, checked) {
  const key = kyRowKey(row)
  if (checked) {
    if (!processKyRows.value.some((r) => kyRowKey(r) === key)) {
      processKyRows.value.push({
        ...row,
        qty: Number(row.stok_qty) || Number(row.qty) || 0,
        tidak_ada_sisa: false,
        ukur_rows: [],
        hasil_ukur: '',
      })
    }
  } else {
    removeProcessKyRowByKey(key)
  }
}

function removeProcessKyRow(row) {
  removeProcessKyRowByKey(kyRowKey(row))
}

function removeProcessKyRowByKey(key) {
  processKyRows.value = processKyRows.value.filter((r) => kyRowKey(r) !== key)
  if (activeKyKey.value === key) {
    activeKyKey.value = ''
    scaleOnline.value = false
  }
}

function kyRowClassName({ row }) {
  return kyRowKey(row) === activeKyKey.value ? 'mrp-proses-ky-row--active' : ''
}

function startProsesUkur(row) {
  activeKyKey.value = kyRowKey(row)
  scaleOnline.value = false
  if (!row.ukur_rows) row.ukur_rows = []
}

function openKyUkurDetail(row) {
  kyUkurDetailRow.value = row
  kyUkurDetailOpen.value = true
}

function deleteKyUkurDetailRow(ukurRow) {
  if (!kyUkurDetailRow.value?.ukur_rows) return
  const key = ukurRow.key ?? ukurRow.id
  kyUkurDetailRow.value.ukur_rows = kyUkurDetailRow.value.ukur_rows.filter(
    (r) => (r.key ?? r.id) !== key,
  )
  refreshKyHasilUkur(kyUkurDetailRow.value)
  if (activeKyKey.value === kyRowKey(kyUkurDetailRow.value) && !kyUkurDetailRow.value.ukur_rows.length) {
    kyUkurDetailRow.value.hasil_ukur = ''
  }
}

function refreshKyHasilUkur(kyRow) {
  const rows = kyRow?.ukur_rows || []
  if (!rows.length) {
    kyRow.hasil_ukur = ''
    return
  }
  const total = rows.reduce((sum, r) => sum + (Number(r.size_val) || 0), 0)
  kyRow.hasil_ukur = `${formatQty(total)} (${rows.length})`
}

function buildKyCandidateRows(kodePalet) {
  return ylStock.value
    .filter((y) => y.kode_palet === kodePalet && Number(y.qty) > 0)
    .map((y) => ({
      kode_palet: y.kode_palet,
      kode_yl: y.kode_yl,
      thickness: y.thickness,
      warna: y.warna,
      color: y.warna,
      stok_qty: Number(y.qty) || 0,
      qty: Number(y.qty) || 0,
    }))
}

function onKySelect(kodePalet) {
  selectedKy.value = kodePalet || ''
  kyCandidateRows.value = kodePalet ? buildKyCandidateRows(kodePalet) : []
}

function rencanaItemLabel(it) {
  const rp = (it.kode_rencana || '').trim()
  const nama = (it.nama_rencana || '').trim()
  const rpi = (it.kode_rencana_item || '').trim()
  return [rp, nama, rpi].filter(Boolean).join(' · ')
}

function resolveMaterialName(item, po = null) {
  const fromItem = (item?.material_name || '').trim()
  const fromPo = po
    ? (po.material_name || po.item_name || '').trim()
    : ''
  return fromItem || fromPo || (item?.kode_kulit || '').trim()
}

function buildCandidateRows(item, poList = []) {
  const meta = {
    rencana_item_id: item.id,
    kode_rencana_item: item.kode_rencana_item,
    kode_rencana: item.kode_rencana,
    nama_rencana: item.nama_rencana,
    thickness: item.thickness,
    color: item.color,
    emboss: item.emboss,
    color_swatch: item.color_swatch,
  }
  if (poList.length) {
    return poList.map((po) => ({
      ...meta,
      material_name: resolveMaterialName(item, po),
      po_link_id: po.po_link_id,
      po_id: po.po_id,
      no_po: po.no_po,
      item_name: po.item_name,
      qty: po.qty ?? po.qty_outstanding,
      qty_outstanding: po.qty_outstanding,
      qty_proses: po.qty_proses,
    }))
  }
  return [
    {
      ...meta,
      material_name: resolveMaterialName(item),
      po_link_id: null,
      po_id: null,
      no_po: '',
      qty: null,
      qty_proses: null,
    },
  ]
}

function applyScanResult(data) {
  scanned.value = data
  candidateRows.value = buildCandidateRows(data, data.po_list || [])
}

function dash(v) {
  const s = (v == null ? '' : String(v)).trim()
  return s || '—'
}

function formatQty(v) {
  const n = Number(v)
  if (!Number.isFinite(n)) return '—'
  return Number.isInteger(n) ? String(n) : n.toLocaleString(undefined, { maximumFractionDigits: 2 })
}

function statusType(status) {
  const s = String(status || '')
  if (s === 'completed' || s === 'saved') return 'success'
  if (s === 'started') return 'warning'
  if (s === 'draft') return 'info'
  return ''
}

function statusLabel(status) {
  const s = String(status || '')
  const map = {
    draft: t('pages.mrpProses.statusDraft'),
    started: t('pages.mrpProses.statusStarted'),
    saved: t('pages.mrpProses.statusSaved'),
    completed: t('pages.mrpProses.statusCompleted'),
  }
  return map[s] || s || '—'
}

function onTreatmentJenisChange() {
  const allowed = new Set(treatmentsFiltered.value.map((tr) => tr.nama_treatment))
  form.treatment_list = form.treatment_list.filter((name) => allowed.has(name))
}

async function reload() {
  loading.value = true
  try {
    const data = await mrpListProses()
    rows.value = data.persiapan_list || []
    rencanaItems.value = data.rencana_items || []
    treatments.value = data.treatments || []
    paletOptions.value = data.palet_options || []
    try {
      ylStock.value = await mrpListYl()
      if (!paletOptions.value.length) {
        paletOptions.value = [...new Set(ylStock.value.map((y) => y.kode_palet).filter(Boolean))]
      }
    } catch {
      ylStock.value = []
    }
  } catch (e) {
    ElMessage.error(e.message || String(e))
  } finally {
    loading.value = false
  }
}

function resetCreateForm() {
  form.kode_scan = ''
  form.rencana_item_id = null
  form.treatment_jenis = 'PU'
  form.treatment_list = []
  scanned.value = null
  candidateRows.value = []
  processRows.value = []
  selectedKy.value = ''
  kyCandidateRows.value = []
  processKyRows.value = []
  activeKyKey.value = ''
  scaleOnline.value = false
  kyUkurDetailOpen.value = false
  kyUkurDetailRow.value = null
  previewKodeWip.value = ''
}

async function loadNextWipPreview() {
  try {
    const data = await mrpProsesNextWip()
    previewKodeWip.value = data.kode_wip || ''
  } catch {
    previewKodeWip.value = ''
  }
}

function openCreate() {
  resetCreateForm()
  createOpen.value = true
  loadNextWipPreview()
}

async function loadItemDetail(kode) {
  if (!kode) {
    scanned.value = null
    candidateRows.value = []
    return
  }
  try {
    const data = await mrpProsesScanRencana(kode)
    applyScanResult(data)
  } catch (e) {
    scanned.value = null
    candidateRows.value = []
    ElMessage.error(e.message || String(e))
  }
}

async function doScan() {
  if (!form.kode_scan.trim()) return
  const kode = form.kode_scan.trim()
  await loadItemDetail(kode)
  if (scanned.value?.id) form.rencana_item_id = scanned.value.id
}

async function onItemSelect(itemId) {
  if (!itemId) {
    scanned.value = null
    candidateRows.value = []
    return
  }
  const it = rencanaItems.value.find((row) => row.id === itemId)
  if (!it?.kode_rencana_item) return
  form.kode_scan = it.kode_rencana_item
  await loadItemDetail(it.kode_rencana_item)
}

function groupProcessRowsByItem(rows) {
  const groups = new Map()
  for (const row of rows) {
    const itemId = row.rencana_item_id
    if (!itemId) continue
    if (!groups.has(itemId)) groups.set(itemId, [])
    groups.get(itemId).push(row)
  }
  return groups
}

function panelStart() {
  if (!activeKyKey.value) {
    ElMessage.warning(t('pages.mrpProses.ukurPickKyHint'))
    return
  }
  scaleOnline.value = true
}

function panelStop() {
  scaleOnline.value = false
}

function panelAddUkur(size) {
  if (!activeKyRow.value) return
  if (!scaleOnline.value) {
    ElMessage.warning(t('pages.mrpProses.panelStartFirst'))
    return
  }
  const val = Number(size)
  if (!(val > 0)) {
    ElMessage.warning(t('pages.mrpProses.sizeUkur'))
    return
  }
  if (!activeKyRow.value.ukur_rows) activeKyRow.value.ukur_rows = []
  activeKyRow.value.ukur_rows.push({ key: `${Date.now()}-${val}`, size_val: val })
}

function panelDeleteUkur(row) {
  if (!activeKyRow.value?.ukur_rows) return
  const key = row.key ?? row.id
  activeKyRow.value.ukur_rows = activeKyRow.value.ukur_rows.filter((r) => (r.key ?? r.id) !== key)
}

function saveKyUkur() {
  if (!activeKyRow.value) return
  if (!activeKyRow.value.ukur_rows?.length) {
    ElMessage.warning(t('pages.mrpProses.sizeUkur'))
    return
  }
  refreshKyHasilUkur(activeKyRow.value)
  scaleOnline.value = false
  ElMessage.success(t('common.saved'))
}

async function applyKyUkursToProses(persiapanId) {
  const rowsToProcess = processKyRows.value.filter(
    (r) => r.ukur_rows?.length || r.tidak_ada_sisa,
  )
  if (!rowsToProcess.length) return
  await mrpProsesAction(persiapanId, { action: 'start' })
  let detail = await mrpGetProses(persiapanId)
  for (const kyRow of rowsToProcess) {
    let session = detail.ky_sessions?.find(
      (s) => s.kode_palet === kyRow.kode_palet && s.kode_yl === kyRow.kode_yl,
    )
    if (!session?.id) continue
    if (session.status !== 'active') {
      await mrpProsesAction(persiapanId, { action: 'activate_ky', ky_id: session.id })
      detail = await mrpGetProses(persiapanId)
      session =
        detail.ky_sessions?.find((s) => s.id === session.id) ||
        detail.ky_sessions?.find(
          (s) => s.kode_palet === kyRow.kode_palet && s.kode_yl === kyRow.kode_yl,
        )
      if (!session?.id) continue
    }
    for (const u of kyRow.ukur_rows || []) {
      await mrpProsesAction(persiapanId, {
        action: 'add_ukur',
        ky_id: session.id,
        size_val: Number(u.size_val),
      })
    }
    if (kyRow.tidak_ada_sisa) {
      await mrpProsesAction(persiapanId, { action: 'selesai_ky', ky_id: session.id })
      detail = await mrpGetProses(persiapanId)
    }
  }
}

async function submit() {
  if (!processRows.value.length && !processKyRows.value.length) {
    ElMessage.warning(t('pages.mrpProses.processRequired'))
    return
  }
  if (!form.treatment_list?.length) {
    ElMessage.warning(t('pages.mrpProses.treatmentRequired'))
    return
  }
  for (const row of processKyRows.value) {
    const qty = Number(row.qty)
    if (!Number.isFinite(qty) || qty <= 0) {
      ElMessage.warning(t('pages.mrpProses.kyQtyInvalid'))
      return
    }
    if (row.stok_qty != null && qty > Number(row.stok_qty)) {
      ElMessage.warning(t('pages.mrpProses.kyQtyExceed', { stok: formatQty(row.stok_qty) }))
      return
    }
    if (row.tidak_ada_sisa && !row.ukur_rows?.length) {
      ElMessage.warning(t('pages.mrpProses.tidakAdaSisaNeedUkur'))
      return
    }
  }
  saving.value = true
  try {
    const kyLines = processKyRows.value.map((row) => ({
      kode_palet: row.kode_palet,
      kode_yl: row.kode_yl,
      target_qty: Number(row.qty),
      tidak_ada_sisa: !!row.tidak_ada_sisa,
    }))
    const groups = groupProcessRowsByItem(processRows.value)
    const created = []
    let attachKy = true
    if (groups.size) {
      for (const [itemId, itemRows] of groups) {
        const poIds = itemRows.map((row) => row.po_id).filter(Boolean)
        const first = itemRows[0]
        const res = await mrpCreateProses({
          rencana_item_id: itemId,
          kode_scan: first.kode_rencana_item || form.kode_scan,
          treatment_jenis: form.treatment_jenis,
          treatment_list: form.treatment_list,
          po_ids: poIds,
          ky_lines: attachKy ? kyLines : [],
        })
        created.push(res)
        attachKy = false
      }
    } else {
      const itemId = form.rencana_item_id || scanned.value?.id
      if (!itemId) {
        ElMessage.warning(t('pages.mrpProses.scanRpi'))
        saving.value = false
        return
      }
      const res = await mrpCreateProses({
        rencana_item_id: itemId,
        kode_scan: form.kode_scan,
        treatment_jenis: form.treatment_jenis,
        treatment_list: form.treatment_list,
        po_ids: [],
        ky_lines: kyLines,
      })
      created.push(res)
    }
    const primaryId = created[0]?.id
    if (primaryId) {
      await applyKyUkursToProses(primaryId)
    }
    ElMessage.success(t('common.saved'))
    createOpen.value = false
    await reload()
    if (created.length === 1) {
      router.push(`/admin/mrp/proses/${created[0].id}`)
    }
  } catch (e) {
    ElMessage.error(e.message || String(e))
  } finally {
    saving.value = false
  }
}

function goDetail(id) {
  router.push(`/admin/mrp/proses/${id}`)
}

onMounted(reload)
</script>

<style scoped>
.mrp-proses-wip-card {
  border: 1px solid var(--el-color-primary-light-7);
  border-radius: 8px;
  padding: 0.75rem 0.85rem;
  background: var(--el-color-primary-light-9);
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}
.mrp-proses-wip-card__label {
  font-size: 0.7rem;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: var(--el-text-color-secondary);
}
.mrp-proses-wip-card__value {
  font-size: 1.05rem;
  font-weight: 700;
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
  color: var(--el-color-primary);
}
.mrp-proses-wip-card__hint {
  font-size: 0.72rem;
  color: var(--el-text-color-secondary);
}
.mrp-proses-scan-card {
  border: 1px solid var(--el-border-color-lighter);
  border-radius: 8px;
  padding: 0.65rem 0.85rem;
  background: var(--el-fill-color-blank);
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
}
.mrp-proses-scan-card__label {
  font-size: 0.7rem;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: var(--el-text-color-secondary);
}
.mrp-proses-scan-card__value {
  font-size: 0.875rem;
  color: var(--el-text-color-primary);
}
.mrp-proses-section-title {
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--el-text-color-primary);
  margin-bottom: 0.5rem;
}
.mrp-proses-treatment-box {
  border: 1px solid var(--el-border-color-lighter);
  border-radius: 8px;
  padding: 0.65rem 0.85rem;
  max-height: 180px;
  overflow-y: auto;
  width: 100%;
}
.mrp-proses-treatment-item {
  margin-bottom: 0.35rem;
}
.mrp-proses-treatment-item:last-child {
  margin-bottom: 0;
}
.mrp-proses-create-layout {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 360px;
  gap: 1rem;
  align-items: start;
}
.mrp-proses-create-layout__main {
  min-width: 0;
  max-height: 72vh;
  overflow: auto;
  padding-right: 0.25rem;
}
@media (max-width: 1100px) {
  .mrp-proses-create-layout {
    grid-template-columns: 1fr;
  }
}
:deep(.mrp-proses-ky-row--active) {
  --el-table-tr-bg-color: var(--el-color-primary-light-9);
}
</style>
