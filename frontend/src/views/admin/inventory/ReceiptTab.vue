<template>
  <AdminSection :title="t('pages.inventory.receiptTitle')" :subtitle="t('pages.inventory.receiptSubtitle')">
    <template #actions>
      <el-button type="primary" :icon="Plus" @click="openCreate">{{ t('pages.inventory.newReceipt') }}</el-button>
    </template>

    <el-table :data="receipts" v-loading="loading" border stripe size="small" class="admin-table" table-layout="fixed" :empty-text="t('common.tableEmpty')">
      <el-table-column prop="receipt_number" :label="t('pages.inventory.receiptNumber')" width="150" />
      <el-table-column prop="receipt_date" :label="t('pages.inventory.date')" width="120" />
      <el-table-column prop="supplier_name" :label="t('pages.inventory.supplier')" min-width="150" />
      <el-table-column prop="warehouse_name" :label="t('pages.inventory.warehouse')" width="120" />
      <el-table-column :label="t('pages.inventory.amount')" width="140" align="right">
        <template #default="{ row }">
          {{ formatCurrency(row.total_amount) }}
        </template>
      </el-table-column>
      <el-table-column :label="t('common.status')" width="100">
        <template #default="{ row }">
          <el-tag :type="row.status === 'confirmed' ? 'success' : 'info'" size="small">
            {{ row.status === 'confirmed' ? t('pages.inventory.confirmed') : 'Draft' }}
          </el-tag>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="formVisible" :title="t('pages.inventory.newReceipt')" width="700px" destroy-on-close align-center>
      <el-form :model="form" label-position="top">
        <el-row :gutter="12">
          <el-col :span="12">
            <el-form-item :label="t('pages.inventory.supplier')">
              <el-input v-model="form.supplier_name" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item :label="t('pages.inventory.date')">
              <el-date-picker v-model="form.receipt_date" type="date" value-format="YYYY-MM-DD" class="w-full" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item :label="t('pages.inventory.warehouse')">
              <el-select v-model="form.warehouse_id" class="w-full">
                <el-option v-for="w in warehouses" :key="w.id" :label="w.name" :value="w.id" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-divider content-position="left">{{ t('pages.inventory.items') }}</el-divider>
        
        <div v-for="(item, idx) in form.details" :key="idx" class="mb-3 p-3 border rounded">
          <el-row :gutter="8">
            <el-col :span="10">
              <el-select v-model="item.material_id" class="w-full" filterable>
                <el-option v-for="m in materials" :key="m.id" :label="`${m.code} - ${m.name}`" :value="m.id" />
              </el-select>
            </el-col>
            <el-col :span="6">
              <el-input-number v-model="item.quantity" class="w-full" />
            </el-col>
            <el-col :span="6">
              <el-input-number v-model="item.unit_cost" class="w-full" />
            </el-col>
            <el-col :span="2">
              <el-button link type="danger" :icon="Delete" @click="removeDetail(idx)" />
            </el-col>
          </el-row>
        </div>
        
        <el-button :icon="Plus" @click="addDetail">{{ t('pages.inventory.addItem') }}</el-button>
      </el-form>
      <template #footer>
        <el-button :icon="Close" @click="formVisible = false">{{ t('common.cancel') }}</el-button>
        <el-button type="primary" :icon="Check" @click="submit">{{ t('common.save') }}</el-button>
      </template>
    </el-dialog>
  </AdminSection>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessage } from 'element-plus'
import { Plus, Close, Check, Delete } from '@element-plus/icons-vue'
import AdminSection from '../../../components/AdminSection.vue'
import { listReceipts, createReceipt, listMaterials, listWarehouses } from '../../../api/client'
import { formatCurrency } from '../../../utils/format'

const { t } = useI18n()
const loading = ref(false)
const receipts = ref([])
const materials = ref([])
const warehouses = ref([])
const formVisible = ref(false)
const form = reactive({
  supplier_name: '',
  receipt_date: new Date().toISOString().split('T')[0],
  warehouse_id: null,
  details: []
})

async function load() {
  loading.value = true
  receipts.value = await listReceipts()
  materials.value = await listMaterials()
  warehouses.value = await listWarehouses()
  loading.value = false
}

function addDetail() {
  form.details.push({ material_id: null, quantity: 1, unit_cost: 0 })
}

function removeDetail(idx) {
  form.details.splice(idx, 1)
}

async function submit() {
  if (!form.warehouse_id) {
    ElMessage.warning('Pilih warehouse')
    return
  }
  try {
    await createReceipt(form)
    formVisible.value = false
    await load()
    ElMessage.success(t('common.saveSuccess'))
  } catch (e) {
    ElMessage.error(e.message)
  }
}

onMounted(load)
</script>