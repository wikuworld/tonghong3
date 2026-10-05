<template>
  <AdminSection :title="t('pages.brandMaster.title')" :subtitle="t('pages.brandMaster.subtitle')">
    <template #actions>
      <el-input
        v-model="keyword"
        :placeholder="t('pages.brandMaster.searchPlaceholder')"
        clearable
        class="brand-master-toolbar-search"
      />
      <span v-if="loading" class="text-xs text-slate-500">{{ t('common.loadingData') }}</span>
      <el-button :icon="Refresh" :loading="loading" @click="load">{{ t('common.refresh') }}</el-button>
      <el-button v-if="canCreate" type="primary" :icon="Plus" @click="openCreate">{{ t('common.create') }}</el-button>
    </template>

    <div class="admin-inner-card">
      <div class="admin-inner-card__head brand-inner-head">
        <div>
          <h3 class="admin-inner-card__title">{{ t('pages.brandMaster.listSectionTitle') }}</h3>
          <p class="admin-inner-card__sub">{{ t('pages.brandMaster.listSubtitle') }}</p>
        </div>
        <el-tooltip placement="top-start" :show-after="200">
          <template #content>{{ t('pages.brandMaster.pageHint') }}</template>
          <el-icon class="brand-page-hint" :size="16" tabindex="0" :aria-label="t('pages.brandMaster.pageHint')">
            <InfoFilled />
          </el-icon>
        </el-tooltip>
      </div>

      <div class="admin-stats-grid admin-stats-grid--3 brand-master-stats">
        <div class="admin-stat-card">
          <span class="admin-stat-card__value">{{ listStats.total }}</span>
          <span class="admin-stat-card__label">{{ t('pages.brandMaster.statTotal') }}</span>
        </div>
        <div class="admin-stat-card admin-stat-card--info">
          <span class="admin-stat-card__value">{{ listStats.shown }}</span>
          <span class="admin-stat-card__label">{{ t('pages.brandMaster.statShown') }}</span>
        </div>
        <div class="admin-stat-card admin-stat-card--success">
          <span class="admin-stat-card__value">{{ listStats.withCustomer }}</span>
          <span class="admin-stat-card__label">{{ t('pages.brandMaster.statWithCustomer') }}</span>
        </div>
      </div>

      <div class="filter-panel brand-filter-panel">
        <p class="filter-panel__title">{{ t('common.filter') }}</p>
        <div class="brand-filter-row">
          <el-select
            v-model="filterCustomerId"
            clearable
            filterable
            class="brand-filter-customer"
            :placeholder="t('pages.brandMaster.filterCustomer')"
          >
            <el-option :label="t('pages.brandMaster.allCustomer')" value="" />
            <el-option
              v-for="c in customers"
              :key="c.id"
              :label="customerOptionLabel(c)"
              :value="c.id"
            />
          </el-select>
          <div class="brand-filter-toggle">
            <span class="brand-filter-toggle__label">{{ t('pages.brandMaster.groupByCustomer') }}</span>
            <el-tooltip placement="top" :show-after="200">
              <template #content>{{ t('pages.brandMaster.groupByCustomerHint') }}</template>
              <el-icon class="brand-page-hint brand-page-hint--inline" :size="14" tabindex="0" :aria-label="t('pages.brandMaster.groupByCustomerHint')">
                <InfoFilled />
              </el-icon>
            </el-tooltip>
            <el-switch v-model="groupByCustomer" />
          </div>
        </div>
      </div>

      <p class="admin-scroll-hint">{{ t('pages.brandMaster.scrollHint') }}</p>

      <div class="admin-table-scroll brand-master-table-wrap">
        <el-table
          :data="filteredRows"
          v-loading="loading"
          @sort-change="onSortChange"
          border
          stripe
          size="small"
          class="admin-table brand-master-table"
          table-layout="fixed"
          row-key="id"
          :tree-props="{ children: 'children' }"
          :empty-text="t('pages.brandMaster.tableEmpty')"
          :default-expand-all="groupByCustomer"
          max-height="58vh"
        >
          <el-table-column type="index" :label="t('common.noLabel')" width="56" align="center" :index="(i) => (page - 1) * pageSize + i + 1" />
          <el-table-column prop="name" :label="t('common.name')" sortable="custom" min-width="200" show-overflow-tooltip />
          <el-table-column :label="t('common.customer')" min-width="280">
            <template #default="{ row }">
              <template v-if="row.actions_disabled">
                <span class="brand-master-group-label">{{ row.customer_name }}</span>
              </template>
              <template v-else>
                <div v-if="!(row.customer_names || []).length" class="brand-cell-empty">{{ t('common.emptyValue') }}</div>
                <el-tooltip v-else placement="top-start" :show-after="200">
                  <template #content>
                    <div class="brand-customer-tooltip">
                      <p class="brand-customer-tooltip__title">
                        {{ t('common.customer') }} ({{ row.customer_names.length }})
                      </p>
                      <ol class="brand-customer-tooltip__list">
                        <li v-for="(name, idx) in row.customer_names" :key="`${idx}-${name}`">{{ name }}</li>
                      </ol>
                    </div>
                  </template>
                  <div class="brand-customer-cell">
                    <span class="brand-customer-cell__badge">{{ row.customer_names.length }}</span>
                    <span class="brand-customer-cell__text">{{ row.customer_names[0] }}</span>
                    <span v-if="row.customer_names.length > 1" class="brand-customer-cell__more">
                      +{{ row.customer_names.length - 1 }}
                    </span>
                  </div>
                </el-tooltip>
              </template>
            </template>
          </el-table-column>
          <el-table-column :label="t('common.buyer')" min-width="160" show-overflow-tooltip>
            <template #default="{ row }">
              <span v-if="row.actions_disabled" />
              <span v-else-if="!(row.buyer_codes || []).length" class="brand-cell-empty">{{ t('common.emptyValue') }}</span>
              <span v-else>{{ row.buyer_codes.join(', ') }}</span>
            </template>
          </el-table-column>
          <el-table-column :label="t('common.actions')" width="112" align="center" fixed="right">
            <template #default="{ row }">
              <AdminTableActions
                v-if="!row.actions_disabled"
                :show-view="true"
                :show-edit="canUpdate"
                :show-delete="canDelete"
                @view="openDetail(row)"
                @edit="openEdit(row)"
                @delete="removeRow(row)"
              />
            </template>
          </el-table-column>
        </el-table>
        <div class="flex justify-end mt-3 px-1 pb-2">
          <el-pagination
            v-model:current-page="page"
            v-model:page-size="pageSize"
            :page-sizes="[10, 20, 50, 100]"
            layout="total, sizes, prev, pager, next"
            :total="totalRows"
            background
          />
        </div>
      </div>
    </div>

    <el-dialog
      v-model="formVisible"
      width="520px"
      destroy-on-close
      align-center
      class="brand-master-dialog"
      :show-close="true"
      @closed="resetForm"
    >
      <template #header>
        <div class="brand-dialog-header">
          <div class="brand-dialog-header__main">
            <h3 class="brand-dialog-header__title">
              {{ isEdit ? t('pages.brandMaster.editTitle') : t('pages.brandMaster.createTitle') }}
            </h3>
            <p class="brand-dialog-header__sub">{{ t('pages.brandMaster.dialogFormSub') }}</p>
          </div>
        </div>
      </template>

      <div class="brand-dialog-body">
        <div class="brand-dialog-panel">
          <div class="brand-dialog-panel__head">
            <h4 class="brand-dialog-panel__title">{{ t('pages.brandMaster.dialogGroupIdentity') }}</h4>
          </div>
          <div class="brand-dialog-panel__body">
            <el-form label-position="top" @submit.prevent>
              <el-form-item :label="t('common.name')" required>
                <el-input v-model="form.name" maxlength="255" clearable />
              </el-form-item>
              <el-form-item>
                <template #label>
                  <span class="brand-form-label-with-hint">
                    {{ t('common.customer') }}
                    <el-tooltip placement="top-start" :show-after="200">
                      <template #content>{{ t('pages.brandMaster.customerFieldHint') }}</template>
                      <el-icon class="brand-page-hint brand-page-hint--inline" :size="14" tabindex="0" :aria-label="t('pages.brandMaster.customerFieldHint')">
                        <InfoFilled />
                      </el-icon>
                    </el-tooltip>
                  </span>
                </template>
                <el-select v-model="form.customer_ids" multiple clearable filterable class="w-full">
                  <el-option
                    v-for="c in customers"
                    :key="c.id"
                    :label="customerOptionLabel(c)"
                    :value="c.id"
                  />
                </el-select>
              </el-form-item>
              <el-form-item>
                <template #label>
                  <span class="brand-form-label-with-hint">
                    {{ t('common.buyer') }}
                    <el-tooltip placement="top-start" :show-after="200">
                      <template #content>{{ t('pages.brandMaster.buyerFieldHint') }}</template>
                      <el-icon class="brand-page-hint brand-page-hint--inline" :size="14" tabindex="0" :aria-label="t('pages.brandMaster.buyerFieldHint')">
                        <InfoFilled />
                      </el-icon>
                    </el-tooltip>
                  </span>
                </template>
                <el-select
                  v-model="form.buyer_codes"
                  multiple
                  clearable
                  filterable
                  class="w-full"
                  :placeholder="t('pages.brandMaster.buyerMapPlaceholder')"
                >
                  <el-option v-for="code in buyerSelectOptions" :key="code" :label="code" :value="code" />
                </el-select>
              </el-form-item>
            </el-form>
          </div>
        </div>
      </div>

      <template #footer>
        <div class="brand-dialog-footer">
          <el-button :icon="Close" @click="formVisible = false">{{ t('common.cancel') }}</el-button>
          <el-button v-if="canCreate || canUpdate" type="primary" :icon="Check" :loading="saving" @click="submit">
            {{ t('common.save') }}
          </el-button>
        </div>
      </template>
    </el-dialog>

    <el-dialog
      v-model="detailVisible"
      width="560px"
      destroy-on-close
      align-center
      class="brand-master-dialog"
      :show-close="true"
      @closed="detailRow = null"
    >
      <template #header>
        <div class="brand-dialog-header">
          <div class="brand-dialog-header__main">
            <h3 class="brand-dialog-header__title">{{ t('pages.brandMaster.dialogDetail') }}</h3>
            <p v-if="detailRow" class="brand-dialog-header__sub">{{ detailRow.name || '—' }}</p>
          </div>
        </div>
      </template>

      <div v-if="detailRow" class="brand-dialog-body">
        <div class="brand-dialog-panel">
          <div class="brand-dialog-panel__head">
            <h4 class="brand-dialog-panel__title">{{ t('pages.brandMaster.detailGroupSummary') }}</h4>
          </div>
          <div class="brand-dialog-panel__body">
            <el-descriptions :column="1" border size="small">
              <el-descriptions-item :label="t('common.name')">{{ detailRow.name || '—' }}</el-descriptions-item>
            </el-descriptions>

            <div class="brand-summary-block">
              <div class="brand-summary-block__head">
                <h5 class="brand-summary-block__title">{{ t('common.customer') }}</h5>
                <span class="brand-summary-block__count">{{ detailCustomers.length }}</span>
              </div>
              <div v-if="detailCustomers.length" class="brand-detail-customers">
                <el-tag
                  v-for="(c, idx) in detailCustomers"
                  :key="`${c}-${idx}`"
                  size="small"
                  effect="plain"
                  type="info"
                >
                  {{ c }}
                </el-tag>
              </div>
              <p v-else class="brand-cell-empty">{{ t('common.emptyValue') }}</p>
            </div>

            <div class="brand-summary-block">
              <div class="brand-summary-block__head">
                <h5 class="brand-summary-block__title">{{ t('common.buyer') }}</h5>
                <span class="brand-summary-block__count">{{ detailBuyers.length }}</span>
              </div>
              <div v-if="detailBuyers.length" class="brand-detail-customers">
                <el-tag
                  v-for="code in detailBuyers"
                  :key="code"
                  size="small"
                  effect="plain"
                  type="info"
                >
                  {{ code }}
                </el-tag>
              </div>
              <p v-else class="brand-cell-empty">{{ t('common.emptyValue') }}</p>
            </div>
          </div>
        </div>
      </div>

      <template #footer>
        <div class="brand-dialog-footer brand-dialog-footer--single">
          <el-button type="primary" @click="detailVisible = false">{{ t('common.close') }}</el-button>
        </div>
      </template>
    </el-dialog>
  </AdminSection>
