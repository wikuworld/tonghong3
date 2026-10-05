<template>
  <AdminSection :title="t('pages.inventory.stockTitle')" :subtitle="t('pages.inventory.stockSubtitle')">
    <template #actions>
      <el-button type="primary" :icon="Refresh" @click="refresh">{{ t('common.refresh') }}</el-button>
    </template>

    <el-row :gutter="12" class="mb-4">
      <el-col :span="6">
        <el-statistic :title="t('pages.inventory.totalMaterials')" :value="summary.total_materials || 0" />
      </el-col>
      <el-col :span="6">
        <el-statistic :title="t('pages.inventory.totalValue')" :value="Number(summary.total_value) || 0">
          <template #formatter="{ value }">{{ formatCurrency(value) }}</template>
        </el-statistic>
      </el-col>
      <el-col :span="6">
        <el-statistic :title="t('pages.inventory.lowStock')" :value="summary.low_stock_count || 0" class="text-red-600">
          <template #suffix>
            <el-tag v-if="summary.low_stock_count > 0" type="danger" size="small">!</el-tag>
          </template>
        </el-statistic>
      </el-col>
      <el-col :span="6">
        <el-statistic :title="t('pages.inventory.totalWarehouses')" :value="summary.total_warehouses || 0" />
      </el-col>
    </el-row>

    <el-table :data="stocks" @sort-change="onSortChange" v-loading="loading" border stripe size="small" class="admin-table" table-layout="fixed" :empty-text="t('common.tableEmpty')">
      <el-table-column prop="material_code" :label="t('pages.inventory.materialCode')" width="120" />
      <el-table-column prop="material_name" :label="t('pages.inventory.materialName')" min-width="180" />
      <el-table-column prop="warehouse_name" :label="t('pages.inventory.warehouse')" width="140" />
      <el-table-column :label="t('pages.inventory.currentStock')" width="120" align="right">
        <template #default="{ row }">
          {{ formatNumber(row.current_stock) }} {{ row.material_unit }}
        </template>
      </el-table-column>
      <el-table-column :label="t('pages.inventory.minStock')" width="100" align="right">
        <template #default="{ row }">
          {{ formatNumber(row.min_stock) || '-' }}
        </template>
      </el-table-column>
      <el-table-column :label="t('common.status')" width="100">
        <template #default="{ row }">
          <el-tag v-if="row.current_stock < (row.min_stock || 0)" type="danger" size="small">
            {{ t('pages.inventory.low') }}
          </el-tag>
          <el-tag v-else type="success" size="small">
            {{ t('pages.inventory.ok') }}
          </el-tag>
        </template>
      </el-table-column>
    </el-table>
  </AdminSection>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessage } from 'element-plus'
import { Refresh } from '@element-plus/icons-vue'
import AdminSection from '../../../components/AdminSection.vue'
import { listStocks, getStockSummary } from '../../../api/client'
import { buildPageParams, fromElSortChange, normalizePageResult } from '../../../utils/tableQuery'
import { formatCurrency, formatNumber } from '../../../utils/format'

const { t } = useI18n()
const loading = ref(false)
const page = ref(1)
const pageSize = ref(20)
const totalRows = ref(0)
const sortBy = ref(null)
const sortDir = ref('asc')
const stocks = ref([])
const summary = ref({})

async function refresh() {
  loading.value = true
  try {
    const raw = await listStocks(buildPageParams({ page: page.value, pageSize: pageSize.value, sortBy: sortBy.value, sortDir: sortDir.value }))
    const pageData = normalizePageResult(raw, { page: page.value, pageSize: pageSize.value })
    stocks.value = pageData.items
    totalRows.value = pageData.total
    summary.value = await getStockSummary()
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  } finally {
    loading.value = false
  }
}

onMounted(refresh)
</script>