<template>
  <div>
    <div class="admin-stats-grid admin-stats-grid--4 inventory-stats">
      <div class="admin-stat-card">
        <span class="admin-stat-card__value">{{ summary.total_materials || 0 }}</span>
        <span class="admin-stat-card__label">{{ t('pages.inventory.totalMaterials') }}</span>
      </div>
      <div class="admin-stat-card">
        <span class="admin-stat-card__value">{{ formatCurrency(summary.total_value || 0) }}</span>
        <span class="admin-stat-card__label">{{ t('pages.inventory.totalValue') }}</span>
      </div>
      <div class="admin-stat-card" :class="{ 'admin-stat-card--warn': summary.low_stock_count > 0 }">
        <span class="admin-stat-card__value">{{ summary.low_stock_count || 0 }}</span>
        <span class="admin-stat-card__label">{{ t('pages.inventory.lowStock') }}</span>
      </div>
      <div class="admin-stat-card">
        <span class="admin-stat-card__value">{{ summary.total_warehouses || 0 }}</span>
        <span class="admin-stat-card__label">{{ t('pages.inventory.totalWarehouses') }}</span>
      </div>
    </div>

    <div class="admin-inner-card">
      <div class="admin-inner-card__head">
        <div>
          <h3 class="admin-inner-card__title">{{ t('pages.inventory.stockListTitle') }}</h3>
          <p class="admin-inner-card__sub">
            {{ t('pages.inventory.stockListSubtitle', { n: filtered.length, total: stocks.length }) }}
          </p>
        </div>
        <el-input
          v-model="search"
          clearable
          size="small"
          class="inventory-toolbar__search"
          :placeholder="t('pages.inventory.searchPlaceholder')"
        />
      </div>

      <el-table
        :data="filtered" @sort-change="onSortChange"
        v-loading="loading"
        border
        stripe
        size="small"
        class="admin-table"
        table-layout="fixed"
        :empty-text="t('pages.inventory.tableEmpty')"
      >
        <el-table-column type="index" width="56" :label="t('common.noLabel')" align="center" />
        <el-table-column prop="material_code" :label="t('pages.inventory.materialCode')" min-width="120" show-overflow-tooltip />
        <el-table-column prop="material_name" :label="t('pages.inventory.materialName')" min-width="180" show-overflow-tooltip />
        <el-table-column prop="warehouse_name" :label="t('pages.inventory.warehouse')" min-width="140" show-overflow-tooltip />
        <el-table-column :label="t('pages.inventory.currentStock')" width="130" align="right">
          <template #default="{ row }">
            {{ formatNumber(row.current_stock) }} {{ row.material_unit || '' }}
          </template>
        </el-table-column>
        <el-table-column :label="t('pages.inventory.minStock')" width="100" align="right">
          <template #default="{ row }">{{ formatNumber(row.min_stock) || '-' }}</template>
        </el-table-column>
        <el-table-column :label="t('common.status')" width="110" align="center">
          <template #default="{ row }">
            <el-tag v-if="row.current_stock < (row.min_stock || 0)" type="danger" size="small">
              {{ t('pages.inventory.low') }}
            </el-tag>
            <el-tag v-else type="success" size="small">{{ t('pages.inventory.ok') }}</el-tag>
          </template>
        </el-table-column>
      </el-table>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessage } from 'element-plus'
import { listStocks, getStockSummary } from '../../../api/client'
import { buildPageParams, fromElSortChange, normalizePageResult } from '../../../utils/tableQuery'
import { formatCurrency, formatNumber } from '../../../utils/format'

const emit = defineEmits(['loading'])
const { t } = useI18n()
const loading = ref(false)
const page = ref(1)
const pageSize = ref(20)
const totalRows = ref(0)
const sortBy = ref(null)
const sortDir = ref('asc')
const stocks = ref([])
const summary = ref({})
const search = ref('')

watch(loading, (v) => emit('loading', v))

const filtered = computed(() => {
  const q = search.value.trim().toLowerCase()
  if (!q) return stocks.value
  return stocks.value.filter((row) =>
    [row.material_code, row.material_name, row.warehouse_name]
      .filter(Boolean)
      .some((v) => String(v).toLowerCase().includes(q))
  )
})

async function reload() {
  loading.value = true
  try {
    const [stockRows, summaryRow] = await Promise.all([listStocks(), getStockSummary()])
    stocks.value = stockRows || []
    summary.value = summaryRow || {}
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  } finally {
    loading.value = false
  }
}

defineExpose({ reload })
function onSortChange(payload) {
  const mapped = fromElSortChange(payload)
  sortBy.value = mapped.sortBy
  sortDir.value = mapped.sortDir
  page.value = 1
  reload()
}
watch([page, pageSize], () => reload())
onMounted(reload)
</script>

<style scoped>
.inventory-stats {
  padding: 0;
  margin-bottom: 16px;
}
.inventory-toolbar__search {
  width: 15rem;
  max-width: 100%;
  min-width: 0;
}
@media (min-width: 900px) {
  .inventory-stats.admin-stats-grid--4 {
    grid-template-columns: repeat(4, minmax(0, 1fr));
  }
}
</style>
