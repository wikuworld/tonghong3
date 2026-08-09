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

    <div v-loading="loading" class="space-y-4">
      <div v-if="packing" class="admin-inner-card">
        <div class="grid grid-cols-2 md:grid-cols-4 gap-3 text-sm">
          <div><strong>{{ t('pages.mrpPacking.kodePacking') }}</strong><div>{{ packing.kode_packing }}</div></div>
          <div><strong>WIP / WO</strong><div>{{ packing.work_order || packing.kode_wip }}</div></div>
          <div><strong>PO</strong><div>{{ packing.no_po }}</div></div>
          <div><strong>{{ t('common.status') }}</strong><div>{{ packing.status }}</div></div>
          <div><strong>{{ t('common.customer') }}</strong><div>{{ packing.customer }}</div></div>
          <div><strong>{{ t('pages.mrpPacking.description') }}</strong><div>{{ packing.description || '-' }}</div></div>
          <div><strong>{{ t('pages.mrpPacking.thickness') }}</strong><div>{{ packing.thickness || '-' }}</div></div>
          <div><strong>{{ t('common.color') }}</strong><div>{{ packing.color || '-' }}</div></div>
          <div><strong>{{ t('pages.mrpPacking.colorSwatch') }}</strong><div>{{ packing.color_swatch || '-' }}</div></div>
          <div><strong>{{ t('pages.mrpPacking.softness') }}</strong><div>{{ packing.softness || '-' }}</div></div>
          <div><strong>{{ t('pages.mrpPacking.grossWeight') }}</strong><div>{{ packing.gross_weight ?? '-' }}</div></div>
          <div><strong>{{ t('pages.mrpPacking.netWeight') }}</strong><div>{{ packing.net_weight ?? '-' }}</div></div>
          <div><strong>{{ t('pages.mrpPacking.totalRolls') }}</strong><div>{{ packing.total_rolls ?? rolls.length }}</div></div>
          <div><strong>{{ t('pages.mrpPacking.totalPieces') }}</strong><div>{{ packing.total_pieces ?? packing.total_lembar }}</div></div>
          <div><strong>{{ t('pages.mrpPacking.totalQty') }}</strong><div>{{ packing.total_quantity ?? packing.total_ukuran }} {{ packing.qty_unit || 'SF' }}</div></div>
        </div>
      </div>

      <div v-if="canUpdate && packing?.status === 'in_progress'" class="admin-inner-card">
        <h3 class="admin-inner-card__title mb-2">{{ t('pages.mrpPacking.editHeader') }}</h3>
        <div class="flex gap-2 flex-wrap items-end">
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

      <div v-if="canUpdate && packing?.status === 'in_progress'" class="admin-inner-card">
        <h3 class="admin-inner-card__title mb-2">{{ t('pages.mrpPacking.addRoll') }}</h3>
        <div class="flex gap-2 flex-wrap">
          <el-input v-model="rollForm.lembar" type="number" :placeholder="t('pages.mrpPacking.pieces')" class="w-28" />
          <el-input v-model="rollForm.ukuran" type="number" :placeholder="t('pages.mrpPacking.quantity')" class="w-28" />
          <el-input v-model="rollForm.remark" :placeholder="t('pages.mrpPacking.remark')" class="w-48" />
          <el-button type="primary" :loading="acting" @click="addRoll">{{ t('common.add') }}</el-button>
        </div>
      </div>

      <div class="admin-inner-card">
        <h3 class="admin-inner-card__title mb-2">{{ t('pages.mrpPacking.rolls') }}</h3>
        <el-table :data="rolls" border size="small">
          <el-table-column prop="roll_no" :label="t('pages.mrpPacking.artNo')" width="80" />
          <el-table-column prop="lembar" :label="t('pages.mrpPacking.pieces')" width="100" />
          <el-table-column prop="ukuran" :label="t('pages.mrpPacking.quantity')" width="110" />
          <el-table-column prop="remark" :label="t('pages.mrpPacking.remark')" min-width="140" />
          <el-table-column prop="created_at" :label="t('common.date')" />
          <el-table-column v-if="canUpdate && packing?.status === 'in_progress'" :label="t('common.actions')" width="90">
            <template #default="{ row }">
              <el-button link type="danger" @click="deleteRoll(row.id)">{{ t('common.delete') }}</el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <div class="admin-inner-card">
        <div class="mb-2 flex items-center justify-between">
          <h3 class="admin-inner-card__title">PO</h3>
          <el-button
            v-if="canUpdate && packing?.status === 'in_progress' && availablePos.length"
            size="small"
            @click="showAddPo = !showAddPo"
          >
            {{ t('common.add') }}
          </el-button>
        </div>
        <div v-if="showAddPo" class="mb-3">
          <el-table :data="availablePos" border size="small">
            <el-table-column prop="no_po" label="PO" />
            <el-table-column prop="no_so" label="SO" />
            <el-table-column prop="qty_sq" label="Qty" width="90" />
            <el-table-column width="90">
              <template #default="{ row }">
                <el-button link type="primary" @click="addPo(row)">Add</el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
        <el-table :data="packingPos" border size="small">
          <el-table-column prop="no_po" label="PO" />
          <el-table-column prop="no_so" label="SO" />
          <el-table-column prop="qty_sq" label="Qty" width="90" />
          <el-table-column v-if="canUpdate && packing?.status === 'in_progress'" width="90">
            <template #default="{ row }">
              <el-button link type="danger" @click="deletePo(row.id)">{{ t('common.delete') }}</el-button>
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
const rollForm = reactive({ lembar: 1, ukuran: 0, remark: '' })
const headerForm = reactive({ softness: '', gross_weight: '', net_weight: '' })

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
  const res = await act({
    action: 'add_roll',
    lembar: Number(rollForm.lembar) || 1,
    ukuran: Number(rollForm.ukuran) || 0,
    remark: rollForm.remark || '',
  })
  if (res) rollForm.remark = ''
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
  })
}

function deletePo(poRowId) {
  return act({ action: 'delete_po', po_row_id: poRowId })
}

async function finish() {
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
    if (!w) throw new Error('Pop-up diblokir browser')
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
<tr><td class="lbl">PO#:</td><td class="val">${esc(p.no_po)}</td>
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
