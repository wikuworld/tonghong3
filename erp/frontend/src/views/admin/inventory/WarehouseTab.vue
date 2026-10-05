<template>
  <AdminSection :title="t('pages.inventory.warehouseTitle')" :subtitle="t('pages.inventory.warehouseSubtitle')">
    <template #actions>
      <el-button v-if="canCreate" type="primary" :icon="Plus" @click="openCreate">{{ t('common.create') }}</el-button>
    </template>

    <el-table :data="warehouses" @sort-change="onSortChange" v-loading="loading" border stripe size="small" class="admin-table" table-layout="fixed" :empty-text="t('common.tableEmpty')">
      <el-table-column prop="code" :label="t('common.code')" width="120" />
      <el-table-column prop="name" :label="t('common.name')" min-width="180" />
      <el-table-column prop="location" :label="t('pages.inventory.location')" />
      <el-table-column :label="t('common.status')" width="100">
        <template #default="{ row }">
          <el-tag :type="row.is_active ? 'success' : 'info'" size="small">
            {{ row.is_active ? t('status.active') : t('status.inactive') }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column :label="t('common.actions')" width="88" align="center">
        <template #default="{ row }">
          <AdminTableActions :show-edit="canUpdate" @edit="openEdit(row)" />
        </template>
      </el-table-column>
    </el-table>
    <div class="flex justify-end mt-3">
      <el-pagination v-model:current-page="page" v-model:page-size="pageSize" :page-sizes="[10,20,50,100]" layout="total, sizes, prev, pager, next" :total="totalRows" background />
    </div>

    <el-dialog v-model="formVisible" :title="isEdit ? t('common.edit') : t('common.create')" width="600px" destroy-on-close align-center>
      <el-form :model="form" label-position="top">
        <el-form-item :label="t('common.code')" required>
          <el-input v-model="form.code" />
        </el-form-item>
        <el-form-item :label="t('common.name')" required>
          <el-input v-model="form.name" />
        </el-form-item>
        <el-form-item :label="t('pages.inventory.location')">
          <el-input v-model="form.location" type="textarea" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button :icon="Close" @click="formVisible = false">{{ t('common.cancel') }}</el-button>
        <el-button v-if="canCreate || canUpdate" type="primary" :icon="Check" @click="submit">{{ t('common.save') }}</el-button>
      </template>
    </el-dialog>
  </AdminSection>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessage } from 'element-plus'
import { Plus, Close, Check } from '@element-plus/icons-vue'
import AdminSection from '../../../components/AdminSection.vue'
import AdminTableActions from '../../../components/admin/AdminTableActions.vue'
import { listWarehouses, createWarehouse, updateWarehouse } from '../../../api/client'
import { buildPageParams, fromElSortChange, normalizePageResult } from '../../../utils/tableQuery'
import { useModulePermission } from '../../../composables/useModulePermission'

const { t } = useI18n()
const { canCreate, canUpdate } = useModulePermission('inventory')
const loading = ref(false)
const page = ref(1)
const pageSize = ref(20)
const totalRows = ref(0)
const sortBy = ref(null)
const sortDir = ref('asc')
const warehouses = ref([])
const formVisible = ref(false)
const isEdit = ref(false)
const form = reactive({ code: '', name: '', location: '' })

async function load() {
  loading.value = true
  try {
    const raw = await listWarehouses(buildPageParams({ page: page.value, pageSize: pageSize.value, sortBy: sortBy.value, sortDir: sortDir.value }))
    const pageData = normalizePageResult(raw, { page: page.value, pageSize: pageSize.value })
    warehouses.value = pageData.items
    totalRows.value = pageData.total
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  } finally {
    loading.value = false
  }
}

function openCreate() {
  isEdit.value = false
  Object.assign(form, { code: '', name: '', location: '' })
  formVisible.value = true
}

function openEdit(row) {
  isEdit.value = true
  Object.assign(form, { id: row.id, code: row.code, name: row.name, location: row.location })
  formVisible.value = true
}

async function submit() {
  if (!form.code || !form.name) {
    ElMessage.warning(t('common.fillRequired'))
    return
  }
  try {
    if (isEdit.value) {
      await updateWarehouse(form.id, form)
    } else {
      await createWarehouse(form)
    }
    formVisible.value = false
    await load()
    ElMessage.success(t('common.saveSuccess'))
  } catch (e) {
    ElMessage.error(e.message)
  }
}

onMounted(load)
</script>