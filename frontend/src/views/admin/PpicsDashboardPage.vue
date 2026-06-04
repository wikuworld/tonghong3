<template>
  <AdminSection :title="t('ppicDashboard.title')" :subtitle="t('ppicDashboard.subtitle')">
    <template #actions>
      <el-select v-model="filterStatus" clearable class="w-[180px]" :placeholder="t('ppicWorkflow.status')" @change="loadAssignments">
        <el-option :label="t('ppicWorkflow.pending')" value="pending" />
        <el-option :label="t('ppicWorkflow.inProgress')" value="in_progress" />
        <el-option :label="t('ppicWorkflow.completed')" value="completed" />
      </el-select>
      <el-button :loading="loading" @click="loadAssignments">{{ t('common.search') }}</el-button>
    </template>

    <el-table :data="assignments" v-loading="loading" border stripe size="small" class="admin-table" table-layout="fixed" :empty-text="t('common.tableEmpty')">
      <el-table-column type="index" width="50" align="center" />
      <el-table-column prop="po_number" :label="t('ppicWorkflow.poNumber')" min-width="140" />
      <el-table-column prop="customer_name" :label="t('ppicWorkflow.customer')" min-width="140" />
      <el-table-column prop="ppic_username" :label="t('ppicWorkflow.ppicUser')" min-width="120" />
      <el-table-column prop="status" :label="t('ppicWorkflow.status')" width="140" align="center">
        <template #default="{ row }">
          <el-tag size="small" :type="statusTagType(row.status)">
            {{ statusLabel(row.status) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="notes" :label="t('ppicWorkflow.notes')" min-width="160" show-overflow-tooltip />
      <el-table-column prop="assigned_at" :label="t('ppicWorkflow.assignedAt')" width="160">
        <template #default="{ row }">{{ formatDate(row.assigned_at) }}</template>
      </el-table-column>
      <el-table-column prop="completed_at" :label="t('ppicWorkflow.completedAt')" width="160">
        <template #default="{ row }">{{ formatDate(row.completed_at) }}</template>
      </el-table-column>
      <el-table-column :label="t('common.actions')" width="180" fixed="right" align="center">
        <template #default="{ row }">
          <div class="flex flex-wrap items-center justify-center gap-1">
            <el-button
              v-if="row.status === 'pending'"
              type="warning"
              size="small"
              @click="updateStatus(row, 'in_progress')"
            >
              {{ t('ppicDashboard.markInProgress') }}
            </el-button>
            <el-button
              v-if="row.status === 'in_progress'"
              type="success"
              size="small"
              @click="updateStatus(row, 'completed')"
            >
              {{ t('ppicDashboard.markComplete') }}
            </el-button>
            <el-button
              type="primary"
              link
              size="small"
              @click="goPo(row.po_id)"
            >
              {{ t('pages.marketingFlow.openPo') }}
            </el-button>
          </div>
        </template>
      </el-table-column>
    </el-table>
  </AdminSection>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import AdminSection from '../../components/AdminSection.vue'
import { getPpicDashboard, updatePpicAssignmentStatus } from '../../api/client'

const { t } = useI18n()
const router = useRouter()
const loading = ref(false)
const assignments = ref([])
const filterStatus = ref(null)

function statusTagType(status) {
  const map = {
    pending: 'info',
    in_progress: 'warning',
    completed: 'success',
  }
  return map[status] || ''
}

function statusLabel(status) {
  const map = {
    pending: t('ppicWorkflow.pending'),
    in_progress: t('ppicWorkflow.inProgress'),
    completed: t('ppicWorkflow.completed'),
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

async function loadAssignments() {
  loading.value = true
  try {
    const params = {}
    if (filterStatus.value) {
      params.status = filterStatus.value
    }
    assignments.value = await getPpicDashboard(params)
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  } finally {
    loading.value = false
  }
}

async function updateStatus(row, newStatus) {
  try {
    await updatePpicAssignmentStatus(row.id, { status: newStatus })
    ElMessage.success(t('common.saveSuccess'))
    await loadAssignments()
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  }
}

function goPo(poId) {
  router.push({ path: '/admin/po', query: { po_id: String(poId) } })
}

onMounted(() => {
  loadAssignments()
})
</script>

<style scoped>
</style>
