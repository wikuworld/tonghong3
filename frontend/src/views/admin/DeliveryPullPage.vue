<template>
  <AdminSection :title="t('pages.deliveryPull.title')" :subtitle="t('pages.deliveryPull.subtitle')">
    <div class="filter-panel">
      <div class="filter-panel__title">{{ t('common.filter') }}</div>
      <el-form label-position="top" class="filter-form">
        <el-row :gutter="12">
          <el-col :xs="24" :sm="12" :md="6">
            <el-form-item :label="t('common.customer')">
              <el-input v-model="filter.customer" :placeholder="t('common.placeholder.customer')" />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :sm="12" :md="6">
            <el-form-item :label="t('common.orderNo')">
              <el-input v-model="filter.orderNo" :placeholder="t('common.placeholder.orderNo')" />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :sm="24" :md="6">
            <el-form-item :label="t('common.dateRange')">
              <el-date-picker
                v-model="filter.dateRange"
                type="daterange"
                :range-separator="t('common.rangeSeparator')"
                :start-placeholder="t('common.startDate')"
                :end-placeholder="t('common.endDate')"
                class="w-full"
                :shortcuts="dateShortcuts"
                unlink-panels
                value-format="YYYY-MM-DD"
              />
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <div class="mt-1 flex flex-wrap gap-2">
        <el-button type="primary" :icon="Search">{{ t('common.search') }}</el-button>
        <el-button type="success" :icon="Check">{{ t('pages.deliveryPull.title') }}</el-button>
        <el-button :icon="Refresh" @click="resetFilter">{{ t('common.reset') }}</el-button>
      </div>
    </div>

    <el-table :data="rows" border stripe size="small" class="admin-table" table-layout="fixed" :empty-text="t('common.tableEmpty')">
      <el-table-column prop="no" :label="t('common.noLabel')" width="60" align="center" />
      <el-table-column prop="sj" :label="t('common.deliveryNo')" min-width="160" />
      <el-table-column prop="customer" :label="t('common.customer')" min-width="180" />
      <el-table-column prop="material" :label="t('common.material')" min-width="140" />
      <el-table-column prop="thickness" :label="t('common.thickness')" min-width="120" />
      <el-table-column prop="color" :label="t('common.color')" min-width="120" />
      <el-table-column prop="qty" :label="t('common.quantity')" min-width="100" align="right" />
      <el-table-column prop="roll" :label="t('common.roll')" min-width="90" align="center" />
      <el-table-column prop="pcs" :label="t('common.pieces')" min-width="90" align="center" />
      <el-table-column :label="t('common.actions')" width="132" align="center" fixed="right">
        <template #default>
          <div class="flex flex-wrap items-center justify-center gap-0">
            <el-tooltip :content="t('common.detail')" placement="top">
              <el-button size="small" type="primary" :icon="View" :aria-label="t('common.detail')" />
            </el-tooltip>
            <el-tooltip :content="t('common.edit')" placement="top">
              <el-button size="small" :icon="EditPen" :aria-label="t('common.edit')" />
            </el-tooltip>
            <el-tooltip :content="t('common.delete')" placement="top">
              <el-button size="small" type="danger" :icon="Delete" :aria-label="t('common.delete')" />
            </el-tooltip>
          </div>
        </template>
      </el-table-column>
    </el-table>

    <div class="mt-4 flex justify-end gap-2">
      <el-button :icon="Close">{{ t('common.cancel') }}</el-button>
      <el-button type="primary" :icon="Check">{{ t('common.confirm') }}</el-button>
    </div>
  </AdminSection>
</template>

<script setup>
import { computed, reactive } from 'vue'
import { useI18n } from 'vue-i18n'
import { Delete, EditPen, View, Search, Close, Refresh, Check } from '@element-plus/icons-vue'
import AdminSection from '../../components/AdminSection.vue'

const { t } = useI18n()
const filter = reactive({ customer: '', orderNo: '', dateRange: [] })

const dateShortcuts = computed(() => [
  {
    text: t('common.shortcutToday'),
    value: () => {
      const end = new Date()
      const start = new Date()
      return [start, end]
    },
  },
  {
    text: t('common.shortcutLast7Days'),
    value: () => {
      const end = new Date()
      const start = new Date()
      start.setTime(start.getTime() - 3600 * 1000 * 24 * 7)
      return [start, end]
    },
  },
  {
    text: t('common.shortcutLast30Days'),
    value: () => {
      const end = new Date()
      const start = new Date()
      start.setTime(start.getTime() - 3600 * 1000 * 24 * 30)
      return [start, end]
    },
  },
  {
    text: t('common.shortcutLast90Days'),
    value: () => {
      const end = new Date()
      const start = new Date()
      start.setTime(start.getTime() - 3600 * 1000 * 24 * 90)
      return [start, end]
    },
  },
  {
    text: t('common.shortcutThisMonth'),
    value: () => {
      const end = new Date()
      const start = new Date(end.getFullYear(), end.getMonth(), 1)
      return [start, end]
    },
  },
  {
    text: t('common.shortcutLastMonth'),
    value: () => {
      const end = new Date()
      end.setDate(0)
      const start = new Date(end.getFullYear(), end.getMonth(), 1)
      return [start, end]
    },
  },
])

const rows = reactive([
  { no: 1, sj: 'THI-M26026001', customer: 'PT. CUSTOMER', material: 'Split Suede', thickness: '1.2 - 1.4', color: 'Grey', qty: 327.8, roll: 2, pcs: 15 },
  { no: 2, sj: 'THI-M26026002', customer: 'PT. CUSTOMER', material: 'Split Suede', thickness: '1.2 - 1.4', color: 'Grey', qty: 327.8, roll: 2, pcs: 15 },
])

const resetFilter = () => {
  filter.customer = ''
  filter.orderNo = ''
  filter.dateRange = []
}
</script>
