<template>
  <AdminSection :title="t('pages.customerPrices.title')" :subtitle="t('pages.customerPrices.subtitle')">
    <template #actions>
      <el-select v-model="filterCustomerId" :placeholder="t('common.allCustomer')" clearable filterable class="w-48" @change="load">
        <el-option v-for="c in customers" :key="c.id" :label="c.name || c.code" :value="c.id" />
      </el-select>
      <el-input v-model="keyword" :placeholder="t('pages.customerPrices.searchPlaceholder')" clearable class="w-64" />
      <el-button v-if="canCreate" type="primary" :icon="Plus" @click="openCreate">{{ t('common.create') }}</el-button>
    </template>

    <el-table :data="filteredRows" @sort-change="onSortChange" v-loading="loading" border stripe size="small" class="admin-table" table-layout="fixed" :empty-text="t('pages.customerPrices.tableEmpty')">
      <el-table-column type="index" :label="t('common.noLabel')" width="56" align="center" :index="(i) => (page - 1) * pageSize + i + 1" />
      <el-table-column prop="customer" :label="t('pages.customerPrices.customerName')" width="180">
        <template #default="{ row }">
          <span v-if="row.customer">{{ row.customer.name || row.customer.code }}</span>
          <span v-else>—</span>
        </template>
      </el-table-column>
      <el-table-column prop="buyer_code" sortable="custom" :label="t('pages.customerPrices.buyerCode')" width="120" />
      <el-table-column prop="material_pattern" :label="t('pages.customerPrices.materialPattern')" min-width="160" />
      <el-table-column prop="price_override" :label="t('pages.customerPrices.priceOverride')" width="130" align="right">
        <template #default="{ row }">
          {{ row.price_override != null ? row.price_override : '—' }}
        </template>
      </el-table-column>
      <el-table-column prop="discount_percentage" :label="t('pages.customerPrices.discountPercentage')" width="120" align="right">
        <template #default="{ row }">
          {{ row.discount_percentage != null ? row.discount_percentage + '%' : '—' }}
        </template>
      </el-table-column>
      <el-table-column prop="valid_from" :label="t('pages.customerPrices.validFrom')" width="110">
        <template #default="{ row }">
          {{ row.valid_from || '—' }}
        </template>
      </el-table-column>
      <el-table-column prop="valid_to" :label="t('pages.customerPrices.validTo')" width="110">
        <template #default="{ row }">
          {{ row.valid_to || '—' }}
        </template>
      </el-table-column>
      <el-table-column :label="t('common.actions')" width="88" align="center">
        <template #default="{ row }">
          <AdminTableActions
            :show-edit="canUpdate"
            :show-delete="canDelete"
            @edit="openEdit(row)"
            @delete="confirmDelete(row)"
          />
        </template>
      </el-table-column>
    </el-table>
    <div class="flex justify-end mt-3">
      <el-pagination
        v-model:current-page="page"
        v-model:page-size="pageSize"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next"
        :total="totalRows"
        background
      />
    </div>

    <el-dialog v-model="formVisible" :title="isEdit ? t('common.edit') : t('common.create')" width="600px" destroy-on-close align-center>
      <el-form :model="form" label-position="top">
        <el-row :gutter="16">
          <el-col :xs="24" :md="12">
            <el-form-item :label="t('pages.customerPrices.customerName')" required>
              <el-select v-model="form.customer_id" filterable class="w-full">
                <el-option v-for="c in customers" :key="c.id" :label="c.name || c.code" :value="c.id" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :xs="24" :md="12">
            <el-form-item :label="t('pages.customerPrices.buyerCode')" required>
              <el-input v-model="form.buyer_code" />
            </el-form-item>
          </el-col>
          <el-col :span="24">
            <el-form-item :label="t('pages.customerPrices.materialPattern')">
              <el-input v-model="form.material_pattern" placeholder="*PU* atau exact match" />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :md="12">
            <el-form-item :label="t('pages.customerPrices.priceOverride')">
              <el-input-number v-model="form.price_override" :min="0" :precision="4" class="w-full" placeholder="0" />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :md="12">
            <el-form-item :label="t('pages.customerPrices.discountPercentage')">
              <el-input-number v-model="form.discount_percentage" :min="0" :max="100" :precision="2" class="w-full" placeholder="0" />
            </el-form-item>
          </el-col>
          <el-col :span="24">
            <el-form-item :label="t('pages.customerPrices.validPeriod')">
              <el-date-picker
                v-model="form.valid_range"
                type="daterange"
                :range-separator="t('common.rangeSeparator')"
                :start-placeholder="t('common.startDate')"
                :end-placeholder="t('common.endDate')"
                value-format="YYYY-MM-DD"
                class="w-full"
              />
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <template #footer>
        <el-button :icon="Close" @click="formVisible = false">{{ t('common.cancel') }}</el-button>
        <el-button v-if="canCreate || canUpdate" type="primary" @click="submitForm">{{ t('common.save') }}</el-button>
      </template>
    </el-dialog>
  </AdminSection>
