<template>
  <AdminSection :title="t('pages.userAccess.title')" :subtitle="t('pages.userAccess.subtitle')">
    <template #actions>
      <el-input
        v-if="activeTab === 'users'"
        v-model="userKeyword"
        :placeholder="t('pages.userAccess.searchPlaceholder')"
        clearable
        class="user-access-toolbar-search"
      />
      <span v-if="loading" class="text-xs text-slate-500">{{ t('common.loadingData') }}</span>
      <el-button :icon="Refresh" :loading="loading" @click="load">{{ t('common.refresh') }}</el-button>
      <el-button v-if="activeTab === 'users' && canCreate" type="primary" :icon="Plus" @click="openCreate">
        {{ t('common.create') }}
      </el-button>
      <template v-if="activeTab === 'matrix'">
        <el-tag v-if="hasMatrixChanges" type="warning" effect="dark">{{ t('pages.userAccess.unsavedChanges') }}</el-tag>
        <el-button :icon="RefreshLeft" :disabled="!hasMatrixChanges" @click="resetMatrix">{{ t('common.reset') }}</el-button>
        <el-button
          v-if="canUpdate"
          type="primary"
          :icon="DocumentChecked"
          :loading="savingMatrix"
          :disabled="!hasMatrixChanges"
          @click="saveMatrix"
        >
          {{ t('pages.userAccess.saveMatrix') }}
        </el-button>
      </template>
    </template>

    <el-tabs v-model="activeTab" class="user-access-tabs">
      <el-tab-pane :label="t('pages.userAccess.usersTab')" name="users">
        <div class="admin-inner-card">
          <div class="admin-inner-card__head user-access-inner-head">
            <div>
              <h3 class="admin-inner-card__title">{{ t('pages.userAccess.usersSectionTitle') }}</h3>
              <p class="admin-inner-card__sub">{{ t('pages.userAccess.usersSectionSub') }}</p>
            </div>
            <el-tooltip placement="top-start" :show-after="200">
              <template #content>{{ t('pages.userAccess.usersPageHint') }}</template>
              <el-icon class="user-access-hint" :size="16" tabindex="0" :aria-label="t('pages.userAccess.usersPageHint')">
                <InfoFilled />
              </el-icon>
            </el-tooltip>
          </div>

          <div class="admin-stats-grid admin-stats-grid--4 user-access-stats">
            <div class="admin-stat-card">
              <span class="admin-stat-card__value">{{ userStats.total }}</span>
              <span class="admin-stat-card__label">{{ t('pages.userAccess.statTotal') }}</span>
            </div>
            <div class="admin-stat-card admin-stat-card--info">
              <span class="admin-stat-card__value">{{ userStats.shown }}</span>
              <span class="admin-stat-card__label">{{ t('pages.userAccess.statShown') }}</span>
            </div>
            <div class="admin-stat-card admin-stat-card--success">
              <span class="admin-stat-card__value">{{ userStats.active }}</span>
              <span class="admin-stat-card__label">{{ t('pages.userAccess.statActive') }}</span>
            </div>
            <div class="admin-stat-card">
              <span class="admin-stat-card__value">{{ userStats.inactive }}</span>
              <span class="admin-stat-card__label">{{ t('pages.userAccess.statInactive') }}</span>
            </div>
          </div>

          <div class="filter-panel user-access-filter-panel">
            <p class="filter-panel__title">{{ t('common.filter') }}</p>
            <el-select v-model="userRoleFilter" clearable class="user-access-filter-role" :placeholder="t('pages.userAccess.filterRole')">
              <el-option v-for="r in roles" :key="r" :label="roleLabel(r)" :value="r" />
            </el-select>
          </div>

          <p class="admin-scroll-hint">{{ t('pages.userAccess.scrollHint') }}</p>

          <div class="admin-table-scroll user-access-table-wrap">
            <el-table
              :data="filteredUsers"
              v-loading="loading"
              border
              stripe
              size="small"
              class="admin-table user-access-table"
              table-layout="fixed"
              row-key="id"
              :empty-text="t('pages.userAccess.tableEmpty')"
              max-height="58vh"
            >
              <el-table-column type="index" :label="t('common.noLabel')" width="56" align="center" />
              <el-table-column prop="username" :label="t('pages.login.username')" min-width="180" show-overflow-tooltip />
              <el-table-column :label="t('pages.userAccess.roleLabel')" width="140">
                <template #default="{ row }">
                  <el-tag size="small" effect="plain">{{ roleLabel(row.role) }}</el-tag>
                </template>
              </el-table-column>
              <el-table-column :label="t('common.status')" width="120" align="center">
                <template #default="{ row }">
                  <el-switch
                    v-if="canUpdate"
                    :model-value="!!row.is_active"
                    :loading="row._toggling"
                    @change="(v) => toggleUserActive(row, v)"
                  />
                  <el-tag v-else :type="row.is_active ? 'success' : 'info'">
                    {{ row.is_active ? t('status.active') : t('status.inactive') }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column :label="t('common.actions')" width="88" align="center" fixed="right">
                <template #default="{ row }">
                  <el-tooltip v-if="canUpdate" :content="t('common.edit')" placement="top">
                    <el-button :icon="EditPen" link type="primary" :aria-label="t('common.edit')" @click="openEdit(row)" />
                  </el-tooltip>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </div>
      </el-tab-pane>

      <el-tab-pane :label="t('pages.userAccess.permissionMatrixTab')" name="matrix">
        <div class="admin-inner-card">
          <div class="admin-inner-card__head user-access-inner-head">
            <div>
              <h3 class="admin-inner-card__title">{{ t('pages.userAccess.matrixSectionTitle') }}</h3>
              <p class="admin-inner-card__sub">{{ t('pages.userAccess.matrixSectionSub') }}</p>
            </div>
            <el-tooltip placement="top-start" :show-after="200">
              <template #content>{{ t('pages.userAccess.matrixPageHint') }}</template>
              <el-icon class="user-access-hint" :size="16" tabindex="0" :aria-label="t('pages.userAccess.matrixPageHint')">
                <InfoFilled />
              </el-icon>
            </el-tooltip>
          </div>

          <div class="admin-stats-grid admin-stats-grid--3 user-access-stats">
            <div class="admin-stat-card">
              <span class="admin-stat-card__value">{{ matrixStats.modules }}</span>
              <span class="admin-stat-card__label">{{ t('pages.userAccess.statModules') }}</span>
            </div>
            <div class="admin-stat-card admin-stat-card--info">
              <span class="admin-stat-card__value">{{ matrixStats.rows }}</span>
              <span class="admin-stat-card__label">{{ t('pages.userAccess.statMatrixRows') }}</span>
            </div>
            <div class="admin-stat-card" :class="hasMatrixChanges ? 'admin-stat-card--warn' : 'admin-stat-card--success'">
              <span class="admin-stat-card__value">{{ hasMatrixChanges ? '!' : '✓' }}</span>
              <span class="admin-stat-card__label">
                {{ hasMatrixChanges ? t('pages.userAccess.unsavedChanges') : t('pages.userAccess.statMatrixSynced') }}
              </span>
            </div>
          </div>

          <div class="filter-panel user-access-filter-panel">
            <p class="filter-panel__title">{{ t('common.filter') }}</p>
            <div class="user-access-matrix-filters">
              <el-input v-model="matrixKeyword" clearable :placeholder="t('pages.userAccess.filterModuleAction')" />
              <el-select v-model="matrixActionFilter" clearable :placeholder="t('pages.userAccess.filterAction')">
                <el-option v-for="a in availableActions" :key="a" :label="actionLabel(a)" :value="a" />
              </el-select>
            </div>
          </div>

          <p class="admin-scroll-hint">{{ t('pages.userAccess.matrixScrollHint') }}</p>

          <div class="matrix-scroll user-access-matrix-wrap">
            <table class="matrix-table w-full border-collapse text-sm">
              <thead>
                <tr>
                  <th class="sticky-col">{{ t('pages.userAccess.matrixModule') }}</th>
                  <th class="sticky-col-2">{{ t('pages.userAccess.matrixAction') }}</th>
                  <th class="matrix-admin-col">
                    <span>admin</span>
                    <el-tooltip placement="top" :show-after="200">
                      <template #content>{{ t('pages.userAccess.adminRoleHint') }}</template>
                      <el-icon class="user-access-hint user-access-hint--inline" :size="14" tabindex="0" :aria-label="t('pages.userAccess.adminRoleHint')">
                        <InfoFilled />
                      </el-icon>
                    </el-tooltip>
                  </th>
                  <th v-for="r in matrixEditableRoles" :key="`h-${r}`">{{ r }}</th>
                  <th>{{ t('pages.userAccess.matrixBulk') }}</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="row in filteredMatrixRows" :key="`${row.module}-${row.action}`">
                  <td class="sticky-col">{{ moduleLabel(row.module) }}</td>
                  <td class="sticky-col-2">{{ actionLabel(row.action) }}</td>
                  <td class="text-center matrix-admin-col">
                    <el-checkbox :model-value="true" disabled />
                  </td>
                  <td v-for="r in matrixEditableRoles" :key="`${row.module}-${row.action}-${r}`" class="text-center">
                    <el-checkbox
                      :model-value="roleChecked(row.module, row.action, r)"
                      @change="(v) => toggleRole(row.module, row.action, r, v)"
                    />
                  </td>
                  <td class="text-nowrap text-center">
                    <div class="flex flex-wrap items-center justify-center gap-0">
                      <el-tooltip :content="t('pages.userAccess.matrixSelectAllRoles')" placement="top">
                        <el-button
                          link
                          type="primary"
                          size="small"
                          :icon="CircleCheck"
                          :aria-label="t('pages.userAccess.matrixSelectAllRoles')"
                          @click="setAllRoles(row.module, row.action, true)"
                        />
                      </el-tooltip>
                      <el-tooltip :content="t('pages.userAccess.matrixClearAllRoles')" placement="top">
                        <el-button
                          link
                          type="danger"
                          size="small"
                          :icon="CircleClose"
                          :aria-label="t('pages.userAccess.matrixClearAllRoles')"
                          @click="setAllRoles(row.module, row.action, false)"
                        />
                      </el-tooltip>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </el-tab-pane>
    </el-tabs>

    <el-dialog
      v-model="dialogVisible"
      width="560px"
      destroy-on-close
      align-center
      class="user-access-dialog"
      :show-close="false"
      @closed="resetForm"
    >
      <div class="user-access-dialog-header">
        <div class="user-access-dialog-header__main">
          <h3 class="user-access-dialog-header__title">
            {{ isEdit ? t('pages.userAccess.dialogEdit') : t('pages.userAccess.dialogAdd') }}
          </h3>
          <p class="user-access-dialog-header__sub">{{ t('pages.userAccess.dialogFormSub') }}</p>
        </div>
        <el-button :icon="Close" circle text @click="dialogVisible = false" :aria-label="t('common.close')" />
      </div>

      <div class="user-access-dialog-panel">
        <el-form ref="formRef" :model="form" label-position="top" @submit.prevent="submit">
          <el-form-item :label="t('pages.login.username')" prop="username" :rules="usernameRules">
            <el-input v-model="form.username" :disabled="isEdit" autocomplete="off" />
          </el-form-item>
          <el-form-item :label="t('pages.userAccess.roleLabel')" prop="role" required>
            <el-select v-model="form.role" class="w-full">
              <el-option v-for="r in roles" :key="r" :label="roleLabel(r)" :value="r" />
            </el-select>
          </el-form-item>
          <el-form-item :label="t('pages.login.password')" prop="password" :rules="passwordRules">
            <el-input
              v-model="form.password"
              type="password"
              show-password
              autocomplete="new-password"
              :placeholder="isEdit ? t('pages.userAccess.keepPasswordHint') : ''"
            />
          </el-form-item>
          <el-form-item :label="t('common.status')">
            <el-switch v-model="form.is_active" :active-text="t('status.active')" :inactive-text="t('status.inactive')" />
          </el-form-item>
        </el-form>
      </div>

      <template #footer>
        <el-button @click="dialogVisible = false">{{ t('common.cancel') }}</el-button>
        <el-button v-if="canCreate || canUpdate" type="primary" :loading="saving" @click="submit">{{ t('common.save') }}</el-button>
      </template>
    </el-dialog>
  </AdminSection>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessage } from 'element-plus'