</template>

<script setup>
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Check, Close, InfoFilled, Plus, Refresh } from '@element-plus/icons-vue'
import AdminSection from '../../components/AdminSection.vue'
import AdminTableActions from '../../components/admin/AdminTableActions.vue'
import {
  createBrand,
  deleteBrand,
  listBrandsPage,
  listBuyerPriceLists,
  listCustomers,
  replaceBrandBuyers,
  updateBrand,
} from '../../api/client'
import { useModulePermission } from '../../composables/useModulePermission'
import { buildPageParams, fromElSortChange, normalizePageResult } from '../../utils/tableQuery'

const { t } = useI18n()
const { canCreate, canUpdate, canDelete } = useModulePermission('brandMaster')
const loading = ref(false)
const saving = ref(false)
const keyword = ref('')
const filterCustomerId = ref('')
const groupByCustomer = ref(false)
const rows = ref([])
const customers = ref([])
const buyerOptions = ref([])
const page = ref(1)
const pageSize = ref(20)
const totalRows = ref(0)
const sortBy = ref(null)
const sortDir = ref('desc')

const formVisible = ref(false)
const isEdit = ref(false)
const editingId = ref(null)
const detailVisible = ref(false)
const detailRow = ref(null)
const form = reactive({
  name: '',
  customer_ids: [],
  buyer_codes: [],
})

