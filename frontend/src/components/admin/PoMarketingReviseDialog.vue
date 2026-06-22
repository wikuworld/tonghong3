<template>
  <el-dialog
    :model-value="modelValue"
    :title="t('pages.po.marketingReviseTitle')"
    width="720px"
    destroy-on-close
    align-center
    @update:model-value="$emit('update:modelValue', $event)"
  >
    <p class="text-xs text-slate-600 mb-3">{{ t('pages.po.marketingReviseHint') }}</p>
    <el-form label-position="top" size="small">
      <el-form-item :label="t('pages.po.headerEtd')">
        <el-date-picker
          v-model="header.etd"
          type="date"
          value-format="YYYY-MM-DD"
          class="w-full"
        />
      </el-form-item>
      <el-form-item :label="t('pages.po.deliveryAddress')">
        <el-input v-model="header.delivery_address" type="textarea" :rows="2" />
      </el-form-item>
      <el-form-item :label="t('pages.marketingFlow.materialRemark')">
        <el-input v-model="header.material_followup_remark" type="textarea" :rows="2" />
      </el-form-item>
      <el-form-item :label="t('pages.marketingFlow.materialDone')">
        <el-switch v-model="header.material_followup_done" />
      </el-form-item>
    </el-form>
    <div class="text-sm font-medium mt-4 mb-2">{{ t('pages.po.lineEtd') }} / {{ t('pages.po.detailRemark') }}</div>
    <el-table v-loading="loading" :data="lines" border size="small" max-height="320">
      <el-table-column prop="detail_id" label="ID" width="72" />
      <el-table-column prop="material_name" :label="t('common.material')" min-width="120" show-overflow-tooltip />
      <el-table-column :label="t('pages.po.lineEtd')" width="138">
        <template #default="{ row }">
          <el-date-picker v-model="row.line_etd" type="date" value-format="YYYY-MM-DD" size="small" class="!w-full" />
        </template>
      </el-table-column>
      <el-table-column :label="t('pages.po.detailRemark')" min-width="100">
        <template #default="{ row }">
          <el-input v-model="row.detail_remark" size="small" />
        </template>
      </el-table-column>
      <el-table-column :label="t('pages.po.colMarketingOutstandingRemark')" min-width="120">
        <template #default="{ row }">
          <el-input v-model="row.marketing_outstanding_remark" size="small" />
        </template>
      </el-table-column>
      <el-table-column :label="t('pages.marketingFlow.colRtd')" width="96">
        <template #default="{ row }">
          <el-input v-model="row.rtd_text" size="small" />
        </template>
      </el-table-column>
    </el-table>
    <template #footer>
      <el-button @click="$emit('update:modelValue', false)">{{ t('common.cancel') }}</el-button>
      <el-button type="primary" :loading="saving" @click="$emit('save')">{{ t('common.save') }}</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { useI18n } from 'vue-i18n'

defineProps({
  modelValue: { type: Boolean, default: false },
  loading: { type: Boolean, default: false },
  saving: { type: Boolean, default: false },
})

const header = defineModel('header', { type: Object, required: true })
const lines = defineModel('lines', { type: Array, default: () => [] })

defineEmits(['update:modelValue', 'save'])

const { t } = useI18n()
</script>
