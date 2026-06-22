<template>
  <AdminSection :title="t('outstandingMaterial.title')" :subtitle="t('outstandingMaterial.subtitle')">
    <template #actions>
      <el-select v-model="filterStatus" clearable class="w-[180px]" :placeholder="t('outstandingMaterial.status')" @change="loadMaterials">
        <el-option :label="t('outstandingMaterial.pending')" value="pending" />
        <el-option :label="t('outstandingMaterial.partial')" value="partial" />
        <el-option :label="t('outstandingMaterial.fulfilled')" value="fulfilled" />
      </el-select>
      <el-button :loading="loading" @click="loadMaterials">{{ t('common.search') }}</el-button>
    </template>

    <el-table :data="materials" v-loading="loading" border stripe size="small" class="admin-table" table-layout="fixed" :empty-text="t('common.tableEmpty')">
      <el-table-column type="index" width="50" align="center" />
      <el-table-column prop="po_number" :label="t('outstandingMaterial.poNumber')" min-width="140" />
      <el-table-column prop="customer_name" :label="t('outstandingMaterial.customer')" min-width="140" />
      <el-table-column prop="material_name" :label="t('outstandingMaterial.materialName')" min-width="200" show-overflow-tooltip />
      <el-table-column prop="total_qty" :label="t('outstandingMaterial.totalQty')" width="120" align="right">
        <template #default="{ row }">{{ formatQty(row.total_qty) }}</template>
      </el-table-column>
      <el-table-column prop="delivered_qty" :label="t('outstandingMaterial.deliveredQty')" width="120" align="right">
        <template #default="{ row }">{{ formatQty(row.delivered_qty) }}</template>
      </el-table-column>
      <el-table-column prop="balance_qty" :label="t('outstandingMaterial.balanceQty')" width="120" align="right">
        <template #default="{ row }">{{ formatQty(row.balance_qty) }}</template>
      </el-table-column>
      <el-table-column prop="status" :label="t('outstandingMaterial.status')" width="140" align="center">
        <template #default="{ row }">
          <el-tag size="small" :type="statusTagType(row.status)">
            {{ statusLabel(row.status) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="updated_at" :label="t('common.date')" width="160">
        <template #default="{ row }">{{ formatDate(row.updated_at) }}</template>
      </el-table-column>
      <el-table-column :label="t('common.actions')" width="200" fixed="right" align="center">
        <template #default="{ row }">
          <div class="flex flex-wrap items-center justify-center gap-1">
            <el-button
              v-if="canUpdate && row.status !== 'fulfilled'"
              type="success"
              size="small"
              @click="openDeliverDialog(row)"
            >
              {{ t('outstandingMaterial.markDelivered') }}
            </el-button>
            <el-button
              type="primary"
              link
              size="small"
              @click="goPoDetail(row.po_detail_id)"
            >
              {{ t('common.detail') }}
            </el-button>
          </div>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="deliverDialogVisible" :title="t('outstandingMaterial.markDelivered')" width="600px" destroy-on-close align-center>
      <el-form label-width="120px">
        <el-form-item :label="t('outstandingMaterial.materialName')">
          <el-input v-model="currentMaterial.material_name" disabled />
        </el-form-item>
        <el-form-item :label="t('outstandingMaterial.totalQty')">
          <el-input :value="formatQty(currentMaterial.total_qty)" disabled />
        </el-form-item>
        <el-form-item :label="t('outstandingMaterial.deliveredQty')">
          <el-input :value="formatQty(currentMaterial.delivered_qty)" disabled />
        </el-form-item>
        <el-form-item :label="t('outstandingMaterial.deliverQty')" required>
          <el-input-number v-model="deliverQty" :min="0" :max="currentMaterial.balance_qty || 0" :precision="2" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="deliverDialogVisible = false">{{ t('common.cancel') }}</el-button>
        <el-button v-if="canUpdate" type="primary" :loading="saving" @click="submitDelivery">{{ t('common.save') }}</el-button>
      </template>
    </el-dialog>
  </AdminSection>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import AdminSection from '../../components/AdminSection.vue'
import { listOutstandingMaterials, deliverOutstandingMaterial } from '../../api/client'
import { useModulePermission } from '../../composables/useModulePermission'

const { canUpdate } = useModulePermission('outstandingMaterials')

const { t } = useI18n()
const router = useRouter()
const loading = ref(false)
const saving = ref(false)
const materials = ref([])
const filterStatus = ref(null)
const deliverDialogVisible = ref(false)
const currentMaterial = ref({})
const deliverQty = ref(0)

function statusTagType(status) {
  const map = {
    pending: 'info',
    partial: 'warning',
    fulfilled: 'success',
  }
  return map[status] || ''
}

function statusLabel(status) {
  const map = {
    pending: t('outstandingMaterial.pending'),
    partial: t('outstandingMaterial.partial'),
    fulfilled: t('outstandingMaterial.fulfilled'),
  }
  return map[status] || status || '—'
}

function formatDate(dateStr) {
  if (!dateStr) return '—'
  try {
    const d = new Date(dateStr)
    return d.toLocaleDateString('id-ID', { year: 'numeric', month: 'short', day: 'numeric' })
  } catch {
    return dateStr
  }
}

function formatQty(qty) {
  if (qty == null) return '—'
  return Number(qty).toLocaleString('id-ID', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

async function loadMaterials() {
  loading.value = true
  try {
    const params = {}
    if (filterStatus.value) {
      params.status = filterStatus.value
    }
    materials.value = await listOutstandingMaterials(params)
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  } finally {
    loading.value = false
  }
}

function openDeliverDialog(row) {
  currentMaterial.value = { ...row }
  deliverQty.value = 0
  deliverDialogVisible.value = true
}

async function submitDelivery() {
  if (deliverQty.value <= 0) {
    ElMessage.warning(t('pages.outstandingMaterial.deliverQtyMustPositive'))
    return
  }
  saving.value = true
  try {
    await deliverOutstandingMaterial(currentMaterial.value.id, deliverQty.value)
    ElMessage.success(t('common.saveSuccess'))
    deliverDialogVisible.value = false
    await loadMaterials()
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  } finally {
    saving.value = false
  }
}

function goPoDetail(poDetailId) {
  router.push({ path: '/admin/po', query: { detail: String(poDetailId) } })
}

onMounted(() => {
  loadMaterials()
})
</script>

<style scoped>
.admin-table {
  width: 100%;
}
</style>