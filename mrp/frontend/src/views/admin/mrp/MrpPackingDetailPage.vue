<template>
  <AdminSection :title="title" :subtitle="t('pages.mrpPacking.detailSubtitle')">
    <template #actions>
      <el-button @click="$router.push('/admin/mrp/packing')">{{ t('common.close') }}</el-button>
      <el-button :icon="Refresh" :loading="loading" @click="reload">{{ t('common.refresh') }}</el-button>
      <el-button v-if="packing" @click="printLabel">{{ t('pages.mrpPacking.printList') }}</el-button>
      <el-button
        v-if="canUpdate && packing?.status === 'in_progress'"
        type="success"
        :loading="acting"
        @click="finish"
      >
        {{ t('pages.mrpPacking.finish') }}
      </el-button>
    </template>

    <div v-loading="loading">
      <div v-if="packing" class="admin-inner-card mb-4">
        <div class="admin-inner-card__body">
        <div class="mrp-pack-flow mb-3">
          <span
            class="mrp-pack-flow__step"
            :class="{ 'is-current': packing.status === 'in_progress', 'is-done': packing.status === 'finished' }"
          >
            {{ t('pages.mrpPacking.statusInProgress') }}
          </span>
          <span
            class="mrp-pack-flow__step"
            :class="{ 'is-current': packing.status === 'finished', 'is-done': packing.status === 'finished' }"
          >
            {{ t('pages.mrpPacking.statusFinished') }}
          </span>
        </div>

        <div class="mrp-pack-stats">
          <div class="mrp-pack-stat">
            <span class="mrp-pack-stat__label">{{ t('pages.mrpPacking.kodePacking') }}</span>
            <span class="mrp-pack-stat__value mrp-pack-stat__value--text">{{ dash(packing.kode_packing) }}</span>
          </div>
          <div class="mrp-pack-stat">
            <span class="mrp-pack-stat__label">WIP / WO</span>
            <span class="mrp-pack-stat__value mrp-pack-stat__value--text">
              {{ dash(packing.work_order || packing.kode_wip) }}
            </span>
          </div>
          <div class="mrp-pack-stat">
            <span class="mrp-pack-stat__label">{{ t('pages.mrpRencana.poCustomerRef') }}</span>
            <span class="mrp-pack-stat__value mrp-pack-stat__value--text">{{ dash(packing.no_po) }}</span>
          </div>
          <div class="mrp-pack-stat">
            <span class="mrp-pack-stat__label">{{ t('common.status') }}</span>
            <span class="mrp-pack-stat__value">
              <el-tag :type="packing.status === 'finished' ? 'success' : 'warning'" size="small" effect="plain">
                {{ packing.status === 'finished' ? t('pages.mrpPacking.statusFinished') : t('pages.mrpPacking.statusInProgress') }}
              </el-tag>
            </span>
          </div>
          <div class="mrp-pack-stat">
            <span class="mrp-pack-stat__label">{{ t('common.customer') }}</span>
            <span class="mrp-pack-stat__value mrp-pack-stat__value--text">{{ dash(packing.customer) }}</span>
          </div>
          <div class="mrp-pack-stat mrp-pack-stat--wide">
            <span class="mrp-pack-stat__label">{{ t('pages.mrpPacking.description') }}</span>
            <span class="mrp-pack-stat__value mrp-pack-stat__value--text">{{ dash(packing.description) }}</span>
          </div>
          <div class="mrp-pack-stat">
            <span class="mrp-pack-stat__label">{{ t('pages.mrpPacking.thickness') }}</span>
            <span class="mrp-pack-stat__value mrp-pack-stat__value--text">{{ dash(packing.thickness) }}</span>
          </div>
          <div class="mrp-pack-stat">
            <span class="mrp-pack-stat__label">{{ t('common.color') }}</span>
            <span class="mrp-pack-stat__value mrp-pack-stat__value--text">{{ dash(packing.color) }}</span>
          </div>
          <div class="mrp-pack-stat">
            <span class="mrp-pack-stat__label">{{ t('pages.mrpPacking.colorSwatch') }}</span>
            <span class="mrp-pack-stat__value mrp-pack-stat__value--text">{{ dash(packing.color_swatch) }}</span>
          </div>
          <div class="mrp-pack-stat">
            <span class="mrp-pack-stat__label">{{ t('pages.mrpPacking.totalRolls') }}</span>
            <span class="mrp-pack-stat__value">{{ packing.total_rolls ?? rolls.length }}</span>
          </div>
          <div class="mrp-pack-stat">
            <span class="mrp-pack-stat__label">{{ t('pages.mrpPacking.totalPieces') }}</span>
            <span class="mrp-pack-stat__value">{{ formatQty(packing.total_pieces ?? packing.total_lembar) }}</span>
          </div>
          <div class="mrp-pack-stat">
            <span class="mrp-pack-stat__label">{{ t('pages.mrpPacking.totalQty') }}</span>
            <span class="mrp-pack-stat__value">
              {{ formatQty(packing.total_quantity ?? packing.total_ukuran) }}
              {{ packing.qty_unit || 'SF' }}
            </span>
          </div>
        </div>

        <el-alert
          v-if="packing.status === 'in_progress' && !rolls.length"
          class="mt-3"
          type="warning"
          :closable="false"
          show-icon
          :title="t('pages.mrpPacking.needRollHint')"
        />
        <el-alert
          v-else-if="packing.status === 'finished'"
          class="mt-3"
          type="success"
          :closable="false"
          show-icon
          :title="t('pages.mrpPacking.finishedHint')"
        />
        </div>
      </div>

      <div v-if="canUpdate && packing?.status === 'in_progress'" class="admin-inner-card mb-4">
        <div class="admin-inner-card__body">
        <h3 class="admin-inner-card__title mb-2">{{ t('pages.mrpPacking.editHeader') }}</h3>
        <div class="mrp-pack-form-row">
          <el-form-item :label="t('pages.mrpPacking.softness')" class="mb-0">
            <el-input v-model="headerForm.softness" class="w-36" placeholder="SOFT" />
          </el-form-item>
          <el-form-item :label="t('pages.mrpPacking.grossWeight')" class="mb-0">
            <el-input v-model="headerForm.gross_weight" type="number" class="w-32" />
          </el-form-item>
          <el-form-item :label="t('pages.mrpPacking.netWeight')" class="mb-0">
            <el-input v-model="headerForm.net_weight" type="number" class="w-32" />
          </el-form-item>
          <el-button type="primary" :loading="acting" @click="saveHeader">{{ t('common.save') }}</el-button>
        </div>
        </div>
      </div>

      <div v-if="canUpdate && packing?.status === 'in_progress'" class="admin-inner-card mb-4">
        <div class="admin-inner-card__body">
        <h3 class="admin-inner-card__title mb-2">{{ t('pages.mrpPacking.addRoll') }}</h3>
        <div class="mrp-pack-form-row">
          <el-form-item :label="t('pages.mrpPacking.pieces')" class="mb-0">
            <el-input v-model="rollForm.lembar" type="number" class="w-28" />
          </el-form-item>
          <el-form-item :label="t('pages.mrpPacking.quantity')" class="mb-0">
            <el-input v-model="rollForm.ukuran" type="number" class="w-28" @keyup.enter="addRoll" />
          </el-form-item>
          <el-form-item :label="t('pages.mrpPacking.remark')" class="mb-0">
            <el-input v-model="rollForm.remark" class="w-48" />
          </el-form-item>
          <el-button type="primary" :loading="acting" @click="addRoll">{{ t('common.add') }}</el-button>
        </div>
        </div>
      </div>

      <div class="admin-inner-card mb-4">
        <div class="admin-inner-card__head">
          <h3 class="admin-inner-card__title">{{ t('pages.mrpPacking.rolls') }}</h3>
        </div>
        <el-table :data="rolls" border stripe size="small" class="admin-table" :empty-text="t('common.tableEmpty')">
          <el-table-column prop="roll_no" :label="t('pages.mrpPacking.artNo')" width="80" align="center" />
          <el-table-column prop="kode_packing" :label="t('pages.mrpPacking.kodePacking')" min-width="130" show-overflow-tooltip>
            <template #default="{ row }">{{ dash(row.kode_packing) }}</template>
          </el-table-column>
          <el-table-column :label="t('pages.mrpPacking.pieces')" width="100" align="right">
            <template #default="{ row }">{{ formatQty(row.lembar) }}</template>
          </el-table-column>
          <el-table-column :label="t('pages.mrpPacking.quantity')" width="110" align="right">
            <template #default="{ row }">{{ formatQty(row.ukuran) }}</template>
          </el-table-column>
          <el-table-column :label="t('pages.mrpPacking.remark')" min-width="140" show-overflow-tooltip>
            <template #default="{ row }">{{ dash(row.remark) }}</template>
          </el-table-column>
          <el-table-column prop="created_at" :label="t('common.date')" min-width="140" />
          <el-table-column :label="t('common.actions')" width="148" align="center" fixed="right">
            <template #default="{ row }">
              <AdminTableActions
                :show-view="false"
                :show-delete="canUpdate && packing?.status === 'in_progress'"
                :more-items="
                  row.id
                    ? [{ command: 'print', label: t('pages.mrpPacking.reprintRollLabel'), icon: Printer }]
                    : []
                "
                @delete="deleteRoll(row.id)"
                @more="(cmd) => cmd === 'print' && printRollLabel(row)"
              />
            </template>
          </el-table-column>
        </el-table>
      </div>

      <div class="admin-inner-card mb-4">
        <div class="admin-inner-card__head">
          <h3 class="admin-inner-card__title">{{ t('pages.mrpPacking.poSection') }}</h3>
          <el-button
            v-if="canUpdate && packing?.status === 'in_progress' && availablePos.length"
            size="small"
            @click="showAddPo = !showAddPo"
          >
            {{ showAddPo ? t('common.close') : t('common.add') }}
          </el-button>
        </div>
        <div v-if="showAddPo" class="admin-inner-card__body" style="border-bottom: 1px solid #e2e8f0">
          <el-table :data="availablePos" border size="small" class="admin-table" :empty-text="t('common.tableEmpty')">
            <el-table-column prop="no_po" :label="t('pages.mrpRencana.poCustomerRef')" min-width="110" />
            <el-table-column prop="no_so" :label="t('pages.mrpRencana.soRef')" min-width="100" />
            <el-table-column prop="item_name" :label="t('pages.mrpPacking.poItem')" min-width="130" show-overflow-tooltip />
            <el-table-column :label="t('pages.mrpPacking.qtyPlan')" width="90" align="right">
              <template #default="{ row }">{{ formatQty(row.qty_sq) }}</template>
            </el-table-column>
            <el-table-column :label="t('common.actions')" width="88" align="center">
              <template #default="{ row }">
                <AdminTableActions
                  :more-items="[{ command: 'add', label: t('common.add'), icon: Plus }]"
                  @more="(cmd) => cmd === 'add' && addPo(row)"
                />
              </template>
            </el-table-column>
          </el-table>
        </div>
        <el-table :data="packingPos" border stripe size="small" class="admin-table" :empty-text="t('common.tableEmpty')">
          <el-table-column prop="no_po" :label="t('pages.mrpRencana.poCustomerRef')" min-width="110" />
          <el-table-column prop="no_so" :label="t('pages.mrpRencana.soRef')" min-width="100" />
          <el-table-column prop="item_name" :label="t('pages.mrpPacking.poItem')" min-width="130" show-overflow-tooltip />
          <el-table-column :label="t('pages.mrpPacking.qtyPlan')" width="90" align="right">
            <template #default="{ row }">{{ formatQty(row.qty_sq) }}</template>
          </el-table-column>
          <el-table-column
            v-if="canUpdate && packing?.status === 'in_progress'"
            :label="t('common.actions')"
            width="88"
            align="center"
            fixed="right"
          >
            <template #default="{ row }">
              <AdminTableActions :show-delete="true" @delete="deletePo(row.id)" />
            </template>
          </el-table-column>
        </el-table>
      </div>
    </div>
  </AdminSection>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Printer, Refresh } from '@element-plus/icons-vue'