const buyerSelectOptions = computed(() => {
  const codes = new Set(buyerOptions.value)
  for (const code of form.buyer_codes || []) {
    if (code) codes.add(code)
  }
  return [...codes].sort()
})

const baseFilteredRows = computed(() => {
  const q = keyword.value.trim().toLowerCase()
  return rows.value.filter((r) => {
    if (filterCustomerId.value && !(r.customer_ids || []).includes(filterCustomerId.value)) return false
    if (!q) return true
    const hay = [r.name, ...(r.customer_names || []), ...(r.buyer_codes || [])].filter(Boolean).join(' ').toLowerCase()
    return hay.includes(q)
  })
})

const filteredRows = computed(() => {
  const base = baseFilteredRows.value
  if (!groupByCustomer.value) return base
  const groups = new Map()
  for (const row of base) {
    const assigned = (row.customer_ids || []).length ? row.customer_ids : [0]
    for (const gid of assigned) {
      if (!groups.has(gid)) {
        const cname = gid
          ? customers.value.find((c) => c.id === gid)?.name || t('common.emptyValue')
          : t('common.emptyValue')
        groups.set(gid, {
          id: `g-${gid}`,
          code: '',
          name: cname,
          customer_name: cname,
          customer_names: [cname],
          actions_disabled: true,
          children: [],
        })
      }
      groups.get(gid).children.push({
        ...row,
        source_id: row.id,
        id: `g-${gid}-b-${row.id}`,
      })
    }
  }
  return Array.from(groups.values())
})

