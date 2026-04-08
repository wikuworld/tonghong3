<template>
  <AdminSection :title="t('pages.production.title')" :subtitle="t('pages.production.subtitle')">
    <template #actions>
      <el-input
        v-model="keyword"
        :placeholder="t('pages.production.searchPlaceholder')"
        clearable
        class="production-toolbar-search"
      />
      <el-button v-if="canManage" type="primary" :icon="Plus" :loading="loading" @click="openCreate">{{ t('common.create') }}</el-button>
    </template>

    <div class="filter-panel mb-4">
      <p class="filter-panel__title">{{ t('common.filter') }}</p>
      <el-form class="filter-form" label-position="top">
        <el-row :gutter="12">
          <el-col :xs="24" :sm="12" :md="8" :lg="6">
            <el-form-item :label="t('common.status')">
              <el-select v-model="filterStatus" clearable class="w-full" :placeholder="t('common.status')">
                <el-option :label="t('status.planned')" value="planned" />
                <el-option :label="t('status.in_progress')" value="in_progress" />
                <el-option :label="t('status.done')" value="done" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :xs="24" :sm="12" :md="8" :lg="6">
            <el-form-item label="&nbsp;">
              <el-button class="w-full" @click="resetFilter">{{ t('common.reset') }}</el-button>
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
    </div>

    <el-table
      :data="filteredRows"
      v-loading="loading"
      border
      stripe
      size="small"
      class="admin-table"
      table-layout="auto"
      :empty-text="t('pages.production.tableEmpty')"
    >
      <el-table-column type="index" :label="t('common.noLabel')" width="56" align="center" />
      <el-table-column prop="production_number" :label="t('common.productionNo')" min-width="140" show-overflow-tooltip />
      <el-table-column prop="po_number_disp" :label="t('common.poNo')" min-width="140" show-overflow-tooltip />
      <el-table-column prop="customer_name" :label="t('common.customer')" min-width="160" show-overflow-tooltip />
      <el-table-column prop="buyer_disp" :label="t('common.buyer')" min-width="110" show-overflow-tooltip />
      <el-table-column prop="etd_disp" :label="t('common.etd')" min-width="110" align="center" />
      <el-table-column prop="start_date" :label="t('common.startDate')" min-width="110" align="center" />
      <el-table-column prop="end_date" :label="t('common.endDate')" min-width="110" align="center" />
      <el-table-column prop="created_at_disp" :label="t('pages.production.fieldCreatedAt')" min-width="150" align="center" />
      <el-table-column prop="status" :label="t('common.status')" min-width="110" align="center">
        <template #default="{ row }">
          <el-tag :type="statusTagType(row.status)" size="small">{{ productionStatusLabel(row.status) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column :label="t('common.actions')" width="80" align="center" fixed="right">
        <template #default="{ row }">
          <el-tooltip :content="t('common.detail')" placement="top">
            <el-button :icon="View" link type="primary" @click="openDetail(row)" />
          </el-tooltip>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog
      v-model="detailVisible"
      :title="t('pages.production.dialogDetail')"
      width="820px"
      destroy-on-close
      align-center
      class="production-dialog"
      @closed="onDetailClosed"
    >
      <div v-loading="detailLoading" class="min-h-[120px]">
        <template v-if="detailRow">
          <el-divider content-position="left">{{ t('pages.production.sectionPo') }}</el-divider>
          <el-descriptions :column="2" border size="small" class="production-descriptions mb-4">
            <el-descriptions-item :label="t('common.productionNo')" :span="1">
              {{ detailRow.production_number || t('common.emptyValue') }}
            </el-descriptions-item>
            <el-descriptions-item :label="t('pages.production.fieldCreatedAt')" :span="1">
              {{ detailRow.created_at_disp || t('common.emptyValue') }}
            </el-descriptions-item>
            <el-descriptions-item :label="t('common.poNo')" :span="1">
              {{ detailRow.po_number_disp || t('common.emptyValue') }}
            </el-descriptions-item>
            <el-descriptions-item :label="t('pages.production.fieldPoStatus')" :span="1">
              <el-tag v-if="detailRow.po_status" size="small" type="info">{{ poStatusLabel(detailRow.po_status) }}</el-tag>
              <span v-else>{{ t('common.emptyValue') }}</span>
            </el-descriptions-item>
            <el-descriptions-item :label="t('common.customer')" :span="1">
              {{ detailRow.customer_name || t('common.emptyValue') }}
            </el-descriptions-item>
            <el-descriptions-item :label="t('common.buyer')" :span="1">
              {{ detailRow.buyer_disp || t('common.emptyValue') }}
            </el-descriptions-item>
            <el-descriptions-item :label="t('common.etd')" :span="1">{{ detailRow.etd_disp || t('common.emptyValue') }}</el-descriptions-item>
            <el-descriptions-item :label="t('common.orderDate')" :span="1">{{ detailRow.order_date_disp || t('common.emptyValue') }}</el-descriptions-item>
            <el-descriptions-item :label="t('common.startDate')" :span="1">{{ detailRow.start_date || t('common.emptyValue') }}</el-descriptions-item>
            <el-descriptions-item :label="t('common.endDate')" :span="1">{{ detailRow.end_date || t('common.emptyValue') }}</el-descriptions-item>
            <el-descriptions-item :label="t('common.status')" :span="2">
              <el-tag :type="statusTagType(detailRow.status)" size="small">{{ productionStatusLabel(detailRow.status) }}</el-tag>
            </el-descriptions-item>
          </el-descriptions>

          <el-divider content-position="left">{{ t('pages.production.sectionLines') }}</el-divider>
          <el-table
            v-if="detailLines.length"
            :data="detailLines"
            border
            stripe
            size="small"
            max-height="320"
            class="admin-table"
          >
            <el-table-column prop="po_detail_id" :label="t('pages.production.poDetailRef')" width="110" align="center" />
            <el-table-column prop="qty_planned" :label="t('pages.production.qtyPlanned')" width="110" align="right">
              <template #default="{ row }">{{ formatQty(row.qty_planned) }}</template>
            </el-table-column>
            <el-table-column prop="qty_actual" :label="t('pages.production.qtyActual')" width="110" align="right">
              <template #default="{ row }">{{ formatQty(row.qty_actual) }}</template>
            </el-table-column>
            <el-table-column prop="lot_number" :label="t('pages.production.lotNumber')" min-width="120" show-overflow-tooltip />
            <el-table-column prop="batch_number" :label="t('pages.production.batchNumber')" min-width="120" show-overflow-tooltip />
            <el-table-column prop="status" :label="t('pages.production.lineStatus')" width="110" align="center">
              <template #default="{ row }">
                <el-tag size="small">{{ lineStatusLabel(row.status) }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="is_over_production" :label="t('pages.production.overProduction')" width="100" align="center">
              <template #default="{ row }">
                {{ row.is_over_production ? t('common.yes') : t('common.no') }}
              </template>
            </el-table-column>
          </el-table>
          <p v-else class="text-sm text-slate-500">{{ t('pages.production.linesEmpty') }}</p>
        </template>
      </div>
      <template #footer>
        <el-button type="primary" @click="detailVisible = false">{{ t('pages.production.closeDetail') }}</el-button>
      </template>
    </el-dialog>

    <el-dialog
      v-model="formVisible"
      :title="t('pages.production.dialogAdd')"
      width="600px"
      destroy-on-close
      align-center
      class="production-dialog"
      @closed="resetFormModel"
    >
      <el-alert class="mb-3" type="info" :closable="false" :title="t('pages.production.formHint')" />
      <el-form ref="formRef" :model="formModel" :rules="formRules" label-position="top" class="production-form" @submit.prevent>
        <el-form-item :label="t('common.poNo')" prop="po_id" required>
          <el-select v-model="formModel.po_id" filterable class="w-full" :placeholder="t('common.placeholder.poNumber')">
            <el-option v-for="p in posEligible" :key="p.id" :label="poOptionLabel(p)" :value="p.id" />
          </el-select>
        </el-form-item>
        <el-form-item :label="t('common.productionNo')">
          <el-input v-model="formModel.production_number" maxlength="100" clearable :placeholder="t('pages.production.placeholderProdNo')" />
        </el-form-item>
        <el-row :gutter="12">
          <el-col :span="12">
            <el-form-item :label="t('common.startDate')" prop="start_date">
              <el-date-picker v-model="formModel.start_date" type="date" class="w-full" value-format="YYYY-MM-DD" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item :label="t('common.endDate')" prop="end_date">
              <el-date-picker v-model="formModel.end_date" type="date" class="w-full" value-format="YYYY-MM-DD" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item :label="t('common.status')" prop="status">
          <el-select v-model="formModel.status" class="w-full">
            <el-option :label="t('status.planned')" value="planned" />
            <el-option :label="t('status.in_progress')" value="in_progress" />
            <el-option :label="t('status.done')" value="done" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="production-dialog-footer">
          <el-button @click="formVisible = false">{{ t('common.cancel') }}</el-button>
          <el-button v-if="canManage" type="primary" :loading="formSubmitting" @click="submitForm">{{ t('common.save') }}</el-button>
        </div>
      </template>
    </el-dialog>
  </AdminSection>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Plus, View } from '@element-plus/icons-vue'
import AdminSection from '../../components/AdminSection.vue'
import { canWrite } from '../../security/permissions'
import {
  createProduction,
  getProduction,
  listPo,
  listProduction,
  listProductionDetails,
  toIsoDate,
} from '../../api/client'

const { t, te } = useI18n()
const route = useRoute()
const canManage = canWrite('production')

const loading = ref(false)
const keyword = ref('')
const filterStatus = ref('')
const rows = ref([])
const poList = ref([])

const poById = computed(() => {
  const m = {}
  for (const p of poList.value) m[p.id] = p
  return m
})

const posEligible = computed(() =>
  poList.value.filter((p) => ['confirmed', 'production', 'completed'].includes(p.status)),
)

function poOptionLabel(p) {
  const cust = p.customer_name_snapshot || p.customer_code || t('common.emptyValue')
  const buyer = p.buyer || t('common.emptyValue')
  const st = p.status && te(`status.${p.status}`) ? t(`status.${p.status}`) : p.status || t('common.emptyValue')
  return `${p.po_number} · ${cust} · ${buyer} (${st})`
}

function sliceDate(v) {
  if (v == null || v === '') return ''
  return String(v).slice(0, 10)
}

function formatCreatedAt(v) {
  if (v == null || v === '') return t('common.emptyValue')
  const s = String(v).replace('T', ' ')
  return s.length > 19 ? s.slice(0, 19) : s
}

function enrichProduction(r) {
  const po = r.po_id ? poById.value[r.po_id] : null
  return {
    ...r,
    po_number_disp: po?.po_number || (r.po_id ? `PO #${r.po_id}` : t('common.emptyValue')),
    customer_name: po?.customer_name_snapshot || po?.customer_code || t('common.emptyValue'),
    buyer_disp: po?.buyer || t('common.emptyValue'),
    etd_disp: sliceDate(po?.etd) || t('common.emptyValue'),
    order_date_disp: sliceDate(po?.order_date) || t('common.emptyValue'),
    po_status: po?.status || null,
    start_date: sliceDate(r.start_date),
    end_date: sliceDate(r.end_date),
    created_at_disp: formatCreatedAt(r.created_at),
  }
}

function productionStatusLabel(status) {
  if (status && te(`status.${status}`)) return t(`status.${status}`)
  return status || t('common.emptyValue')
}

function poStatusLabel(status) {
  if (status && te(`status.${status}`)) return t(`status.${status}`)
  return status || t('common.emptyValue')
}

function lineStatusLabel(status) {
  if (status && te(`status.${status}`)) return t(`status.${status}`)
  return status || t('common.emptyValue')
}

function formatQty(v) {
  if (v == null || v === '') return t('common.emptyValue')
  const n = Number(v)
  return Number.isFinite(n) ? String(n) : String(v)
}

async function load() {
  loading.value = true
  try {
    const [pr, po] = await Promise.all([listProduction(), listPo()])
    poList.value = po
    rows.value = pr.map((r) => enrichProduction(r))
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  await load()
  const productionIdRaw = route.query.production_id
  const productionId = Number(productionIdRaw)
  if (!Number.isNaN(productionId) && productionId > 0) {
    const target = rows.value.find((r) => Number(r.id) === productionId)
    if (target) await openDetail(target)
  }
})

const filteredRows = computed(() => {
  return rows.value.filter((row) => {
    const statusMatch = !filterStatus.value || row.status === filterStatus.value
    const q = keyword.value.trim().toLowerCase()
    const keywordMatch =
      !q ||
      [row.production_number, row.po_number_disp, row.customer_name, row.buyer_disp]
        .filter(Boolean)
        .join(' ')
        .toLowerCase()
        .includes(q)
    return statusMatch && keywordMatch
  })
})

function statusTagType(status) {
  if (status === 'in_progress') return 'warning'
  if (status === 'done') return 'success'
  return 'info'
}

const resetFilter = () => {
  filterStatus.value = ''
  keyword.value = ''
}

const detailVisible = ref(false)
const detailLoading = ref(false)
const detailRow = ref(null)
const detailLines = ref([])

function onDetailClosed() {
  detailRow.value = null
  detailLines.value = []
}

async function openDetail(row) {
  detailVisible.value = true
  detailLoading.value = true
  detailRow.value = null
  detailLines.value = []
  try {
    const full = await getProduction(row.id)
    detailRow.value = enrichProduction(full)
    detailLines.value = await listProductionDetails(row.id)
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
    detailVisible.value = false
  } finally {
    detailLoading.value = false
  }
}

const formVisible = ref(false)
const formRef = ref(null)
const formSubmitting = ref(false)

const formModel = reactive({
  po_id: null,
  production_number: '',
  start_date: '',
  end_date: '',
  status: 'planned',
})

const formRules = computed(() => ({
  po_id: [{ required: true, message: t('pages.production.rulePoNo'), trigger: 'change' }],
}))

function resetFormModel() {
  formModel.po_id = null
  formModel.production_number = ''
  formModel.start_date = ''
  formModel.end_date = ''
  formModel.status = 'planned'
  formRef.value?.clearValidate?.()
}

function openCreate() {
  resetFormModel()
  formVisible.value = true
}

async function submitForm() {
  if (!formRef.value) return
  try {
    await formRef.value.validate()
  } catch {
    return
  }
  formSubmitting.value = true
  try {
    await createProduction({
      po_id: formModel.po_id,
      production_number: formModel.production_number?.trim() || undefined,
      start_date: toIsoDate(formModel.start_date) || undefined,
      end_date: toIsoDate(formModel.end_date) || undefined,
      status: formModel.status,
    })
    ElMessage.success(t('pages.production.saved'))
    formVisible.value = false
    await load()
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  } finally {
    formSubmitting.value = false
  }
}
</script>

<style scoped>
.admin-table {
  width: 100%;
}

.production-form :deep(.el-form-item) {
  margin-bottom: 16px;
}

.production-descriptions :deep(.el-descriptions__label) {
  width: 140px;
  font-weight: 600;
  color: #475569;
}

.production-dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}

.w-full {
  width: 100%;
}

.production-toolbar-search {
  width: 240px;
  max-width: 100%;
  margin-right: 8px;
  vertical-align: middle;
}
</style>
