<template>
  <el-dialog
    :model-value="modelValue"
    :title="t('pages.poDetail.title')"
    width="95%" style="max-width: 900px"
    destroy-on-close
    align-center
    class="po-dialog"
    @update:model-value="$emit('update:modelValue', $event)"
  >
    <el-descriptions v-if="detailView" :column="2" border size="small">
      <el-descriptions-item :label="t('common.poNo')">{{ detailView.po_number }}</el-descriptions-item>
      <el-descriptions-item :label="t('common.status')">{{ statusLabel(detailView.status) }}</el-descriptions-item>
      <el-descriptions-item :label="t('pages.po.poCustomerRef')">{{ detailView.po_customer_ref || t('common.emptyValue') }}</el-descriptions-item>
      <el-descriptions-item :label="t('common.customer')">{{ detailView.customerName }}</el-descriptions-item>
      <el-descriptions-item :label="t('common.buyer')">{{ detailView.buyer || t('common.emptyValue') }}</el-descriptions-item>
      <el-descriptions-item :label="t('pages.po.headerEtd')">{{ detailView.etd || t('common.emptyValue') }}</el-descriptions-item>
    </el-descriptions>
    <p class="mt-2 text-xs text-slate-500">{{ t('pages.poDetail.lineRevisionHint') }}</p>
    <el-table
      v-if="detailLines.length"
      :data="detailLines"
      class="mt-4"
      border
      size="small"
      table-layout="auto"
      max-height="360"
    >
      <el-table-column prop="material_name" :label="t('common.material')" min-width="130" show-overflow-tooltip />
      <el-table-column prop="thickness_text" :label="t('common.thickness')" width="100" />
      <el-table-column prop="color" :label="t('common.color')" width="88" />
      <el-table-column prop="color_family" :label="t('pages.po.colorFamily')" width="120" show-overflow-tooltip>
        <template #default="{ row }">{{ colorFamilyLabel(row.color_family) }}</template>
      </el-table-column>
      <el-table-column prop="emboss" :label="t('pages.po.emboss')" width="88" show-overflow-tooltip />
      <el-table-column prop="color_standard" :label="t('pages.po.colorStandart')" width="120" show-overflow-tooltip />
      <el-table-column prop="quantity_order" :label="t('common.quantityOrder')" width="96" />
      <el-table-column prop="unit_price" :label="t('pages.po.unitPriceUsd')" width="100" align="right">
        <template #default="{ row }">{{ row.unit_price != null ? row.unit_price : t('common.emptyValue') }}</template>
      </el-table-column>
      <el-table-column prop="thi_line_ref" :label="t('pages.po.thiLineRef')" min-width="110" show-overflow-tooltip />
      <el-table-column prop="style_article" :label="t('common.styleArticle')" min-width="100" show-overflow-tooltip />
      <el-table-column prop="model" :label="t('common.model')" width="96" show-overflow-tooltip />
    </el-table>
    <PoDetailAuditPanel :entries="detailAudit" />
    <template #footer>
      <el-button type="primary" :icon="Close" @click="$emit('update:modelValue', false)">{{ t('pages.customers.closeDetail') }}</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { Close } from '@element-plus/icons-vue'
import { useI18n } from 'vue-i18n'

import PoDetailAuditPanel from './PoDetailAuditPanel.vue'
import { statusLabel } from '../../utils/format'

defineProps({
  modelValue: { type: Boolean, default: false },
  detailView: { type: Object, default: null },
  detailLines: { type: Array, default: () => [] },
  detailAudit: { type: Array, default: () => [] },
  colorFamilyLabel: { type: Function, required: true },
})

defineEmits(['update:modelValue'])

const { t } = useI18n()
</script>