const listStats = computed(() => {
  const base = baseFilteredRows.value
  return {
    total: totalRows.value,
    shown: base.length,
    withCustomer: base.filter((r) => (r.customer_ids || []).length > 0).length,
  }
})

const detailCustomers = computed(() => {
  if (!detailRow.value) return []
  return (detailRow.value.customer_names || []).filter(Boolean)
})

const detailBuyers = computed(() => {
  if (!detailRow.value) return []
  return (detailRow.value.buyer_codes || []).filter(Boolean)
})

function customerOptionLabel(c) {
  return `${c.code || ''} ${c.name || ''}`.trim() || String(c.id)
}

function resetForm() {
  form.name = ''
  form.customer_ids = []
  form.buyer_codes = []
  isEdit.value = false
  editingId.value = null
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
        q: keyword.value.trim() || undefined,
        customer_id: filterCustomerId.value || undefined,
      },
    })
    const [raw, cust, priceLists] = await Promise.all([
      listBrandsPage(params),
      listCustomers(),
      listBuyerPriceLists({ page: 1, pageSize: 200 }).catch(() => []),
    ])
    customers.value = normalizePageResult(cust).items
    const priceItems = normalizePageResult(priceLists).items
    buyerOptions.value = [...new Set(priceItems.map((row) => String(row.buyer_code || '').trim()).filter(Boolean))].sort()
    const pageData = normalizePageResult(raw, { page: page.value, pageSize: pageSize.value })
    totalRows.value = pageData.total
    rows.value = pageData.items.map((b) => ({
      ...b,
      customer_names: (b.customer_ids || []).map((id) => cust.find((c) => c.id === id)?.name).filter(Boolean),
      customer_name: (b.customer_ids || []).map((id) => cust.find((c) => c.id === id)?.name).filter(Boolean).join(', ') || t('common.emptyValue'),
      buyer_codes: [...(b.buyer_codes || [])],
    }))
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  } finally {
    loading.value = false
  }
}