import {
  CircleCheck,
  CircleClose,
  Close,
  DocumentChecked,
  EditPen,
  InfoFilled,
  Plus,
  Refresh,
  RefreshLeft,
} from '@element-plus/icons-vue'
import AdminSection from '../../components/AdminSection.vue'
import { useModulePermission } from '../../composables/useModulePermission'
import { createUser, getPermissionMatrix, listUsers, savePermissionMatrix, updateUser } from '../../api/client'
import { ACTION_MATRIX, setRuntimePermissionMatrix } from '../../security/permissions'
import { ACTION_LABEL_KEYS, MODULE_LABEL_KEYS } from '../../security/rbac'

const { t } = useI18n()
const { canCreate, canUpdate } = useModulePermission('userAccess')

const loading = ref(false)
const saving = ref(false)
const rows = ref([])
const activeTab = ref('users')
const userKeyword = ref('')
const userRoleFilter = ref('')
const matrixKeyword = ref('')
const matrixActionFilter = ref('')
const dialogVisible = ref(false)
const isEdit = ref(false)
const editingId = ref(null)
const formRef = ref(null)

const roles = ['admin', 'marketing', 'ppic', 'production', 'qc', 'warehouse', 'finance', 'exim', 'sales']
const matrixEditableRoles = roles.filter((r) => r !== 'admin')

