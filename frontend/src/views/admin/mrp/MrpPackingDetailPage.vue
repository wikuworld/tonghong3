<template>
  <AdminSection :title="title" :subtitle="t('pages.mrpPacking.detailSubtitle')">
    <template #actions>
      <span v-if="loading" class="text-xs text-slate-500">{{ t('common.loadingData') }}</span>
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

    <div v-loading="loading" class="space-y-4">
      <div v-if="packing" class="admin-inner-card">
        <div class="admin-inner-card__head">
          <div>
            <h3 class="admin-inner-card__title">{{ t('pages.mrpPacking.overviewTitle') }}</h3>
            <p class="admin-inner-card__sub">{{ t('pages.mrpPacking.overviewSubtitle') }}</p>
          </div>
        </div>
        <div class="mkt-section-body">
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

        <div class="admin-stats-grid admin-stats-grid--4">
          <div class="admin-stat-card">
            <span class="admin-stat-card__label">{{ t('pages.mrpPacking.kodePacking') }}</span>
            <span class="admin-stat-card__value">{{ dash(packing.kode_packing) }}</span>
          </div>
          <div class="admin-stat-card">
            <span class="admin-stat-card__label">{{ t('pages.mrpPacking.wipWo') }}</span>
            <span class="admin-stat-card__value">
              {{ dash(packing.work_order || packing.kode_wip) }}
            </span>
          </div>
          <div class="admin-stat-card">
            <span class="admin-stat-card__label">{{ t('pages.mrpRencana.poCustomerRef') }}</span>
            <span class="admin-stat-card__value">{{ dash(packing.no_po) }}</span>
          </div>
          <div class="admin-stat-card">
            <span class="admin-stat-card__label">{{ t('common.status') }}</span>
            <span class="admin-stat-card__value">
              <el-tag :type="packing.status === 'finished' ? 'success' : 'warning'" size="small" effect="plain">
                {{ packing.status === 'finished' ? t('pages.mrpPacking.statusFinished') : t('pages.mrpPacking.statusInProgress') }}
              </el-tag>
            </span>
          </div>
          <div class="admin-stat-card">
            <span class="admin-stat-card__label">{{ t('common.customer') }}</span>
            <span class="admin-stat-card__value">{{ dash(packing.customer) }}</span>
          </div>
          <div class="admin-stat-card">
            <span class="admin-stat-card__label">{{ t('pages.mrpPacking.description') }}</span>
            <span class="admin-stat-card__value">{{ dash(packing.description) }}</span>
          </div>
          <div class="admin-stat-card">
            <span class="admin-stat-card__label">{{ t('pages.mrpPacking.thickness') }}</span>
            <span class="admin-stat-card__value">{{ dash(packing.thickness) }}</span>
          </div>
          <div class="admin-stat-card">
            <span class="admin-stat-card__label">{{ t('common.color') }}</span>
            <span class="admin-stat-card__value">{{ dash(packing.color) }}</span>
          </div>
          <div class="admin-stat-card">
            <span class="admin-stat-card__label">{{ t('pages.mrpPacking.colorSwatch') }}</span>
            <span class="admin-stat-card__value">{{ dash(packing.color_swatch) }}</span>
          </div>
          <div class="admin-stat-card">
            <span class="admin-stat-card__label">{{ t('pages.mrpPacking.totalRolls') }}</span>
            <span class="admin-stat-card__value">{{ packing.total_rolls ?? rolls.length }}</span>
          </div>
          <div class="admin-stat-card">
            <span class="admin-stat-card__label">{{ t('pages.mrpPacking.totalPieces') }}</span>
            <span class="admin-stat-card__value">{{ formatQty(packing.total_pieces ?? packing.total_lembar) }}</span>
          </div>
          <div class="admin-stat-card">
            <span class="admin-stat-card__label">{{ t('pages.mrpPacking.totalQty') }}</span>
            <span class="admin-stat-card__value">
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

      <div v-if="canUpdate && packing?.status === 'in_progress'" class="admin-inner-card">
        <div class="admin-inner-card__head">
          <div>
            <h3 class="admin-inner-card__title">{{ t('pages.mrpPacking.editHeader') }}</h3>
          </div>
        </div>
        <div class="mkt-section-body">
        <div class="mrp-pack-form-row">
          <el-form-item :label="t('pages.mrpPacking.softness')" class="mb-0">
            <el-input v-model="headerForm.softness" class="w-36" :placeholder="t('pages.mrpPacking.softPlaceholder')" />
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

      <div v-if="canUpdate && packing?.status === 'in_progress'" class="admin-inner-card">
        <div class="admin-inner-card__head">
          <div>
            <h3 class="admin-inner-card__title">{{ t('pages.mrpPacking.addRoll') }}</h3>
          </div>
        </div>
        <div class="mkt-section-body">
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

      <div class="admin-inner-card">
        <div class="admin-inner-card__head">
          <div>
            <h3 class="admin-inner-card__title">{{ t('pages.mrpPacking.rolls') }}</h3>
            <p class="admin-inner-card__sub">{{ t('pages.mrpPacking.rollsSubtitle') }}</p>
          </div>
        </div>
        <div class="mkt-section-body">
        <el-table :data="rolls" border stripe size="small" class="admin-table" :empty-text="t('pages.mrpPacking.tableEmpty')">
          <el-table-column prop="roll_no" :label="t('pages.mrpPacking.artNo')" width="80" align="center" />
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
          <el-table-column
            v-if="canUpdate && packing?.status === 'in_progress'"
            :label="t('common.actions')"
            width="90"
            fixed="right"
          >
            <template #default="{ row }">
              <el-button link type="danger" @click="deleteRoll(row.id)">{{ t('common.delete') }}</el-button>
            </template>
          </el-table-column>
        </el-table>
        </div>
      </div>

      <div class="admin-inner-card">
        <div class="admin-inner-card__head">
          <div>
            <h3 class="admin-inner-card__title">{{ t('pages.mrpPacking.poSection') }}</h3>
            <p class="admin-inner-card__sub">{{ t('pages.mrpPacking.poSectionSubtitle') }}</p>
          </div>
          <el-button
            v-if="canUpdate && packing?.status === 'in_progress' && availablePos.length"
            size="small"
            @click="showAddPo = !showAddPo"
          >
            {{ showAddPo ? t('common.close') : t('common.add') }}
          </el-button>
        </div>
        <div class="mkt-section-body">
        <div v-if="showAddPo" class="mb-3">
          <el-table :data="availablePos" border stripe size="small" class="admin-table" :empty-text="t('pages.mrpPacking.tableEmpty')">
            <el-table-column prop="no_po" :label="t('pages.mrpRencana.poCustomerRef')" min-width="110" />
            <el-table-column prop="no_so" :label="t('pages.mrpRencana.soRef')" min-width="100" />
            <el-table-column prop="item_name" :label="t('pages.mrpPacking.poItem')" min-width="130" show-overflow-tooltip />
            <el-table-column :label="t('pages.mrpPacking.qtyPlan')" width="90" align="right">
              <template #default="{ row }">{{ formatQty(row.qty_sq) }}</template>
            </el-table-column>
            <el-table-column width="90">
              <template #default="{ row }">
                <el-button link type="primary" @click="addPo(row)">{{ t('common.add') }}</el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
        <el-table :data="packingPos" border stripe size="small" class="admin-table" :empty-text="t('pages.mrpPacking.tableEmpty')">
          <el-table-column prop="no_po" :label="t('pages.mrpRencana.poCustomerRef')" min-width="110" />
          <el-table-column prop="no_so" :label="t('pages.mrpRencana.soRef')" min-width="100" />
          <el-table-column prop="item_name" :label="t('pages.mrpPacking.poItem')" min-width="130" show-overflow-tooltip />
          <el-table-column :label="t('pages.mrpPacking.qtyPlan')" width="90" align="right">
            <template #default="{ row }">{{ formatQty(row.qty_sq) }}</template>
          </el-table-column>
          <el-table-column v-if="canUpdate && packing?.status === 'in_progress'" width="90" fixed="right">
            <template #default="{ row }">
              <el-button link type="danger" @click="deletePo(row.id)">{{ t('common.delete') }}</el-button>
            </template>
          </el-table-column>
        </el-table>
        </div>
      </div>
    </div>
  </AdminSection>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Refresh } from '@element-plus/icons-vue'
