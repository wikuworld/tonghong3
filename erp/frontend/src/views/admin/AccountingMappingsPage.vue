<template>
  <AdminSection :title="t('pages.accountingMappings.title')" :subtitle="t('pages.accountingMappings.subtitle')">
    <template #actions>
      <el-select v-model="filterTransactionType" :placeholder="t('pages.accountingMappings.filterTransactionType')" clearable class="w-48">
        <el-option :label="t('pages.accountingMappings.allTransactionTypes')" value="" />
        <el-option :label="t('pages.accountingMappings.po_created')" value="po_created" />
        <el-option :label="t('pages.accountingMappings.invoice')" value="invoice" />
        <el-option :label="t('pages.accountingMappings.payment')" value="payment" />
      </el-select>
      <el-select v-model="filterStatus" :placeholder="t('pages.accountingMappings.filterStatus')" clearable class="w-40">
        <el-option :label="t('pages.accountingMappings.allStatuses')" value="" />
        <el-option :label="t('pages.accountingMappings.draft')" value="draft" />
        <el-option :label="t('pages.accountingMappings.confirmed')" value="confirmed" />
        <el-option :label="t('pages.accountingMappings.sent')" value="sent" />
        <el-option :label="t('pages.accountingMappings.paid')" value="paid" />
      </el-select>
      <el-button v-if="canCreate" type="primary" :icon="Plus" @click="openCreate">{{ t('common.create') }}</el-button>
    </template>

    <el-table :data="filteredRows" @sort-change="onSortChange" v-loading="loading" border stripe size="small" class="admin-table" table-layout="fixed" :empty-text="t('common.tableEmpty')">
      <el-table-column type="index" :label="t('common.noLabel')" width="56" align="center" :index="(i) => (page - 1) * pageSize + i + 1" />
      <el-table-column prop="transaction_type" sortable="custom" :label="t('pages.accountingMappings.transactionType')" width="140">
        <template #default="{ row }">
          {{ t(`pages.accountingMappings.${row.transaction_type}`) }}
        </template>
      </el-table-column>
      <el-table-column prop="status" :label="t('common.status')" width="120">
        <template #default="{ row }">
          <el-tag v-if="row.status" :type="statusTagType(row.status)" size="small">
            {{ t(`pages.accountingMappings.${row.status}`) }}
          </el-tag>
          <span v-else>—</span>
        </template>
      </el-table-column>
      <el-table-column prop="coa_code" sortable="custom" :label="t('pages.accountingMappings.coaCode')" width="120" />
      <el-table-column prop="coa_name" :label="t('pages.accountingMappings.coaName')" min-width="180" />
      <el-table-column prop="description" :label="t('pages.accountingMappings.description')" min-width="160" show-overflow-tooltip />
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
            <el-form-item :label="t('pages.accountingMappings.transactionType')" required>
              <el-select v-model="form.transaction_type" class="w-full">
                <el-option :label="t('pages.accountingMappings.po_created')" value="po_created" />
                <el-option :label="t('pages.accountingMappings.invoice')" value="invoice" />
                <el-option :label="t('pages.accountingMappings.payment')" value="payment" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :xs="24" :md="12">
            <el-form-item :label="t('common.status')">
              <el-select v-model="form.status" class="w-full" clearable>
                <el-option :label="t('pages.accountingMappings.draft')" value="draft" />
                <el-option :label="t('pages.accountingMappings.confirmed')" value="confirmed" />
                <el-option :label="t('pages.accountingMappings.sent')" value="sent" />
                <el-option :label="t('pages.accountingMappings.paid')" value="paid" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :xs="24" :md="12">
            <el-form-item :label="t('pages.accountingMappings.coaCode')" required>
              <el-input v-model="form.coa_code" placeholder="e.g. 1-1100" />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :md="12">
            <el-form-item :label="t('pages.accountingMappings.coaName')" required>
              <el-input v-model="form.coa_name" placeholder="e.g. Account Receivable" />
            </el-form-item>
          </el-col>
          <el-col :span="24">
            <el-form-item :label="t('pages.accountingMappings.description')">
              <el-input v-model="form.description" type="textarea" :rows="2" />
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <template #footer>
        <el-button @click="formVisible = false">{{ t('common.cancel') }}</el-button>
        <el-button v-if="canCreate || canUpdate" type="primary" @click="submitForm">{{ t('common.save') }}</el-button>
      </template>
    </el-dialog>
  </AdminSection>
</template>

<script setup>
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { Plus } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import AdminSection from '../../components/AdminSection.vue'
import AdminTableActions from '../../components/admin/AdminTableActions.vue'
import { listAccountingMappings, createAccountingMapping, updateAccountingMapping, deleteAccountingMapping } from '../../api/client'
import { useModulePermission } from '../../composables/useModulePermission'
import { buildPageParams, fromElSortChange, normalizePageResult } from '../../utils/tableQuery'

const { t } = useI18n()
const { canCreate, canUpdate, canDelete } = useModulePermission('accountingMappings')

const loading = ref(false)
const rows = ref([])
const page = ref(1)
const pageSize = ref(20)
const totalRows = ref(0)
const sortBy = ref(null)
const sortDir = ref('desc')
const filterTransactionType = ref('')
const filterStatus = ref('')
const formVisible = ref(false)
const isEdit = ref(false)
const editingId = ref(null)

const form = reactive({
  transaction_type: 'po_created',
  status: null,
  coa_code: '',
  coa_name: '',
  description: '',
})

const filteredRows = computed(() => rows.value)

function statusTagType(status) {
  const map = {
    draft: 'info',
    confirmed: 'warning',
    sent: 'primary',
    paid: 'success',
  }
  return map[status] || 'info'
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
        transaction_type: filterTransactionType.value || undefined,
        status: filterStatus.value || undefined,
      },
    })
    const raw = await listAccountingMappings(params)
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

watch([filterTransactionType, filterStatus], () => { page.value = 1; load() })
watch([page, pageSize], () => load())

function resetForm() {
  Object.assign(form, {
    transaction_type: 'po_created',
    status: null,
    coa_code: '',
    coa_name: '',
    description: '',
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
    transaction_type: row.transaction_type,
    status: row.status,
    coa_code: row.coa_code,
    coa_name: row.coa_name,
    description: row.description || '',
  })
  formVisible.value = true
}

async function submitForm() {
  try {
    if (isEdit.value) {
      await updateAccountingMapping(editingId.value, form)
    } else {
      await createAccountingMapping(form)
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
    await ElMessageBox.confirm(t('pages.accountingMappings.deleteConfirm'), t('common.confirm'), { type: 'warning' })
    await deleteAccountingMapping(row.id)
    ElMessage.success(t('common.deleteSuccess'))
    await load()
  } catch (e) {
    if (e !== 'cancel') ElMessage.error(e.message || t('common.errorGeneric'))
  }
}

onMounted(load)
</script>
