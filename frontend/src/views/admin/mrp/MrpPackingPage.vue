<template>
  <AdminSection :title="t('pages.mrpPacking.title')" :subtitle="t('pages.mrpPacking.subtitle')">
    <template #actions>
      <el-button :icon="Refresh" :loading="loading" @click="reload">{{ t('common.refresh') }}</el-button>
    </template>

    <div v-if="canCreate" class="admin-inner-card mb-4">
      <h3 class="admin-inner-card__title mb-2">{{ t('pages.mrpPacking.scanWip') }}</h3>
      <div class="flex gap-2 mb-3">
        <el-input v-model="wipCode" :placeholder="'WIP-...'" class="max-w-xs" @keyup.enter="scanWip" />
        <el-button type="primary" :loading="scanning" @click="scanWip">Scan WIP</el-button>
      </div>
      <el-table v-if="poList.length" :data="poList" border size="small">
        <el-table-column prop="no_po" label="PO" min-width="120" />
        <el-table-column prop="no_so" label="SO" min-width="100" />
        <el-table-column prop="item_name" label="Item" min-width="140" />
        <el-table-column prop="customer" :label="t('common.customer')" min-width="120" />
        <el-table-column prop="qty_sq" label="Qty" width="90" />
        <el-table-column :label="t('common.actions')" width="100">
          <template #default="{ row }">
            <el-button link type="success" :loading="starting" @click="startPacking(row)">
              {{ t('pages.mrpPacking.start') }}
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <div class="admin-inner-card">
      <h3 class="admin-inner-card__title mb-2">{{ t('pages.mrpPacking.listTitle') }}</h3>
      <el-table :data="rows" v-loading="loading" border stripe size="small" class="admin-table">
        <el-table-column type="index" width="56" :label="t('common.noLabel')" align="center" />
        <el-table-column prop="kode_packing" :label="t('pages.mrpPacking.kodePacking')" min-width="140" />
        <el-table-column prop="kode_wip" label="WIP" min-width="120" />
        <el-table-column prop="no_po" label="PO" width="120" />
        <el-table-column prop="customer" :label="t('common.customer')" min-width="120" />
        <el-table-column prop="total_lembar" label="Lembar" width="90" />
        <el-table-column prop="total_ukuran" label="Ukuran" width="90" />
        <el-table-column prop="status" :label="t('common.status')" width="110" />
        <el-table-column :label="t('common.actions')" width="100" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="$router.push(`/admin/mrp/packing/${row.id}`)">
              {{ t('common.detail') }}
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>
  </AdminSection>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Refresh } from '@element-plus/icons-vue'
import AdminSection from '../../../components/AdminSection.vue'
import { can } from '../../../security/permissions'
import { mrpListPacking, mrpPackingScanWip, mrpStartPacking } from '../../../api/client'

const { t } = useI18n()
const router = useRouter()
const loading = ref(false)
const scanning = ref(false)
const starting = ref(false)
const rows = ref([])
const wipCode = ref('')
const scannedWip = ref('')
const poList = ref([])
const canCreate = computed(() => can('mrpShopfloor', 'create'))

async function reload() {
  loading.value = true
  try {
    rows.value = await mrpListPacking()
  } catch (e) {
    ElMessage.error(e.message || String(e))
  } finally {
    loading.value = false
  }
}

async function scanWip() {
  if (!wipCode.value.trim()) return
  scanning.value = true
  try {
    const data = await mrpPackingScanWip(wipCode.value.trim())
    scannedWip.value = data.kode_wip
    poList.value = data.po_list || []
    if (!poList.value.length) ElMessage.warning(t('pages.mrpPacking.noPo'))
  } catch (e) {
    poList.value = []
    ElMessage.error(e.message || String(e))
  } finally {
    scanning.value = false
  }
}

async function startPacking(row) {
  starting.value = true
  try {
    const res = await mrpStartPacking({
      kode_wip: scannedWip.value,
      no_po: row.no_po,
      no_so: row.no_so || '',
      customer: row.customer || '',
      qty_sq: row.qty_sq || 0,
    })
    ElMessage.success(t('common.saved'))
    router.push(`/admin/mrp/packing/${res.id}`)
  } catch (e) {
    ElMessage.error(e.message || String(e))
  } finally {
    starting.value = false
  }
}

onMounted(reload)
</script>
