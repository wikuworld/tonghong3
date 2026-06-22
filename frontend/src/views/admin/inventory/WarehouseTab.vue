<template>
  <AdminSection :title="t('pages.inventory.warehouseTitle')" :subtitle="t('pages.inventory.warehouseSubtitle')">
    <template #actions>
      <el-button v-if="canCreate" type="primary" :icon="Plus" @click="openCreate">{{ t('common.create') }}</el-button>
    </template>

    <el-table :data="warehouses" v-loading="loading" border stripe size="small" class="admin-table" table-layout="fixed" :empty-text="t('common.tableEmpty')">
      <el-table-column prop="code" :label="t('common.code')" width="120" />
      <el-table-column prop="name" :label="t('common.name')" min-width="180" />
      <el-table-column prop="location" :label="t('pages.inventory.location')" />
      <el-table-column :label="t('common.status')" width="100">
        <template #default="{ row }">
          <el-tag :type="row.is_active ? 'success' : 'info'" size="small">
            {{ row.is_active ? t('common.active') : t('common.inactive') }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column :label="t('common.actions')" width="150" align="center">
        <template #default="{ row }">
          <el-button v-if="canUpdate" link type="primary" :icon="EditPen" @click="openEdit(row)">{{ t('common.edit') }}</el-button>
        </template>
      </el-table-column>
    </el-table>

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
import { Plus, Close, Check, EditPen } from '@element-plus/icons-vue'
import AdminSection from '../../../components/AdminSection.vue'
import { listWarehouses, createWarehouse, updateWarehouse } from '../../../api/client'
import { useModulePermission } from '../../../composables/useModulePermission'

const { t } = useI18n()
const { canCreate, canUpdate } = useModulePermission('inventory')
const loading = ref(false)
const warehouses = ref([])
const formVisible = ref(false)
const isEdit = ref(false)
const form = reactive({ code: '', name: '', location: '' })

async function load() {
  loading.value = true
  warehouses.value = await listWarehouses()
  loading.value = false
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