const editableMatrix = ref({})
const matrixSavedSnapshot = ref('')
const savingMatrix = ref(false)

const matrixRows = computed(() => {
  const out = []
  Object.entries(editableMatrix.value || ACTION_MATRIX).forEach(([module, actions]) => {
    Object.entries(actions || {}).forEach(([action]) => {
      out.push({ module, action })
    })
  })
  return out.sort((a, b) => `${a.module}.${a.action}`.localeCompare(`${b.module}.${b.action}`))
})

const availableActions = computed(() => [...new Set(matrixRows.value.map((x) => x.action))].sort())

const filteredMatrixRows = computed(() =>
  matrixRows.value.filter((x) => {
    const k = matrixKeyword.value.trim().toLowerCase()
    const moduleText = moduleLabel(x.module).toLowerCase()
    const actionText = actionLabel(x.action).toLowerCase()
    const passKeyword = !k || `${x.module} ${x.action} ${moduleText} ${actionText}`.toLowerCase().includes(k)
    const passAction = !matrixActionFilter.value || x.action === matrixActionFilter.value
    return passKeyword && passAction
  }),
)

const filteredUsers = computed(() =>
  rows.value.filter((u) => {
    const q = userKeyword.value.trim().toLowerCase()
    const passKeyword = !q || `${u.username} ${u.role}`.toLowerCase().includes(q)
    const passRole = !userRoleFilter.value || u.role === userRoleFilter.value
    return passKeyword && passRole
  }),
)

