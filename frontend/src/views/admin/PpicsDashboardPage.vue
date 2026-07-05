<template>
  <AdminSection :title="t('ppicDashboard.title')" :subtitle="t('ppicDashboard.subtitle')">
    <template #actions>
      <el-input
        v-model="keyword"
        clearable
        class="ppic-toolbar-search"
        :placeholder="t('ppicDashboard.searchPlaceholder')"
      />
      <span v-if="loading" class="text-xs text-slate-500">{{ t('common.loadingData') }}</span>
      <el-button :icon="Refresh" :loading="loading" @click="loadAssignments">{{ t('common.refresh') }}</el-button>
    </template>

    <div class="filter-panel mb-4">
      <p class="filter-panel__title">{{ t('common.filter') }}</p>
      <el-form class="filter-form" label-position="top">
        <el-row :gutter="12">
          <el-col :xs="24" :sm="12" :md="8" :lg="6">
            <el-form-item :label="t('ppicWorkflow.status')">
              <el-select v-model="filterStatus" clearable class="w-full" :placeholder="t('ppicWorkflow.status')">
                <el-option :label="t('ppicWorkflow.pending')" value="pending" />
                <el-option :label="t('ppicWorkflow.inProgress')" value="in_progress" />
                <el-option :label="t('ppicWorkflow.completed')" value="completed" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :xs="24" :sm="12" :md="10" :lg="8">
            <el-form-item :label="t('ppicWorkflow.ppicUser')">
              <el-select
                v-model="filterPpicUserId"
                clearable
                filterable
                class="w-full"
                :placeholder="t('ppicDashboard.filterPpicUser')"
              >
                <el-option
                  v-for="u in ppicUsers"
                  :key="u.id"
                  :label="u.username"
                  :value="u.id"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :xs="24" :sm="8" :md="6" :lg="3" class="ppic-filter-action-col">
            <el-form-item label="&nbsp;">
              <el-button class="w-full" :icon="RefreshLeft" @click="resetFilters">{{ t('common.reset') }}</el-button>
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
    </div>

    <div class="ppic-stats mb-4">
      <div class="ppic-stat">
        <span class="ppic-stat__value">{{ stats.total }}</span>
        <span class="ppic-stat__label">{{ t('common.total') }}</span>
      </div>
      <div class="ppic-stat ppic-stat--pending">
        <span class="ppic-stat__value">{{ stats.pending }}</span>
        <span class="ppic-stat__label">{{ t('ppicWorkflow.pending') }}</span>
      </div>
      <div class="ppic-stat ppic-stat--progress">
        <span class="ppic-stat__value">{{ stats.inProgress }}</span>
        <span class="ppic-stat__label">{{ t('ppicWorkflow.inProgress') }}</span>
      </div>
      <div class="ppic-stat ppic-stat--completed">
        <span class="ppic-stat__value">{{ stats.completed }}</span>
        <span class="ppic-stat__label">{{ t('ppicWorkflow.completed') }}</span>
      </div>
    </div>

    <p class="mb-3 text-xs text-slate-500">{{ t('ppicDashboard.flowHint') }}</p>

    <div class="admin-table-scroll">
      <el-table
        :data="displayedAssignments"
        v-loading="loading"
        border
        stripe
        size="small"
        class="admin-table ppic-assignment-table"
        :empty-text="t('ppicDashboard.tableEmpty')"
      >
        <el-table-column type="index" :label="t('common.noLabel')" width="50" align="center" fixed="left" />
        <el-table-column prop="po_number" :label="t('ppicWorkflow.poNumber')" min-width="150" show-overflow-tooltip>
          <template #default="{ row }">
            <el-button v-if="row.po_id" link type="primary" @click="goPo(row.po_id)">
              {{ row.po_number || `#${row.po_id}` }}
            </el-button>
            <span v-else>{{ row.po_number || '—' }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="customer_name" :label="t('ppicWorkflow.customer')" min-width="180" show-overflow-tooltip />
        <el-table-column prop="ppic_username" :label="t('ppicWorkflow.ppicUser')" min-width="120" show-overflow-tooltip />
        <el-table-column prop="status" :label="t('ppicWorkflow.status')" width="130" align="center">
          <template #default="{ row }">
            <el-tag size="small" :type="statusTagType(row.status)">
              {{ statusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="notes" :label="t('ppicWorkflow.notes')" min-width="160" show-overflow-tooltip />
        <el-table-column prop="assigned_at" :label="t('ppicWorkflow.assignedAt')" width="140">
          <template #default="{ row }">{{ formatDate(row.assigned_at) }}</template>
        </el-table-column>
        <el-table-column prop="completed_at" :label="t('ppicWorkflow.completedAt')" width="140">
          <template #default="{ row }">{{ formatDate(row.completed_at) }}</template>
        </el-table-column>
        <el-table-column :label="t('common.actions')" width="160" fixed="right" align="center">
          <template #default="{ row }">
            <div class="flex flex-wrap items-center justify-center gap-1">
              <el-tooltip
                v-if="canUpdate && row.status === 'pending'"
                :content="t('ppicDashboard.markInProgress')"
                placement="top"
              >
                <el-button type="warning" size="small" :icon="VideoPlay" @click="updateStatus(row, 'in_progress')" />
              </el-tooltip>
              <el-tooltip
                v-if="canUpdate && row.status === 'in_progress'"
                :content="t('ppicDashboard.markComplete')"
                placement="top"
              >
                <el-button type="success" size="small" :icon="Check" @click="updateStatus(row, 'completed')" />
              </el-tooltip>
              <el-tooltip v-if="row.po_id" :content="t('ppicDashboard.openPo')" placement="top">
                <el-button type="primary" link :icon="View" @click="goPo(row.po_id)" />
              </el-tooltip>
            </div>
          </template>
        </el-table-column>
      </el-table>
    </div>
  </AdminSection>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Check, Refresh, RefreshLeft, VideoPlay, View } from '@element-plus/icons-vue'
import AdminSection from '../../components/AdminSection.vue'
import { getPpicDashboard, listPpicUsers, updatePpicAssignmentStatus } from '../../api/client'
import { useModulePermission } from '../../composables/useModulePermission'

const { t } = useI18n()
const { canUpdate } = useModulePermission('ppicDashboard')
const router = useRouter()
const loading = ref(false)
const assignments = ref([])
const ppicUsers = ref([])
const filterStatus = ref('')
const filterPpicUserId = ref(null)
const keyword = ref('')

const stats = computed(() => {
  const list = assignments.value
  return {
    total: list.length,
    pending: list.filter((r) => r.status === 'pending').length,
    inProgress: list.filter((r) => r.status === 'in_progress').length,
    completed: list.filter((r) => r.status === 'completed').length,
  }
})

const displayedAssignments = computed(() => {
  const q = keyword.value.trim().toLowerCase()
  if (!q) return assignments.value
  return assignments.value.filter((row) => {
    const haystack = [
      row.po_number,
      row.customer_name,
      row.ppic_username,
      row.notes,
      statusLabel(row.status),
    ]
      .filter(Boolean)
      .join(' ')
      .toLowerCase()
    return haystack.includes(q)
  })
})

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

async function loadPpicUsers() {
  try {
    ppicUsers.value = await listPpicUsers()
  } catch {
    ppicUsers.value = []
  }
}

async function loadAssignments() {
  loading.value = true
  try {
    const params = {}
    if (filterStatus.value) params.status = filterStatus.value
    if (filterPpicUserId.value) params.user_id = filterPpicUserId.value
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

function resetFilters() {
  filterStatus.value = ''
  filterPpicUserId.value = null
  keyword.value = ''
  loadAssignments()
}

function goPo(poId) {
  router.push({ path: '/admin/po', query: { po_id: String(poId) } })
}

watch([filterStatus, filterPpicUserId], () => {
  loadAssignments()
})

onMounted(async () => {
  await loadPpicUsers()
  await loadAssignments()
})
</script>

<style scoped>
.ppic-stats {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
}

@media (min-width: 640px) {
  .ppic-stats {
    grid-template-columns: repeat(4, minmax(0, 1fr));
  }
}

.ppic-stat {
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  background: #fff;
  padding: 12px 14px;
}

.ppic-stat__value {
  display: block;
  font-size: 1.35rem;
  font-weight: 700;
  line-height: 1.2;
  color: #0f172a;
}

.ppic-stat__label {
  display: block;
  margin-top: 4px;
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.03em;
  text-transform: uppercase;
  color: #64748b;
}

.ppic-stat--pending .ppic-stat__value {
  color: #0369a1;
}

.ppic-stat--progress .ppic-stat__value {
  color: #b45309;
}

.ppic-stat--completed .ppic-stat__value {
  color: #15803d;
}

.ppic-filter-action-col {
  display: flex;
  align-items: flex-end;
}

.ppic-assignment-table {
  width: 100%;
  min-width: 1180px;
}
</style>