import AdminSection from '../../../components/AdminSection.vue'
import AdminTableActions from '../../../components/admin/AdminTableActions.vue'
import { can } from '../../../security/permissions'
import { mrpGetPacking, mrpPackingAction, mrpPackingPrint, mrpPackingRollLabel } from '../../../api/client'
import { printPackingList } from '../../../utils/mrpPackingListPrint'
import { printMrpPackingRollLabel } from '../../../utils/mrpPackingRollLabelPrint'

const { t } = useI18n()
const route = useRoute()
const loading = ref(false)
const acting = ref(false)
const printingRollId = ref(null)
const showAddPo = ref(false)
const packing = ref(null)
const rolls = ref([])
const packingPos = ref([])
const availablePos = ref([])
const canUpdate = computed(() => can('mrpShopfloor', 'update'))
const title = computed(() => packing.value?.kode_packing || t('pages.mrpPacking.title'))
const rollForm = reactive({ lembar: 1, ukuran: '', remark: '' })
const headerForm = reactive({ softness: '', gross_weight: '', net_weight: '' })

function dash(v) {
  const s = (v == null ? '' : String(v)).trim()
  return s || '—'
}

function formatQty(v) {
  const n = Number(v)
  if (!Number.isFinite(n)) return '—'
  return Number.isInteger(n) ? String(n) : n.toLocaleString(undefined, { maximumFractionDigits: 2 })
}