const userStats = computed(() => {
  const total = rows.value.length
  const shown = filteredUsers.value.length
  const active = rows.value.filter((u) => u.is_active).length
  return { total, shown, active, inactive: total - active }
})

const matrixStats = computed(() => ({
  modules: Object.keys(editableMatrix.value || {}).length,
  rows: filteredMatrixRows.value.length,
}))

const normalizedSnapshot = computed(() => JSON.stringify(sanitizeMatrixForSave(editableMatrix.value)))
const hasMatrixChanges = computed(() => normalizedSnapshot.value !== matrixSavedSnapshot.value)

const form = reactive({
  username: '',
  role: 'marketing',
  password: '',
  is_active: true,
})

const usernameRules = computed(() => [
  { required: true, message: t('pages.userAccess.ruleUsername'), trigger: 'blur' },
])

const passwordRules = computed(() => {
  if (isEdit.value) return []
  return [{ required: true, message: t('pages.userAccess.rulePassword'), trigger: 'blur' }]
})

function roleLabel(role) {
  const key = `pages.userAccess.roles.${role}`
  const translated = t(key)
  return translated === key ? role : translated
}

function moduleLabel(moduleKey) {
  const labelKey = MODULE_LABEL_KEYS[moduleKey]
  return labelKey ? t(labelKey) : moduleKey
}

