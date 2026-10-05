<template>
  <el-drawer
    :model-value="modelValue"
    direction="rtl"
    size="100%"
    destroy-on-close
    class="so-page-drawer po-detail-drawer"
    @update:model-value="$emit('update:modelValue', $event)"
  >
    <template #header>
      <h2 class="po-detail-drawer__title">{{ t('pages.poDetail.title') }}</h2>
    </template>
    <div class="po-detail-drawer__body">
      <el-descriptions v-if="detailView" :column="2" border size="small">
        <el-descriptions-item :label="t('common.poNo')">{{ detailView.po_number }}</el-descriptions-item>
        <el-descriptions-item :label="t('common.status')">{{ statusLabel(detailView.status) }}</el-descriptions-item>
        <el-descriptions-item :label="t('pages.po.poCustomerRef')">{{ detailView.po_customer_ref || t('common.emptyValue') }}</el-descriptions-item>
        <el-descriptions-item :label="t('common.customer')">{{ detailView.customerName }}</el-descriptions-item>
        <el-descriptions-item :label="t('common.buyer')">{{ detailView.buyer || t('common.emptyValue') }}</el-descriptions-item>
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
        <el-table-column :label="t('common.orderDate')" width="120" align="center" fixed="left">
          <template #default>
            {{
              detailView?.order_date_fmt
                || (detailView?.order_date ? String(detailView.order_date).slice(0, 10) : t('common.emptyValue'))
            }}
          </template>
        </el-table-column>
        <el-table-column
          prop="thi_line_ref"
          :label="t('pages.po.thiLineRef')"
          min-width="140"
          show-overflow-tooltip
          fixed="left"
        >
          <template #default="{ row }">{{ formatThiLot(row) }}</template>
        </el-table-column>
        <el-table-column
          prop="system_reference"
          :label="t('pages.marketingFlow.colLotNo')"
          min-width="140"
          show-overflow-tooltip
          fixed="left"
        >
          <template #default="{ row }">{{ formatNoLot(row) }}</template>
        </el-table-column>
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
        <el-table-column :label="t('common.etd')" width="112" align="center">
          <template #default>{{ formatHeaderEtd(detailView) }}</template>
        </el-table-column>
        <el-table-column :label="t('pages.marketingFlow.colReplyEtd')" width="120" align="center">
          <template #default="{ row }">{{ formatLineEtd(row.line_etd) }}</template>
        </el-table-column>
        <el-table-column prop="style_article" :label="t('common.styleArticle')" min-width="100" show-overflow-tooltip />
        <el-table-column prop="model" :label="t('common.model')" width="96" show-overflow-tooltip />
      </el-table>
      <PoDetailAuditPanel :entries="detailAudit" />
    </div>
    <template #footer>
      <div class="po-detail-drawer__footer">
        <el-button type="primary" :icon="Close" @click="$emit('update:modelValue', false)">{{ t('pages.customers.closeDetail') }}</el-button>
      </div>
    </template>
  </el-drawer>
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

function formatLineEtd(value) {
  if (value == null || value === '') return t('common.emptyValue')
  return String(value).slice(0, 10)
}

function formatHeaderEtd(view) {
  if (!view) return t('common.emptyValue')
  const fromDisplay = (view.etd_display || '').trim()
  if (fromDisplay) return fromDisplay.slice(0, 10)
  const raw = view.etd
  if (raw == null || raw === '' || raw === t('common.emptyValue')) return t('common.emptyValue')
  return String(raw).slice(0, 10)
}

/** THI Lot: utamakan thi_line_ref (nomor lot marketing). */
function formatThiLot(row) {
  const thi = String(row?.thi_line_ref || '').trim()
  if (thi) return thi
  return t('common.emptyValue')
}

/** No Lot: system_reference, fallback thi_line_ref agar tidak kosong bila hanya THI terisi. */
function formatNoLot(row) {
  const sys = String(row?.system_reference || '').trim()
  if (sys) return sys
  const thi = String(row?.thi_line_ref || '').trim()
  if (thi) return thi
  return t('common.emptyValue')
}
</script>

<style scoped>
.po-detail-drawer__title {
  margin: 0;
  padding: 16px 0 16px 20px;
  font-size: 1.05rem;
  font-weight: 600;
  color: #0f172a;
}

.po-detail-drawer__body {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  padding: 16px 20px 24px;
}

.po-detail-drawer__footer {
  display: flex;
  justify-content: flex-end;
  padding: 12px 16px;
  background: #fff;
  border-top: 1px solid #e2e8f0;
}
</style>