async function reload() {
  loading.value = true
  try {
    const data = await mrpGetPacking(route.params.id)
    packing.value = data.packing
    rolls.value = data.rolls || []
    packingPos.value = data.packing_pos || []
    availablePos.value = data.available_pos || []
    headerForm.softness = data.packing?.softness || ''
    headerForm.gross_weight = data.packing?.gross_weight ?? ''
    headerForm.net_weight = data.packing?.net_weight ?? ''
  } catch (e) {
    ElMessage.error(e.message || String(e))
  } finally {
    loading.value = false
  }
}

async function act(body) {
  acting.value = true
  try {
    const res = await mrpPackingAction(route.params.id, body)
    ElMessage.success(res.message || t('common.saved'))
    await reload()
    return res
  } catch (e) {
    ElMessage.error(e.message || String(e))
    return null
  } finally {
    acting.value = false
  }
}

function saveHeader() {
  return act({
    action: 'update_header',
    softness: headerForm.softness,
    gross_weight: headerForm.gross_weight === '' ? null : Number(headerForm.gross_weight),
    net_weight: headerForm.net_weight === '' ? null : Number(headerForm.net_weight),
  })
}

async function addRoll() {
  const lembar = Number(rollForm.lembar)
  const ukuran = Number(rollForm.ukuran)
  if (!(lembar > 0)) {
    ElMessage.warning(t('pages.mrpPacking.piecesInvalid'))
    return
  }
  if (!(ukuran > 0)) {
    ElMessage.warning(t('pages.mrpPacking.qtyInvalid'))
    return
  }
  const res = await act({
    action: 'add_roll',
    lembar,
    ukuran,
    remark: rollForm.remark || '',
  })
  if (res) {
    rollForm.ukuran = ''
    rollForm.remark = ''
  }
}