function actionLabel(action) {
  const labelKey = ACTION_LABEL_KEYS[action]
  return labelKey ? t(labelKey) : action
}

function parseErrorMessage(e) {
  const raw = e?.message || ''
  try {
    const j = JSON.parse(raw)
    if (typeof j.detail === 'string') return j.detail
    if (Array.isArray(j.detail)) return j.detail.map((x) => x.msg || JSON.stringify(x)).join('; ')
  } catch {
    /* raw text */
  }
  return raw || t('common.errorGeneric')
}

function normalizeLoadedMatrix(raw) {
  const base = JSON.parse(JSON.stringify(ACTION_MATRIX))
  const src = raw && typeof raw === 'object' ? raw : {}
  Object.entries(base).forEach(([moduleKey, actions]) => {
    const incoming = src[moduleKey]
    if (!incoming || typeof incoming !== 'object') return
    Object.keys(actions).forEach((action) => {
      const list = incoming[action]
      if (!Array.isArray(list)) return
      base[moduleKey][action] = [...new Set(list.map((r) => String(r).trim()).filter((r) => roles.includes(r) && r !== 'admin'))]
    })
  })
  return base
}

function sanitizeMatrixForSave(matrix) {
  const out = {}
  Object.entries(ACTION_MATRIX).forEach(([moduleKey, actions]) => {
    out[moduleKey] = {}
    const src = matrix?.[moduleKey] || {}
    Object.keys(actions).forEach((action) => {
      const list = Array.isArray(src[action]) ? src[action] : []
      out[moduleKey][action] = [...new Set(list.map((r) => String(r).trim()).filter((r) => matrixEditableRoles.includes(r)))].sort()
    })
  })
  return out
}

function roleChecked(moduleKey, action, role) {
  const m = editableMatrix.value[moduleKey] || {}
  const rs = m[action] || []
  return rs.includes(role)
}

function toggleRole(moduleKey, action, role, checked) {
  if (!editableMatrix.value[moduleKey]) editableMatrix.value[moduleKey] = {}
  if (!editableMatrix.value[moduleKey][action]) editableMatrix.value[moduleKey][action] = []
  const arr = editableMatrix.value[moduleKey][action]
  const idx = arr.indexOf(role)
  if (checked && idx < 0) arr.push(role)
  if (!checked && idx >= 0) arr.splice(idx, 1)
}

function setAllRoles(moduleKey, action, checked) {
  if (!editableMatrix.value[moduleKey]) editableMatrix.value[moduleKey] = {}
  editableMatrix.value[moduleKey][action] = checked ? [...matrixEditableRoles] : []
}

function resetForm() {
  form.username = ''
  form.role = 'marketing'
  form.password = ''
  form.is_active = true
}

async function loadMatrix() {
  const pm = await getPermissionMatrix().catch(() => null)
  editableMatrix.value = normalizeLoadedMatrix(pm?.matrix)
  matrixSavedSnapshot.value = JSON.stringify(sanitizeMatrixForSave(editableMatrix.value))
}

async function load() {
  loading.value = true
  try {
    rows.value = await listUsers()
    await loadMatrix()
  } catch (e) {
    ElMessage.error(parseErrorMessage(e))
  } finally {
    loading.value = false
  }
}

async function saveMatrix() {
  savingMatrix.value = true
  try {
    const payload = sanitizeMatrixForSave(editableMatrix.value)
    await savePermissionMatrix(payload)
    const pm = await getPermissionMatrix().catch(() => null)
    if (pm?.matrix) {
      editableMatrix.value = normalizeLoadedMatrix(pm.matrix)
      setRuntimePermissionMatrix(pm.matrix)
      matrixSavedSnapshot.value = JSON.stringify(sanitizeMatrixForSave(editableMatrix.value))
    } else {
      setRuntimePermissionMatrix(payload)
      matrixSavedSnapshot.value = JSON.stringify(payload)
    }
    ElMessage.success(t('pages.userAccess.matrixSaved'))
  } catch (e) {
    ElMessage.error(parseErrorMessage(e))
  } finally {
    savingMatrix.value = false
  }
}

