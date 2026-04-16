<template>
  <AdminSection :title="t('pages.specialPrices.title')" :subtitle="t('pages.specialPrices.subtitle')">
    <template #actions>
      <el-input v-model="keyword" :placeholder="t('pages.specialPrices.searchPlaceholder')" clearable class="w-64" />
      <el-button type="primary" :icon="Plus" @click="openCreate">{{ t('common.create') }}</el-button>
    </template>

    <el-table :data="filteredRows" v-loading="loading" border stripe size="small" class="admin-table" table-layout="fixed" :empty-text="t('pages.specialPrices.tableEmpty')">
      <el-table-column type="index" :label="t('common.noLabel')" width="56" align="center" />
      <el-table-column prop="buyer_code" :label="t('pages.specialPrices.buyerCode')" width="120" />
      <el-table-column prop="material_pattern" :label="t('pages.specialPrices.materialPattern')" min-width="160" />
      <el-table-column prop="emboss_pattern" :label="t('pages.specialPrices.embossPattern')" width="140" />
      <el-table-column prop="discount_type" :label="t('pages.specialPrices.discountType')" width="110">
        <template #default="{ row }">
          <el-tag :type="row.discount_type === 'percentage' ? 'primary' : 'success'" size="small">
            {{ t(`pages.specialPrices.${row.discount_type}`) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="discount_value" :label="t('pages.specialPrices.discountValue')" width="120">
        <template #default="{ row }">
          {{ row.discount_value }}{{ row.discount_type === 'percentage' ? '%' : '' }}
        </template>
      </el-table-column>
      <el-table-column :label="t('common.actions')" width="100" align="center">
        <template #default="{ row }">
          <el-button :icon="EditPen" link type="primary" @click="openEdit(row)" />
          <el-button :icon="Delete" link type="danger" @click="confirmDelete(row)" />
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="formVisible" :title="isEdit ? t('common.edit') : t('common.create')" width="600px" destroy-on-close align-center>
      <el-form :model="form" label-position="top">
        <el-row :gutter="16">
          <el-col :xs="24" :md="12">
            <el-form-item :label="t('pages.specialPrices.buyerCode')" required>
              <el-input v-model="form.buyer_code" />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :md="12">
            <el-form-item :label="t('pages.specialPrices.discountType')">
              <el-select v-model="form.discount_type" class="w-full">
                <el-option :label="t('pages.specialPrices.percentage')" value="percentage" />
                <el-option :label="t('pages.specialPrices.nominal')" value="nominal" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :xs="24" :md="12">
            <el-form-item :label="t('pages.specialPrices.discountValue')" required>
              <el-input-number v-model="form.discount_value" :min="0" :precision="4" class="w-full" />
            </el-form-item>
          </el-col>
          <el-col :span="24">
            <el-form-item :label="t('pages.specialPrices.materialPattern')">
              <el-input v-model="form.material_pattern" placeholder="*PU* atau exact match" />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :md="12">
            <el-form-item :label="t('pages.specialPrices.embossPattern')">
              <el-input v-model="form.emboss_pattern" />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :md="12">
            <el-form-item :label="t('pages.specialPrices.colorPattern')">
              <el-input v-model="form.color_pattern" />
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <template #footer>
        <el-button @click="formVisible = false">{{ t('common.cancel') }}</el-button>
        <el-button type="primary" @click="submitForm">{{ t('common.save') }}</el-button>
      </template>
    </el-dialog>
  </AdminSection>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { Plus, EditPen, Delete } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import AdminSection from '../../components/AdminSection.vue'
import { listSpecialPrices, createSpecialPrice, updateSpecialPrice, deleteSpecialPrice } from '../../api/client'

const { t } = useI18n()

const loading = ref(false)
const rows = ref([])
const keyword = ref('')
const formVisible = ref(false)
const isEdit = ref(false)
const editingId = ref(null)

const form = reactive({
  buyer_code: '',
  material_pattern: '',
  emboss_pattern: '',
  color_pattern: '',
  discount_type: 'percentage',
  discount_value: 0,
})

const filteredRows = computed(() => {
  if (!keyword.value) return rows.value
  const q = keyword.value.toLowerCase()
  return rows.value.filter(r => 
    r.buyer_code?.toLowerCase().includes(q) ||
    r.material_pattern?.toLowerCase().includes(q)
  )
})

async function load() {
  loading.value = true
  try {
    rows.value = await listSpecialPrices()
  } finally {
    loading.value = false
  }
}

function resetForm() {
  Object.assign(form, {
    buyer_code: '',
    material_pattern: '',
    emboss_pattern: '',
    color_pattern: '',
    discount_type: 'percentage',
    discount_value: 0,
  })
}

function openCreate() {
  isEdit.value = false
  editingId.value = null
  resetForm()
  formVisible.value = true
}

function openEdit(row) {
  isEdit.value = true
  editingId.value = row.id
  Object.assign(form, { ...row })
  formVisible.value = true
}

async function submitForm() {
  try {
    if (isEdit.value) {
      await updateSpecialPrice(editingId.value, form)
    } else {
      await createSpecialPrice(form)
    }
    ElMessage.success(t('common.save'))
    formVisible.value = false
    await load()
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  }
}

async function confirmDelete(row) {
  try {
    await ElMessageBox.confirm(t('pages.specialPrices.deleteConfirm'), t('common.confirm'), { type: 'warning' })
    await deleteSpecialPrice(row.id)
    ElMessage.success(t('common.deleteSuccess'))
    await load()
  } catch (e) {
    if (e !== 'cancel') ElMessage.error(e.message || t('common.errorGeneric'))
  }
}

onMounted(load)
</script>