function deleteRoll(rollId) {
  return act({ action: 'delete_roll', roll_id: rollId })
}

async function printRollLabel(row) {
  if (!row?.id) return
  printingRollId.value = row.id
  try {
    const res = await mrpPackingRollLabel(row.id)
    printMrpPackingRollLabel(res.label, t)
    ElMessage.success(t('pages.mrpPacking.reprintOk'))
  } catch (e) {
    ElMessage.error(e.message || String(e))
  } finally {
    printingRollId.value = null
  }
}

function addPo(row) {
  return act({
    action: 'add_po',
    no_po: row.no_po,
    no_so: row.no_so || '',
    qty_sq: row.qty_sq || 0,
    po_id: row.po_id || null,
  })
}

function deletePo(poRowId) {
  return act({ action: 'delete_po', po_row_id: poRowId })
}

async function finish() {
  if (!rolls.value.length) {
    ElMessage.warning(t('pages.mrpPacking.needRollHint'))
    return
  }
  const p = packing.value
  const wip = Number(p?.qty_wip ?? 0)
  const actual = Number(p?.qty_actual ?? p?.total_ukuran ?? 0)
  if (p && !p.stock_sisa_id && Number.isFinite(wip) && wip > 0 && actual > wip + 1e-9) {
    ElMessage.warning(
      t('pages.mrpPacking.finishActualExceedsWip', {
        actual: formatQty(actual),
        wip: formatQty(wip),
      }),
    )
    return
  }
  const shortfall = wip - actual
  try {
    if (p && !p.stock_sisa_id && Number.isFinite(wip) && wip > 0 && shortfall > 0.009) {
      await ElMessageBox.confirm(
        t('pages.mrpPacking.finishShortfallConfirm', {
          actual: formatQty(actual),
          wip: formatQty(wip),
          selisih: formatQty(shortfall),
        }),
        { type: 'warning', confirmButtonText: t('pages.mrpPacking.finish'), cancelButtonText: t('common.cancel') },
      )
    }
    await ElMessageBox.confirm(t('pages.mrpPacking.finishConfirm'), { type: 'warning' })
    await act({ action: 'finish' })
  } catch (e) {
    if (e !== 'cancel') ElMessage.error(e?.message || String(e))
  }
}

