<template>
  <AdminSection :title="title" :subtitle="t('pages.mrpPacking.detailSubtitle')">
    <template #actions>
      <el-button @click="$router.push('/admin/mrp/packing')">{{ t('common.close') }}</el-button>
      <el-button :icon="Refresh" :loading="loading" @click="reload">{{ t('common.refresh') }}</el-button>
      <el-button v-if="packing" @click="printLabel">Print</el-button>
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
          <div><strong>WIP</strong><div>{{ packing.kode_wip }}</div></div>
          <div><strong>PO</strong><div>{{ packing.no_po }}</div></div>
          <div><strong>{{ t('common.status') }}</strong><div>{{ packing.status }}</div></div>
          <div><strong>{{ t('common.customer') }}</strong><div>{{ packing.customer }}</div></div>
          <div><strong>Lembar</strong><div>{{ packing.total_lembar }}</div></div>
          <div><strong>Ukuran</strong><div>{{ packing.total_ukuran }}</div></div>
        </div>
      </div>

      <div v-if="canUpdate && packing?.status === 'in_progress'" class="admin-inner-card">
        <h3 class="admin-inner-card__title mb-2">{{ t('pages.mrpPacking.addRoll') }}</h3>
        <div class="flex gap-2 flex-wrap">
          <el-input v-model="rollForm.lembar" type="number" placeholder="Lembar" class="w-28" />
          <el-input v-model="rollForm.ukuran" type="number" placeholder="Ukuran" class="w-28" />
          <el-button type="primary" :loading="acting" @click="addRoll">{{ t('common.add') }}</el-button>
        </div>
      </div>

      <div class="admin-inner-card">
        <h3 class="admin-inner-card__title mb-2">Rolls</h3>
        <el-table :data="rolls" border size="small">
          <el-table-column prop="roll_no" label="#" width="70" />
          <el-table-column prop="lembar" label="Lembar" width="100" />
          <el-table-column prop="ukuran" label="Ukuran" width="100" />
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
const rollForm = reactive({ lembar: 1, ukuran: 0 })

async function reload() {
  loading.value = true
  try {
    const data = await mrpGetPacking(route.params.id)
    packing.value = data.packing
    rolls.value = data.rolls || []
    packingPos.value = data.packing_pos || []
    availablePos.value = data.available_pos || []
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
  } catch (e) {
    ElMessage.error(e.message || String(e))
  } finally {
    acting.value = false
  }
}

function addRoll() {
  return act({ action: 'add_roll', lembar: Number(rollForm.lembar) || 1, ukuran: Number(rollForm.ukuran) || 0 })
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
    const rollsHtml = (data.rolls || [])
      .map((r) => `<tr><td>${r.roll_no}</td><td>${r.lembar}</td><td>${r.ukuran}</td></tr>`)
      .join('')
    const w = window.open('', '_blank')
    w.document.write(`<!DOCTYPE html><html><head><title>${p.kode_packing}</title>
      <style>body{font-family:sans-serif;padding:24px} table{border-collapse:collapse;width:100%}
      td,th{border:1px solid #ccc;padding:6px}</style></head><body>
      <h1>${p.kode_packing || ''}</h1>
      <p>WIP: ${p.kode_wip || ''} · PO: ${p.no_po || ''} · ${p.customer || ''}</p>
      <p>Total lembar: ${p.total_lembar || 0} · Ukuran: ${p.total_ukuran || 0}</p>
      <table><thead><tr><th>#</th><th>Lembar</th><th>Ukuran</th></tr></thead>
      <tbody>${rollsHtml}</tbody></table>
      </body></html>`)
    w.document.close()
    w.print()
  } catch (e) {
    ElMessage.error(e.message || String(e))
  }
}

onMounted(reload)
</script>
