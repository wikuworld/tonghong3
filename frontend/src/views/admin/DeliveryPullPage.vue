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
          <el-col :xs="24" :sm="12" :md="6">
            <el-form-item :label="`${t('common.date')} ${t('common.from')}`">
              <el-date-picker v-model="filter.fromDate" type="date" class="w-full" :placeholder="t('common.placeholder.fromDate')" />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :sm="12" :md="6">
            <el-form-item :label="`${t('common.date')} ${t('common.to')}`">
              <el-date-picker v-model="filter.toDate" type="date" class="w-full" :placeholder="t('common.placeholder.toDate')" />
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <div class="mt-1 flex flex-wrap gap-2">
        <el-button type="primary">{{ t('common.search') }}</el-button>
        <el-button type="success">{{ t('pages.deliveryPull.title') }}</el-button>
        <el-button @click="resetFilter">{{ t('common.reset') }}</el-button>
      </div>
    </div>

    <el-table :data="rows" border stripe size="small" class="admin-table" table-layout="auto">
      <el-table-column prop="no" :label="t('common.noLabel')" width="60" align="center" />
      <el-table-column prop="sj" :label="t('common.deliveryNo')" min-width="160" />
      <el-table-column prop="customer" :label="t('common.customer')" min-width="180" />
      <el-table-column prop="material" :label="t('common.material')" min-width="140" />
      <el-table-column prop="thickness" :label="t('common.thickness')" min-width="120" />
      <el-table-column prop="color" :label="t('common.color')" min-width="120" />
      <el-table-column prop="qty" :label="t('common.quantity')" min-width="100" align="right" />
      <el-table-column prop="roll" :label="t('common.roll')" min-width="90" align="center" />
      <el-table-column prop="pcs" :label="t('common.pieces')" min-width="90" align="center" />
      <el-table-column :label="t('common.actions')" min-width="200" align="center">
        <template #default>
          <el-button size="small" type="primary">{{ t('common.detail') }}</el-button>
          <el-button size="small">{{ t('common.edit') }}</el-button>
          <el-button size="small" type="danger">{{ t('common.delete') }}</el-button>
        </template>
      </el-table-column>
    </el-table>

    <div class="mt-4 flex justify-end gap-2">
      <el-button>{{ t('common.cancel') }}</el-button>
      <el-button type="primary">{{ t('common.confirm') }}</el-button>
    </div>
  </AdminSection>
</template>

<script setup>
import { reactive } from 'vue'
import { useI18n } from 'vue-i18n'
import AdminSection from '../../components/AdminSection.vue'

const { t } = useI18n()
const filter = reactive({ customer: '', orderNo: '', fromDate: '', toDate: '' })

const rows = reactive([
  { no: 1, sj: 'THI-M26026001', customer: 'PT. CUSTOMER', material: 'Split Suede', thickness: '1.2 - 1.4', color: 'Grey', qty: 327.8, roll: 2, pcs: 15 },
  { no: 2, sj: 'THI-M26026002', customer: 'PT. CUSTOMER', material: 'Split Suede', thickness: '1.2 - 1.4', color: 'Grey', qty: 327.8, roll: 2, pcs: 15 },
])

const resetFilter = () => {
  filter.customer = ''
  filter.orderNo = ''
  filter.fromDate = ''
  filter.toDate = ''
}
</script>