</template>

<script setup>
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { Plus, Close } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import AdminSection from '../../components/AdminSection.vue'
import AdminTableActions from '../../components/admin/AdminTableActions.vue'
import { listCustomerPrices, createCustomerPrice, updateCustomerPrice, deleteCustomerPrice, listCustomers } from '../../api/client'
import { useModulePermission } from '../../composables/useModulePermission'
import { buildPageParams, fromElSortChange, normalizePageResult } from '../../utils/tableQuery'

const { t } = useI18n()
const { canCreate, canUpdate, canDelete } = useModulePermission('customerPrices')

const loading = ref(false)
const rows = ref([])
const page = ref(1)
const pageSize = ref(20)
const totalRows = ref(0)
const sortBy = ref(null)
const sortDir = ref('desc')
const customers = ref([])
const keyword = ref('')
const filterCustomerId = ref(null)
const formVisible = ref(false)
const isEdit = ref(false)
const editingId = ref(null)

const form = reactive({
  customer_id: null,
  buyer_code: '',
  material_pattern: '',
  price_override: null,
  discount_percentage: null,
  valid_range: [],
})

const filteredRows = computed(() => {
  if (!keyword.value) return rows.value
  const q = keyword.value.toLowerCase()
  return rows.value.filter(r => 
    r.buyer_code?.toLowerCase().includes(q) ||
    r.material_pattern?.toLowerCase().includes(q) ||
    r.customer?.name?.toLowerCase().includes(q) ||
    r.customer?.code?.toLowerCase().includes(q)
  )
})


async function loadCustomers() {
  try {
    customers.value = await listCustomers()
  } catch (e) {
    console.error('Failed to load customers', e)
  }
}

async function load() {
  loading.value = true
  try {
    const params = buildPageParams({
      page: page.value,
      pageSize: pageSize.value,
      sortBy: sortBy.value,
      sortDir: sortDir.value,
      extra: {
        customer_id: filterCustomerId.value || undefined,
      },
    })
    const raw = await listCustomerPrices(params)
    const pageData = normalizePageResult(raw, { page: page.value, pageSize: pageSize.value })
    rows.value = pageData.items
    totalRows.value = pageData.total
  } finally {
    loading.value = false
  }
}

function onSortChange(payload) {
  const mapped = fromElSortChange(payload)
  sortBy.value = mapped.sortBy
  sortDir.value = mapped.sortDir
  page.value = 1
  load()
}

watch(filterCustomerId, () => { page.value = 1; load() })
watch([page, pageSize], () => load())

function resetForm() {
  Object.assign(form, {
    customer_id: null,
    buyer_code: '',
    material_pattern: '',
    price_override: null,
    discount_percentage: null,
    valid_range: [],
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
  Object.assign(form, {
    customer_id: row.customer_id,
    buyer_code: row.buyer_code || '',
    material_pattern: row.material_pattern || '',
    price_override: row.price_override,
    discount_percentage: row.discount_percentage,
    valid_range: row.valid_from && row.valid_to ? [row.valid_from, row.valid_to] : [],
  })
  formVisible.value = true
}

async function submitForm() {
  try {
    const payload = {
      ...form,
      valid_from: form.valid_range?.[0] || null,
      valid_to: form.valid_range?.[1] || null,
    }
    delete payload.valid_range
    if (isEdit.value) {
      await updateCustomerPrice(editingId.value, payload)
    } else {
      await createCustomerPrice(payload)
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
    await ElMessageBox.confirm(t('pages.customerPrices.deleteConfirm'), t('common.confirm'), { type: 'warning' })
    await deleteCustomerPrice(row.id)
    ElMessage.success(t('common.deleteSuccess'))
    await load()
  } catch (e) {
    if (e !== 'cancel') ElMessage.error(e.message || t('common.errorGeneric'))
  }
}

onMounted(() => {
  loadCustomers()
  load()
})
</script>