import AdminSection from '../../../components/AdminSection.vue'
import { can } from '../../../security/permissions'
import { mrpGetPacking, mrpPackingAction, mrpPackingPrint } from '../../../api/client'

const { t } = useI18n()
const route = useRoute()
const loading = ref(false)
const acting = ref(false)
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

function esc(v) {
  return String(v ?? '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
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
  try {
    await ElMessageBox.confirm(t('pages.mrpPacking.finishConfirm'), { type: 'warning' })
    await act({ action: 'finish' })
  } catch (e) {
    if (e !== 'cancel') ElMessage.error(e?.message || String(e))
  }
}

async function printLabel() {
  try {
    const data = await mrpPackingPrint(route.params.id)
    const p = data.packing || {}
    const unit = p.qty_unit || 'SF'
    const rollsHtml = (data.rolls || [])
      .map(
        (r) =>
          `<tr><td class="num">${esc(r.roll_no)}</td><td class="num">${esc(r.lembar)}</td>` +
          `<td class="qty">${esc(r.ukuran)}</td><td>${esc(r.remark || '')}</td></tr>`,
      )
      .join('')
    const w = window.open('', '_blank')
    if (!w) throw new Error(t('pages.mrpPacking.popupBlocked'))
    w.document.write(`<!DOCTYPE html><html><head><meta charset="utf-8"><title>Packing List - ${esc(p.kode_packing)}</title>
<style>
@page{size:A4;margin:12mm}
body{font-family:Arial,Helvetica,sans-serif;font-size:12px;color:#111;margin:0;padding:16px}
.company{text-align:center;line-height:1.25;margin-bottom:6px}
.company .name{font-size:18px;font-weight:700}
.company .name-zh{font-size:14px;margin-top:2px}
.doc-title{text-align:center;font-size:20px;font-weight:700;margin:10px 0 4px}
.doc-title-zh{text-align:center;font-size:13px;margin-bottom:12px}
.meta{width:100%;border-collapse:collapse;margin-bottom:12px}
.meta td{padding:3px 6px;vertical-align:top}
.meta .lbl{width:18%;font-weight:700;white-space:nowrap}
.meta .val{width:32%;border-bottom:1px solid #bbb}
table.rolls{width:100%;border-collapse:collapse;margin-top:8px}
table.rolls th,table.rolls td{border:1px solid #333;padding:5px 6px}
table.rolls th{background:#f3f3f3;text-align:center}
table.rolls td.num{text-align:center}
table.rolls td.qty{text-align:right}
.totals{margin-top:14px;width:100%;border-collapse:collapse}
.totals td{padding:3px 6px}
.totals .lbl{font-weight:700;width:22%}
.totals .val{border-bottom:1px solid #bbb;width:28%}
.footer{margin-top:18px;font-size:11px;color:#444}
</style></head><body>
<div class="company">
  <div class="name">${esc(p.company_name || 'PT. TONG HONG TANNERY INDONESIA')}</div>
  <div class="name-zh">${esc(p.company_name_zh || '東崇皮革印尼有限公司')}</div>
</div>
<div class="doc-title">PACKING LIST</div>
<div class="doc-title-zh">裝貨單</div>
<table class="meta">
<tr><td class="lbl">Customer:</td><td class="val">${esc(p.customer)}</td>
<td class="lbl">Date:</td><td class="val">${esc(p.date_created)}</td></tr>
<tr><td class="lbl">Description:</td><td class="val" colspan="3">${esc(p.description)}</td></tr>
<tr><td class="lbl">${esc(t('pages.mrpRencana.poCustomerRef'))}:</td><td class="val">${esc(p.no_po)}</td>
<td class="lbl">Thickness:</td><td class="val">${esc(p.thickness)}</td></tr>
<tr><td class="lbl">Color:</td><td class="val">${esc(p.color)}</td>
<td class="lbl">Softness:</td><td class="val">${esc(p.softness || '-')}</td></tr>
<tr><td class="lbl">Color Swatch:</td><td class="val">${esc(p.color_swatch)}</td>
<td class="lbl">Work Order No:</td><td class="val">${esc(p.work_order || p.kode_wip)}</td></tr>
<tr><td class="lbl">Packing Code:</td><td class="val">${esc(p.kode_packing)}</td>
<td class="lbl">WIP:</td><td class="val">${esc(p.kode_wip)}</td></tr>
</table>
<table class="rolls">
<thead><tr><th>Art.no</th><th>Pieces</th><th>Quantity</th><th>Remark</th></tr></thead>
<tbody>${rollsHtml}</tbody>
</table>
<table class="totals">
<tr><td class="lbl">Total Rolls:</td><td class="val">${esc(p.total_rolls ?? (data.rolls || []).length)} ROLL</td>
<td class="lbl">Total Pieces:</td><td class="val">${esc(p.total_pieces ?? p.total_lembar ?? 0)} PIECES</td></tr>
<tr><td class="lbl">Total Quantity:</td><td class="val">${esc(p.total_quantity ?? p.total_ukuran ?? 0)} ${esc(unit)}</td>
<td class="lbl">Gross Weight:</td><td class="val">${esc(p.gross_weight ?? '')}</td></tr>
<tr><td class="lbl">Net Weight:</td><td class="val">${esc(p.net_weight ?? '')}</td><td></td><td></td></tr>
</table>
<div class="footer">${esc(p.form_code || 'QER-48-A/0')}</div>
<script>window.onload=function(){window.print()}<\/script>
</body></html>`)
    w.document.close()
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






.mrp-pack-form-row {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  align-items: flex-end;
}
@media (max-width: 900px) {
  
  
}
</style>
