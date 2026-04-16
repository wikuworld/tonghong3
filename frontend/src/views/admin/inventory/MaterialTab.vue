<template>
  <AdminSection :title="t('pages.inventory.materialTitle')" :subtitle="t('pages.inventory.materialSubtitle')">
    <template #actions>
      <el-button type="primary" :icon="Plus" @click="openCreate">{{ t('common.create') }}</el-button>
    </template>

    <el-table :data="materials" v-loading="loading" border stripe size="small" class="admin-table" table-layout="fixed" :empty-text="t('common.tableEmpty')">
      <el-table-column prop="code" :label="t('common.code')" width="120" />
      <el-table-column prop="name" :label="t('common.name')" min-width="180" />
      <el-table-column prop="material_type" :label="t('pages.inventory.type')" width="120" />
      <el-table-column prop="unit" :label="t('pages.inventory.unit')" width="80" />
      <el-table-column :label="t('pages.inventory.cost')" width="120" align="right">
        <template #default="{ row }">
          {{ formatCurrency(row.cost_price) }}
        </template>
      </el-table-column>
      <el-table-column :label="t('common.actions')" width="100" align="center">
        <template #default="{ row }">
          <el-button link type="primary" @click="openEdit(row)">{{ t('common.edit') }}</el-button>
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
        <el-form-item :label="t('pages.inventory.type')">
          <el-select v-model="form.material_type" class="w-full">
            <el-option label="Leather" value="leather" />
            <el-option label="Chemical" value="chemical" />
            <el-option label="Accessory" value="accessory" />
          </el-select>
        </el-form-item>
        <el-form-item :label="t('pages.inventory.unit')">
          <el-input v-model="form.unit" />
        </el-form-item>
        <el-form-item :label="t('pages.inventory.minStock')">
          <el-input-number v-model="form.min_stock" class="w-full" />
        </el-form-item>
        <el-form-item :label="t('pages.inventory.cost')">
          <el-input-number v-model="form.cost_price" class="w-full" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="formVisible = false">{{ t('common.cancel') }}</el-button>
        <el-button type="primary" @click="submit">{{ t('common.save') }}</el-button>
      </template>
    </el-dialog>
  </AdminSection>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessage } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import AdminSection from '../../../components/AdminSection.vue'
import { listMaterials, createMaterial, updateMaterial } from '../../../api/client'
import { formatCurrency } from '../../../utils/format'

const { t } = useI18n()
const loading = ref(false)
const materials = ref([])
const formVisible = ref(false)
const isEdit = ref(false)
const form = reactive({
  code: '', name: '', material_type: 'leather', unit: '', min_stock: null, cost_price: null
})

async function load() {
  loading.value = true
  materials.value = await listMaterials()
  loading.value = false
}

function openCreate() {
  isEdit.value = false
  Object.assign(form, { code: '', name: '', material_type: 'leather', unit: '', min_stock: null, cost_price: null })
  formVisible.value = true
}

function openEdit(row) {
  isEdit.value = true
  Object.assign(form, { id: row.id, code: row.code, name: row.name, material_type: row.material_type, unit: row.unit, min_stock: row.min_stock, cost_price: row.cost_price })
  formVisible.value = true
}

async function submit() {
  if (!form.code || !form.name) {
    ElMessage.warning(t('common.fillRequired'))
    return
  }
  try {
    if (isEdit.value) {
      await updateMaterial(form.id, form)
    } else {
      await createMaterial(form)
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