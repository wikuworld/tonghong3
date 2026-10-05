<template>
  <AdminSection :title="t('pages.mrpMasterTreatment.title')" :subtitle="t('pages.mrpMasterTreatment.subtitle')">
    <template #actions>
      <el-button :icon="Refresh" :loading="loading" @click="reload">{{ t('common.refresh') }}</el-button>
      <el-button v-if="canCreate" type="primary" :icon="Plus" @click="openCreate">{{ t('common.create') }}</el-button>
    </template>

    <div class="admin-inner-card">
      <el-table :data="rows" v-loading="loading" border stripe size="small" class="admin-table" :empty-text="t('common.tableEmpty')" @sort-change="onSortChange">
        <el-table-column type="index" width="56" :label="t('common.noLabel')" align="center">
          <template #default="{ $index }">{{ (page - 1) * pageSize + $index + 1 }}</template>
        </el-table-column>
        <el-table-column prop="jenis" label="Jenis" width="100" sortable="custom" />
        <el-table-column prop="nama_treatment" :label="t('common.name')" min-width="180" sortable="custom" />
        <el-table-column prop="created_at" :label="t('common.date')" min-width="140" sortable="custom" />
        <el-table-column v-if="canCreate" :label="t('common.actions')" width="112" align="center" fixed="right">
          <template #default="{ row }">
            <AdminTableActions
              :show-edit="true"
              :show-delete="true"
              @edit="openEdit(row)"
              @delete="remove(row)"
            />
          </template>
        </el-table-column>
      </el-table>
      <div class="mt-3 flex justify-end">
        <el-pagination
          v-model:current-page="page"
          v-model:page-size="pageSize"
          :total="total"
          :page-sizes="[20, 50, 100]"
          layout="total, sizes, prev, pager, next"
          background
          small
          @current-change="reload"
          @size-change="() => { page = 1; reload() }"
        />
      </div>
    </div>

    <el-dialog v-model="dialogOpen" :title="editId ? t('common.edit') : t('common.create')" width="420px" destroy-on-close>
      <el-form label-position="top">
        <el-form-item label="Jenis" required>
          <el-select v-model="form.jenis" class="w-full">
            <el-option label="PU" value="PU" />
            <el-option label="Suede" value="Suede" />
          </el-select>
        </el-form-item>
        <el-form-item :label="t('common.name')" required>
          <el-input v-model="form.nama_treatment" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogOpen = false">{{ t('common.cancel') }}</el-button>
        <el-button type="primary" :loading="saving" @click="submit">{{ t('common.save') }}</el-button>
      </template>
    </el-dialog>
  </AdminSection>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Refresh } from '@element-plus/icons-vue'
import AdminSection from '../../../components/AdminSection.vue'
import AdminTableActions from '../../../components/admin/AdminTableActions.vue'
import { can } from '../../../security/permissions'
import {
  mrpCreateTreatment,
  mrpDeleteTreatment,
  mrpListTreatment,
  mrpUpdateTreatment,
} from '../../../api/client'
import { buildPageParams, fromElSortChange, normalizePageResult } from '../../../utils/tableQuery'

const { t } = useI18n()
const loading = ref(false)
const saving = ref(false)
const dialogOpen = ref(false)
const editId = ref(null)
const rows = ref([])
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)
const sortBy = ref('jenis')
const sortDir = ref('asc')
const canCreate = computed(() => can('mrpShopfloor', 'create'))
const form = reactive({ jenis: 'PU', nama_treatment: '' })

async function reload() {
  loading.value = true
  try {
    const data = await mrpListTreatment(
      buildPageParams({
        page: page.value,
        pageSize: pageSize.value,
        sortBy: sortBy.value,
        sortDir: sortDir.value,
      }),
    )
    const pageData = normalizePageResult(data, { page: page.value, pageSize: pageSize.value })
    rows.value = pageData.items
    total.value = pageData.total
  } catch (e) {
    ElMessage.error(e.message || String(e))
  } finally {
    loading.value = false
  }
}

function onSortChange(payload) {
  const mapped = fromElSortChange(payload)
  sortBy.value = mapped.sortBy || 'jenis'
  sortDir.value = mapped.sortDir || 'asc'
  page.value = 1
  reload()
}

function openCreate() {
  editId.value = null
  form.jenis = 'PU'
  form.nama_treatment = ''
  dialogOpen.value = true
}

function openEdit(row) {
  editId.value = row.id
  form.jenis = row.jenis
  form.nama_treatment = row.nama_treatment
  dialogOpen.value = true
}

async function submit() {
  saving.value = true
  try {
    if (editId.value) await mrpUpdateTreatment(editId.value, { ...form })
    else await mrpCreateTreatment({ ...form })
    ElMessage.success(t('common.saved'))
    dialogOpen.value = false
    await reload()
  } catch (e) {
    ElMessage.error(e.message || String(e))
  } finally {
    saving.value = false
  }
}

async function remove(row) {
  try {
    await ElMessageBox.confirm(t('common.confirm'), { type: 'warning' })
    await mrpDeleteTreatment(row.id)
    ElMessage.success(t('common.saved'))
    await reload()
  } catch (e) {
    if (e !== 'cancel') ElMessage.error(e.message || String(e))
  }
}

onMounted(reload)
</script>