async function printLabel() {
  try {
    const data = await mrpPackingPrint(route.params.id)
    printPackingList(data, t)
  } catch (e) {
    ElMessage.error(e.message || String(e))
  }
}

onMounted(reload)
</script>

<style scoped>
.mrp-pack-flow {
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem;
}
.mrp-pack-flow__step {
  font-size: 0.75rem;
  padding: 0.25rem 0.65rem;
  border-radius: 999px;
  border: 1px solid var(--el-border-color);
  color: var(--el-text-color-secondary);
  background: var(--el-fill-color-blank);
}
.mrp-pack-flow__step.is-done {
  border-color: var(--el-color-success-light-5);
  color: var(--el-color-success);
  background: var(--el-color-success-light-9);
}
.mrp-pack-flow__step.is-current {
  border-color: var(--el-color-primary-light-5);
  color: var(--el-color-primary);
  background: var(--el-color-primary-light-9);
  font-weight: 600;
}
.mrp-pack-stats {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 0.6rem;
}
.mrp-pack-stat {
  border: 1px solid var(--el-border-color-lighter);
  border-radius: 8px;
  padding: 0.65rem 0.75rem;
  min-height: 3.4rem;
}
.mrp-pack-stat--wide {
  grid-column: span 2;
}
.mrp-pack-stat__label {
  display: block;
  font-size: 0.7rem;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: var(--el-text-color-secondary);
  margin-bottom: 0.2rem;
}
.mrp-pack-stat__value {
  font-size: 1rem;
  font-weight: 600;
}
.mrp-pack-stat__value--text {
  font-size: 0.875rem;
  font-weight: 500;
  word-break: break-word;
}
.mrp-pack-form-row {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  align-items: flex-end;
}
@media (max-width: 900px) {
  .mrp-pack-stats {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
  .mrp-pack-stat--wide {
    grid-column: span 2;
  }
}
</style>
