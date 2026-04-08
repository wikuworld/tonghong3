<template>
  <AdminSection :title="t('pages.poEntry.title')" :subtitle="t('pages.poEntry.subtitle')">
    <el-form label-position="top">
      <el-row :gutter="12">
        <el-col :xs="24" :md="12">
          <el-form-item :label="t('common.code')">
            <el-input v-model="form.customerCode" :placeholder="t('common.placeholder.customerCode')" />
          </el-form-item>
        </el-col>
        <el-col :xs="24" :md="12">
          <el-form-item :label="t('common.poNo')">
            <el-input v-model="form.poNumber" :placeholder="t('common.placeholder.poNumber')" />
          </el-form-item>
        </el-col>
        <el-col :xs="24" :md="12">
          <el-form-item :label="t('common.category')">
            <el-select v-model="form.category" class="w-full" :placeholder="t('common.placeholder.deliveryType')">
              <el-option :label="t('status.production')" value="production" />
              <el-option :label="t('status.sample')" value="sample" />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :xs="24" :md="12">
          <el-form-item :label="t('common.buyer')">
            <el-input v-model="form.buyer" :placeholder="t('common.placeholder.buyer')" />
          </el-form-item>
        </el-col>
        <el-col :xs="24" :md="12">
          <el-form-item :label="t('common.material')">
            <el-input v-model="form.material" :placeholder="t('common.placeholder.material')" />
          </el-form-item>
        </el-col>
        <el-col :xs="24" :md="12">
          <el-form-item :label="t('common.thickness')">
            <el-input v-model="form.thickness" :placeholder="t('common.placeholder.thickness')" />
          </el-form-item>
        </el-col>
        <el-col :xs="24" :md="12">
          <el-form-item :label="t('common.color')">
            <el-input v-model="form.color" :placeholder="t('common.placeholder.color')" />
          </el-form-item>
        </el-col>
        <el-col :xs="24" :md="12">
          <el-form-item :label="t('common.softness')">
            <el-input v-model="form.softness" :placeholder="t('common.placeholder.softness')" />
          </el-form-item>
        </el-col>
        <el-col :xs="24" :md="12">
          <el-form-item :label="t('common.quantity')">
            <el-input v-model="form.quantity" :placeholder="t('common.placeholder.quantity')" />
          </el-form-item>
        </el-col>
        <el-col :xs="24" :md="12">
          <el-form-item :label="t('common.etd')">
            <el-date-picker v-model="form.etd" type="date" class="w-full" :placeholder="t('common.placeholder.etd')" />
          </el-form-item>
        </el-col>
        <el-col :xs="24">
          <el-form-item :label="t('common.remark')">
            <el-input v-model="form.remark" type="textarea" :rows="3" :placeholder="t('common.placeholder.remark')" />
          </el-form-item>
        </el-col>
      </el-row>
    </el-form>

    <div class="mt-3 flex justify-end gap-2">
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
  customerCode: '',
  poNumber: '',
  category: 'production',
  buyer: '',
  material: '',
  thickness: '',
  color: '',
  softness: '',
  quantity: '',
  etd: '',
  remark: '',
})
</script>
