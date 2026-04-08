<template>
  <AdminSection :title="t('pages.suratJalan.title')" :subtitle="t('pages.suratJalan.subtitle')">
    <el-form label-position="top">
      <el-row :gutter="12">
        <el-col :xs="24" :sm="12" :md="6">
          <el-form-item :label="t('common.factoryCode')">
            <el-input v-model="form.factory" :placeholder="t('common.placeholder.factoryCode')" />
          </el-form-item>
        </el-col>
        <el-col :xs="24" :sm="12" :md="6">
          <el-form-item :label="t('common.customerName')">
            <el-input v-model="form.customer" :placeholder="t('common.placeholder.customerName')" />
          </el-form-item>
        </el-col>
        <el-col :xs="24" :sm="12" :md="6">
          <el-form-item :label="t('common.date')">
            <el-date-picker v-model="form.deliveryDate" type="date" class="w-full" :placeholder="t('common.placeholder.deliveryDate')" />
          </el-form-item>
        </el-col>
        <el-col :xs="24" :sm="12" :md="6">
          <el-form-item :label="t('common.deliveryType')">
            <el-select v-model="form.deliveryType" class="w-full" :placeholder="t('common.placeholder.deliveryType')">
              <el-option :label="t('status.production')" value="production" />
              <el-option :label="t('status.sample')" value="sample" />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :xs="24" :sm="12" :md="6">
          <el-form-item :label="t('common.warehouse')">
            <el-input v-model="form.warehouse" :placeholder="t('common.placeholder.warehouse')" />
          </el-form-item>
        </el-col>
        <el-col :xs="24" :sm="12" :md="6">
          <el-form-item :label="t('common.vehicle')">
            <el-input v-model="form.vehicle" :placeholder="t('common.placeholder.vehicle')" />
          </el-form-item>
        </el-col>
        <el-col :xs="24" :sm="12" :md="6">
          <el-form-item :label="t('common.driver')">
            <el-input v-model="form.driver" :placeholder="t('common.placeholder.driver')" />
          </el-form-item>
        </el-col>
        <el-col :xs="24" :sm="12" :md="6">
          <el-form-item :label="t('common.remark')">
            <el-input v-model="form.remark" :placeholder="t('common.placeholder.remark')" />
          </el-form-item>
        </el-col>
      </el-row>
    </el-form>

    <el-table :data="rows" border stripe size="small" class="admin-table mt-3" table-layout="auto">
      <el-table-column prop="no" :label="t('common.noLabel')" width="60" />
      <el-table-column prop="orderNo" :label="t('common.orderNo')" min-width="150" />
      <el-table-column prop="material" :label="t('common.material')" min-width="140" />
      <el-table-column prop="thickness" :label="t('common.thickness')" min-width="110" />
      <el-table-column prop="color" :label="t('common.color')" min-width="110" />
      <el-table-column prop="orderQty" :label="t('common.quantity')" min-width="110" align="right" />
      <el-table-column prop="deliveredQty" :label="t('common.actual')" min-width="120" align="right" />
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
      <el-button type="primary">{{ t('common.save') }}</el-button>
    </div>
  </AdminSection>
</template>

<script setup>
import { reactive } from 'vue'
import { useI18n } from 'vue-i18n'
import AdminSection from '../../components/AdminSection.vue'

const { t } = useI18n()

const form = reactive({
  factory: 'SD047',
  customer: '',
  deliveryDate: '',
  deliveryType: 'production',
  warehouse: 'Finished Goods',
  vehicle: '',
  driver: '',
  remark: '',
})

const rows = reactive([
  { no: 1, orderNo: 'PS25122909', material: 'Split Suede', thickness: '1.2 - 1.4', color: 'Grey One', orderQty: 28639, deliveredQty: 4137.6, roll: 2, pcs: 15 },
])
</script>