function openCreate() {
  resetForm()
  formVisible.value = true
}

function openEdit(row) {
  isEdit.value = true
  editingId.value = row.source_id || row.id
  form.name = row.name || ''
  form.customer_ids = [...(row.customer_ids || [])]
  form.buyer_codes = [...(row.buyer_codes || [])]
  formVisible.value = true
}

function openDetail(row) {
  detailRow.value = row
  detailVisible.value = true
}

async function submit() {
  if (!form.name?.trim()) {
    ElMessage.warning(t('pages.brandMaster.codeRequired'))
    return
  }
  saving.value = true
  try {
    const payload = {
      name: form.name?.trim() || undefined,
      customer_ids: [...(form.customer_ids || [])],
    }
    let brandId = editingId.value
    if (isEdit.value && editingId.value) {
      await updateBrand(editingId.value, payload)
    } else {
      const created = await createBrand(payload)
      brandId = created?.id
    }
    if (brandId) {
      await replaceBrandBuyers(brandId, { buyer_codes: [...(form.buyer_codes || [])] })
    }
    formVisible.value = false
    ElMessage.success(t('common.save'))
    await load()
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  } finally {
    saving.value = false
  }
}

async function removeRow(row) {
  const targetId = row.source_id || row.id
  try {
    await ElMessageBox.confirm(
      t('pages.brandMaster.deleteConfirm', { name: row.name || row.id }),
      t('pages.brandMaster.deleteTitle'),
      {
        type: 'warning',
        confirmButtonText: t('common.delete'),
        cancelButtonText: t('common.cancel'),
      },
    )
    await deleteBrand(targetId)
    ElMessage.success(t('common.deleteSuccess'))
    await load()
  } catch (e) {
    if (e !== 'cancel') ElMessage.error(e.message || t('common.errorGeneric'))
  }
}

function onSortChange(payload) {
  const mapped = fromElSortChange(payload)
  sortBy.value = mapped.sortBy
  sortDir.value = mapped.sortDir
  page.value = 1
  load()
}

watch([keyword, filterCustomerId], () => {
  page.value = 1
  load()
})
watch([page, pageSize], () => load())

onMounted(load)
</script>

<style scoped>
.brand-inner-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
}

.brand-page-hint {
  color: #94a3b8;
  cursor: help;
  flex-shrink: 0;
  outline: none;
}

.brand-page-hint--inline {
  vertical-align: middle;
}

.brand-page-hint:hover,
.brand-page-hint:focus-visible {
  color: var(--el-color-primary);
}

.brand-master-stats {
  border-bottom: 1px solid #e2e8f0;
}

.brand-filter-panel {
  margin: 0 16px;
}