function resetMatrix() {
  editableMatrix.value = normalizeLoadedMatrix(JSON.parse(matrixSavedSnapshot.value || '{}'))
}

function openCreate() {
  isEdit.value = false
  editingId.value = null
  resetForm()
  dialogVisible.value = true
}

function openEdit(row) {
  isEdit.value = true
  editingId.value = row.id
  form.username = row.username
  form.role = row.role
  form.password = ''
  form.is_active = !!row.is_active
  dialogVisible.value = true
}

async function toggleUserActive(row, active) {
  if (!canUpdate.value) return
  row._toggling = true
  try {
    await updateUser(row.id, { is_active: !!active })
    row.is_active = !!active
    ElMessage.success(t('pages.userAccess.userSaved'))
  } catch (e) {
    ElMessage.error(parseErrorMessage(e))
  } finally {
    row._toggling = false
  }
}

async function submit() {
  const valid = await formRef.value?.validate?.().catch(() => false)
  if (valid === false) return
  if (!isEdit.value && !form.password?.trim()) {
    ElMessage.warning(t('pages.userAccess.rulePassword'))
    return
  }

  saving.value = true
  try {
    if (isEdit.value && editingId.value) {
      const body = { role: form.role, is_active: form.is_active }
      if (form.password?.trim()) body.password = form.password.trim()
      await updateUser(editingId.value, body)
    } else {
      await createUser({
        username: form.username.trim(),
        role: form.role,
        password: form.password,
        is_active: form.is_active,
      })
    }
    dialogVisible.value = false
    await load()
    ElMessage.success(t('pages.userAccess.userSaved'))
  } catch (e) {
    ElMessage.error(parseErrorMessage(e))
  } finally {
    saving.value = false
  }
}

onMounted(load)
</script>

<style scoped>
.user-access-tabs :deep(.el-tabs__header) {
  margin-bottom: 1rem;
}

.user-access-hint {
  color: #64748b;
  cursor: help;
  flex-shrink: 0;
}

.user-access-hint--inline {
  margin-left: 4px;
  vertical-align: middle;
}

.user-access-inner-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
}

.user-access-stats {
  margin: 0 1rem 1rem;
}

.user-access-filter-panel {
  margin: 0 1rem 0.75rem;
}

.user-access-filter-role {
  width: 100%;
  max-width: 280px;
}

.user-access-matrix-filters {
  display: grid;
  grid-template-columns: 1fr;
  gap: 0.75rem;
}

@media (min-width: 640px) {
  .user-access-matrix-filters {
    grid-template-columns: 1fr 200px;
  }
}

.user-access-matrix-wrap {
  margin: 0 1rem 1rem;
  overflow: auto;
  max-height: 58vh;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  background: #fff;
}

.matrix-table th,
.matrix-table td {
  border: 1px solid #e2e8f0;
  padding: 8px 10px;
  white-space: nowrap;
}

.matrix-table thead th {
  position: sticky;
  top: 0;
  background: #f8fafc;
  z-index: 3;
  font-weight: 600;
  font-size: 12px;
}

.sticky-col {
  position: sticky;
  left: 0;
  background: #fff;
  z-index: 2;
  min-width: 160px;
}

.sticky-col-2 {
  position: sticky;
  left: 160px;
  background: #fff;
  z-index: 2;
  min-width: 120px;
}

.matrix-admin-col {
  background: #f8fafc;
}

.user-access-dialog-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
  padding: 0 4px 12px;
  border-bottom: 1px solid #e2e8f0;
  margin-bottom: 16px;
}

.user-access-dialog-header__title {
  margin: 0;
  font-size: 1.05rem;
  font-weight: 600;
  color: #0f172a;
}

.user-access-dialog-header__sub {
  margin: 4px 0 0;
  font-size: 0.8rem;
  color: #64748b;
}

.user-access-dialog-panel {
  padding: 0 4px;
}
</style>
