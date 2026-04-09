<template>
  <AdminSection :title="t('pages.userAccess.title')" :subtitle="t('pages.userAccess.subtitle')">
    <template #actions>
      <el-button v-if="activeTab === 'users' && canCreate" type="primary" :icon="Plus" @click="openCreate">{{ t('common.create') }}</el-button>
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

    <el-tabs v-model="activeTab">
      <el-tab-pane :label="t('pages.userAccess.usersTab')" name="users">
        <div class="mb-3 grid grid-cols-1 gap-3 md:grid-cols-2">
          <el-input v-model="userKeyword" clearable :placeholder="`${t('common.search')} username / role`" />
          <el-select v-model="userRoleFilter" clearable :placeholder="t('pages.userAccess.filterRole')">
            <el-option v-for="r in roles" :key="r" :label="r" :value="r" />
          </el-select>
        </div>
        <el-table :data="filteredUsers" v-loading="loading" border stripe size="small" class="admin-table">
          <el-table-column prop="id" :label="t('pages.userAccess.idLabel')" width="72" />
          <el-table-column prop="username" :label="t('pages.login.username')" min-width="180" />
          <el-table-column prop="role" :label="t('pages.userAccess.roleLabel')" width="140" />
          <el-table-column :label="t('common.status')" width="120" align="center">
            <template #default="{ row }">
              <el-tag :type="row.is_active ? 'success' : 'info'">
                {{ row.is_active ? t('status.active') : t('status.inactive') }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column :label="t('common.actions')" width="88" align="center">
            <template #default="{ row }">
              <el-tooltip v-if="canUpdate" :content="t('common.edit')" placement="top">
                <el-button :icon="EditPen" link type="primary" :aria-label="t('common.edit')" @click="openEdit(row)" />
              </el-tooltip>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <el-tab-pane :label="t('pages.userAccess.permissionMatrixTab')" name="matrix">
        <div class="mb-3 grid grid-cols-1 gap-3 md:grid-cols-2">
          <el-input v-model="matrixKeyword" clearable :placeholder="t('pages.userAccess.filterModuleAction')" />
          <el-select v-model="matrixActionFilter" clearable :placeholder="t('pages.userAccess.filterAction')">
            <el-option v-for="a in availableActions" :key="a" :label="a" :value="a" />
          </el-select>
        </div>

        <div class="matrix-scroll rounded border border-slate-200 bg-white">
          <table class="matrix-table">
            <thead>
              <tr>
                <th class="sticky-col">{{ t('pages.userAccess.matrixModule') }}</th>
                <th>{{ t('pages.userAccess.matrixAction') }}</th>
                <th v-for="r in roles" :key="`h-${r}`">{{ r }}</th>
                <th>{{ t('pages.userAccess.matrixBulk') }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="row in filteredMatrixRows" :key="`${row.module}-${row.action}`">
                <td class="sticky-col">{{ row.module }}</td>
                <td>{{ row.action }}</td>
                <td v-for="r in roles" :key="`${row.module}-${row.action}-${r}`" class="text-center">
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
      </el-tab-pane>
    </el-tabs>

    <el-dialog v-model="dialogVisible" :title="isEdit ? t('common.edit') : t('common.create')" width="520px">
      <el-form label-position="top">
        <el-form-item :label="t('pages.login.username')" required>
          <el-input v-model="form.username" :disabled="isEdit" />
        </el-form-item>
        <el-form-item :label="t('pages.userAccess.roleLabel')" required>
          <el-select v-model="form.role" class="w-full">
            <el-option v-for="r in roles" :key="r" :label="r" :value="r" />
          </el-select>
        </el-form-item>
        <el-form-item :label="t('pages.login.password')" :required="!isEdit">
          <el-input v-model="form.password" type="password" show-password :placeholder="isEdit ? t('pages.userAccess.keepPasswordHint') : ''" />
        </el-form-item>
        <el-form-item :label="t('common.status')">
          <el-switch v-model="form.is_active" />
        </el-form-item>
      </el-form>
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
import { CircleCheck, CircleClose, DocumentChecked, EditPen, Plus, RefreshLeft } from '@element-plus/icons-vue'
import AdminSection from '../../components/AdminSection.vue'
import { createUser, getPermissionMatrix, listUsers, savePermissionMatrix, updateUser } from '../../api/client'
import { ACTION_MATRIX, can, setRuntimePermissionMatrix } from '../../security/permissions'

const { t } = useI18n()
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
const roles = ['admin', 'marketing', 'ppic', 'production', 'qc', 'warehouse', 'finance', 'exim', 'sales']
const canCreate = can('userAccess', 'create')
const canUpdate = can('userAccess', 'update')
const matrixRows = computed(() => {
  const out = []
  Object.entries(editableMatrix.value || ACTION_MATRIX).forEach(([module, actions]) => {
    Object.entries(actions).forEach(([action, rs]) => {
      out.push({ module, action, roles: rs.join(', ') })
    })
  })
  return out
})
const editableMatrix = ref({})
const matrixSavedSnapshot = ref('')
const savingMatrix = ref(false)
const availableActions = computed(() => [...new Set(matrixRows.value.map((x) => x.action))].sort())
const filteredMatrixRows = computed(() =>
  matrixRows.value.filter((x) => {
    const k = matrixKeyword.value.trim().toLowerCase()
    const passKeyword = !k || `${x.module} ${x.action}`.toLowerCase().includes(k)
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
const hasMatrixChanges = computed(() => JSON.stringify(editableMatrix.value) !== matrixSavedSnapshot.value)

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
  editableMatrix.value[moduleKey][action] = checked ? [...roles] : []
}

const form = reactive({
  username: '',
  role: 'marketing',
  password: '',
  is_active: true,
})

function resetForm() {
  form.username = ''
  form.role = 'marketing'
  form.password = ''
  form.is_active = true
}

async function load() {
  loading.value = true
  try {
    rows.value = await listUsers()
    const pm = await getPermissionMatrix().catch(() => null)
    editableMatrix.value = pm?.matrix && Object.keys(pm.matrix).length ? pm.matrix : JSON.parse(JSON.stringify(ACTION_MATRIX))
    matrixSavedSnapshot.value = JSON.stringify(editableMatrix.value)
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  } finally {
    loading.value = false
  }
}

async function saveMatrix() {
  savingMatrix.value = true
  try {
    await savePermissionMatrix({ matrix: editableMatrix.value })
    setRuntimePermissionMatrix(editableMatrix.value)
    matrixSavedSnapshot.value = JSON.stringify(editableMatrix.value)
    ElMessage.success(t('pages.userAccess.matrixSaved'))
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  } finally {
    savingMatrix.value = false
  }
}

function resetMatrix() {
  editableMatrix.value = JSON.parse(matrixSavedSnapshot.value || '{}')
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

async function submit() {
  saving.value = true
  try {
    if (isEdit.value && editingId.value) {
      const body = { role: form.role, is_active: form.is_active }
      if (form.password) body.password = form.password
      await updateUser(editingId.value, body)
    } else {
      await createUser({
        username: form.username,
        role: form.role,
        password: form.password,
        is_active: form.is_active,
      })
    }
    dialogVisible.value = false
    await load()
    ElMessage.success(t('common.save'))
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  } finally {
    saving.value = false
  }
}

onMounted(load)
</script>

<style scoped>
.matrix-scroll {
  overflow: auto;
  max-height: 66vh;
}
.matrix-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
}
.matrix-table th,
.matrix-table td {
  border: 1px solid #e2e8f0;
  padding: 8px;
  white-space: nowrap;
}
.matrix-table thead th {
  position: sticky;
  top: 0;
  background: #f8fafc;
  z-index: 2;
}
.sticky-col {
  position: sticky;
  left: 0;
  background: #fff;
  z-index: 1;
}
</style>