.brand-filter-row {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 12px 16px;
}

.brand-filter-customer {
  min-width: 0;
  flex: 1 1 220px;
  max-width: 100%;
}

.brand-filter-toggle {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.brand-filter-toggle__label {
  font-size: 13px;
  color: #475569;
}

.brand-master-table-wrap {
  padding: 0 16px 16px;
}

.brand-master-group-label {
  font-weight: 600;
  color: #334155;
}

.brand-cell-empty {
  color: #94a3b8;
  font-size: 13px;
}

.brand-customer-cell {
  display: flex;
  align-items: center;
  gap: 6px;
  min-width: 0;
  cursor: help;
}

.brand-customer-cell__badge {
  flex-shrink: 0;
  min-width: 1.5rem;
  padding: 0 6px;
  border-radius: 999px;
  background: #e0f2fe;
  color: #0369a1;
  font-size: 11px;
  font-weight: 600;
  line-height: 1.6;
  text-align: center;
}

.brand-customer-cell__text {
  flex: 1;
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-size: 12px;
  color: #334155;
}

.brand-customer-cell__more {
  flex-shrink: 0;
  font-size: 11px;
  color: #64748b;
}

.brand-customer-tooltip__title {
  margin: 0 0 6px;
  font-size: 12px;
  font-weight: 600;
}

.brand-customer-tooltip__list {
  margin: 0;
  padding-left: 1.1rem;
  max-height: 200px;
  overflow-y: auto;
  font-size: 12px;
  line-height: 1.45;
}

.brand-customer-tooltip__list li + li {
  margin-top: 4px;
}

.brand-form-label-with-hint {
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

:deep(.brand-master-dialog.el-dialog) {
  border-radius: 14px;
  overflow: hidden;
  max-height: 92vh;
  display: flex;
  flex-direction: column;
}

:deep(.brand-master-dialog .el-dialog__header) {
  padding: 16px 20px 12px;
  margin: 0;
  border-bottom: 1px solid #e2e8f0;
}

:deep(.brand-master-dialog .el-dialog__body) {
  padding: 0;
  background: #f8fafc;
  overflow-y: auto;
}

:deep(.brand-master-dialog .el-dialog__footer) {
  padding: 12px 20px 16px;
  border-top: 1px solid #e2e8f0;
}

.brand-dialog-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
  padding-right: 28px;
}

.brand-dialog-header__title {
  margin: 0;
  font-size: 1.05rem;
  font-weight: 600;
  color: #0f172a;
  line-height: 1.3;
}

.brand-dialog-header__sub {
  margin: 4px 0 0;
  font-size: 12px;
  color: #64748b;
  line-height: 1.45;
}

.brand-dialog-body {
  padding: 16px;
}

.brand-dialog-panel {
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  background: #fff;
  overflow: hidden;
}

.brand-dialog-panel__head {
  padding: 12px 16px;
  border-bottom: 1px solid #e2e8f0;
  background: #f8fafc;
}

.brand-dialog-panel__title {
  margin: 0;
  font-size: 0.9rem;
  font-weight: 600;
  color: #0f172a;
}

.brand-dialog-panel__body {
  padding: 16px;
}

.brand-summary-block {
  margin-top: 16px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  background: #f8fafc;
  overflow: hidden;
}

.brand-summary-block__head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  padding: 10px 12px;
  border-bottom: 1px solid #e2e8f0;
  background: #fff;
}

.brand-summary-block__title {
  margin: 0;
  font-size: 12px;
  font-weight: 600;
  color: #0f172a;
}

.brand-summary-block__count {
  flex-shrink: 0;
  min-width: 1.5rem;
  padding: 0 8px;
  border-radius: 999px;
  background: #e0f2fe;
  color: #0369a1;
  font-size: 11px;
  font-weight: 600;
  line-height: 1.7;
  text-align: center;
}

.brand-detail-customers {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  padding: 12px;
}

.brand-dialog-footer {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 8px;
  width: 100%;
}

.brand-dialog-footer--single {
  justify-content: flex-end;
}
</style>
