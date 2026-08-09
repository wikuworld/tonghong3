<template>
  <AdminSection :title="t('pages.mrpGudangFg.title')" :subtitle="t('pages.mrpGudangFg.subtitle')">
    <template #actions>
      <el-button :icon="Refresh" :loading="loading" @click="reload">{{ t('common.refresh') }}</el-button>
    </template>

    <div v-if="canUpdate" class="admin-inner-card mb-4">
      <h3 class="admin-inner-card__title mb-2">{{ t('pages.mrpGudangFg.outTitle') }}</h3>
      <div class="flex gap-2 flex-wrap">
        <el-input v-model="outForm.kode_packing" :placeholder="t('pages.mrpPacking.kodePacking')" class="max-w-xs" />
        <el-input v-model="outForm.keterangan" :placeholder="t('common.notes')" class="max-w-xs" />
        <el-button type="danger" :loading="outing" @click="doOut">OUT</el-button>
      </div>
    </div>

    <div class="admin-inner-card">
      <el-table :data="rows" v-loading="loading" border stripe size="small" class="admin-table">
        <el-table-column type="index" width="56" :label="t('common.noLabel')" align="center" />
        <el-table-column prop="kode_packing" :label="t('pages.mrpPacking.kodePacking')" min-width="140" />
        <el-table-column prop="kode_wip" label="WIP" min-width="120" />
        <el-table-column prop="customer" :label="t('common.customer')" min-width="120" />
        <el-table-column prop="total_lembar" label="Lembar" width="90" />
        <el-table-column prop="total_ukuran" label="Ukuran" width="90" />
        <el-table-column prop="status" :label="t('common.status')" width="100" />
        <el-table-column :label="t('pages.mrpGudangFg.erpDelivery')" min-width="160">
          <template #default="{ row }">
            <el-button
              v-if="row.erp_delivery_id"
              link
              type="primary"
              @click="$router.push({ path: '/admin/delivery', query: { delivery_id: row.erp_delivery_id } })"
            >
              {{ row.erp_delivery_number || `#${row.erp_delivery_id}` }}
            </el-button>
            <span v-else-if="row.bridge_status === 'failed'" class="text-red-600">
              {{ t('pages.mrpGudangFg.bridgeFailed') }}
            </span>
            <span v-else class="text-gray-400">—</span>
          </template>
        </el-table-column>
        <el-table-column prop="date_in" :label="t('pages.mrpGudangFg.dateIn')" min-width="140" />
        <el-table-column :label="t('common.actions')" width="100" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="openDetail(row)">{{ t('common.detail') }}</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <el-drawer v-model="detailOpen" size="45%" :title="detail?.fg?.kode_packing || t('common.detail')">
      <template v-if="detail">
        <div class="text-sm mb-3 space-y-1">
          <div>WIP: {{ detail.fg.kode_wip }}</div>
          <div>{{ t('common.customer') }}: {{ detail.fg.customer }}</div>
          <div>{{ t('common.status') }}: {{ detail.fg.status }}</div>
          <div>Lembar / Ukuran: {{ detail.fg.total_lembar }} / {{ detail.fg.total_ukuran }}</div>
          <div v-if="detail.fg.date_out">OUT: {{ detail.fg.date_out }} — {{ detail.fg.keterangan_out }}</div>
          <div v-if="detail.fg.erp_delivery_id" class="flex items-center gap-1">
            <span>{{ t('pages.mrpGudangFg.erpDelivery') }}:</span>
            <el-button
              link
              type="primary"
              @click="$router.push({ path: '/admin/delivery', query: { delivery_id: detail.fg.erp_delivery_id } })"
            >
              {{ detail.fg.erp_delivery_number || `#${detail.fg.erp_delivery_id}` }}
            </el-button>
          </div>
          <div v-if="detail.fg.bridge_error" class="text-red-600">
            {{ detail.fg.bridge_error }}
          </div>
        </div>
        <h4 class="mb-2 font-semibold">Rolls</h4>
        <el-table :data="detail.rolls || []" border size="small" class="mb-4">
          <el-table-column prop="roll_no" label="#" width="60" />
          <el-table-column prop="lembar" label="Lembar" />
          <el-table-column prop="ukuran" label="Ukuran" />
        </el-table>
        <h4 class="mb-2 font-semibold">PO</h4>
        <el-table :data="detail.packing_pos || []" border size="small">
          <el-table-column prop="no_po" label="PO" />
          <el-table-column prop="no_so" label="SO" />
          <el-table-column prop="qty_sq" label="Qty" />
          <el-table-column prop="source_detail_id" label="PO Detail" width="100" />
        </el-table>
      </template>
    </el-drawer>
  </AdminSection>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessage } from 'element-plus'
import { Refresh } from '@element-plus/icons-vue'
import AdminSection from '../../../components/AdminSection.vue'
import { can } from '../../../security/permissions'
import { mrpGetGudangFg, mrpGudangFgOut, mrpListGudangFg } from '../../../api/client'

const { t } = useI18n()
const loading = ref(false)
const outing = ref(false)
const rows = ref([])
const detailOpen = ref(false)
const detail = ref(null)
const canUpdate = computed(() => can('mrpShopfloor', 'update'))
const outForm = reactive({ kode_packing: '', keterangan: '' })

async function reload() {
  loading.value = true
  try {
    rows.value = await mrpListGudangFg()
  } catch (e) {
    ElMessage.error(e.message || String(e))
  } finally {
    loading.value = false
  }
}

async function doOut() {
  if (!outForm.kode_packing.trim()) return
  outing.value = true
  try {
    const res = await mrpGudangFgOut({ ...outForm })
    const dn = res?.erp_delivery_number || (res?.erp_delivery_id ? `#${res.erp_delivery_id}` : '')
    ElMessage.success(
      dn
        ? t('pages.mrpGudangFg.outBridged', { delivery: dn })
        : t('common.saved'),
    )
    outForm.kode_packing = ''
    outForm.keterangan = ''
    await reload()
  } catch (e) {
    ElMessage.error(e.message || String(e))
  } finally {
    outing.value = false
  }
}

async function openDetail(row) {
  try {
    detail.value = await mrpGetGudangFg(row.id)
    detailOpen.value = true
  } catch (e) {
    ElMessage.error(e.message || String(e))
  }
}

onMounted(reload)
</script>
