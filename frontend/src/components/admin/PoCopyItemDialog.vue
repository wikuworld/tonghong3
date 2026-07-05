<template>
  <el-dialog
    :model-value="modelValue"
    :title="t('pages.po.copyItemFromOtherPo')"
    width="95%" style="max-width: 900px"
    destroy-on-close
    align-center
    @update:model-value="$emit('update:modelValue', $event)"
  >
    <el-form label-position="top">
      <el-row :gutter="12">
        <el-col :xs="24" :md="12">
          <el-form-item :label="t('common.customer')">
            <el-select
              :model-value="customerId"
              clearable
              filterable
              class="w-full"
              :placeholder="t('common.placeholder.customer')"
              @update:model-value="$emit('update:customerId', $event)"
            >
              <el-option
                v-for="c in customers"
                :key="c.id"
                :label="formatCustomerOption(c)"
                :value="c.id"
              />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :xs="24" :md="12">
          <el-form-item :label="t('common.placeholder.search')">
            <el-input
              :model-value="search"
              clearable
              :placeholder="t('pages.po.searchItems')"
              @update:model-value="$emit('update:search', $event)"
            />
          </el-form-item>
        </el-col>
      </el-row>
    </el-form>

    <el-table
      v-if="sourceItems.length"
      :data="filteredItems"
      border
      size="small"
      max-height="350"
      @selection-change="$emit('selection-change', $event)"
    >
      <el-table-column type="selection" width="55" />
      <el-table-column prop="source_po_number" :label="t('common.poNo')" width="140" />
      <el-table-column prop="material_name" :label="t('common.material')" min-width="160" show-overflow-tooltip />
      <el-table-column prop="thickness_text" :label="t('common.thickness')" width="90" />
      <el-table-column prop="color" :label="t('common.color')" width="90" />
      <el-table-column prop="quantity_order" :label="t('common.quantityOrder')" width="100" align="right" />
      <el-table-column prop="unit_price" :label="t('pages.po.unitPriceUsd')" width="100" align="right">
        <template #default="{ row }">{{ row.unit_price != null ? row.unit_price : '—' }}</template>
      </el-table-column>
    </el-table>
    <div v-else-if="!customerId" class="text-center text-slate-500 py-8">
      {{ t('pages.po.selectCustomerToSeeItems') }}
    </div>
    <div v-else class="text-center text-slate-500 py-8">
      {{ t('pages.po.noItemsFound') }}
    </div>
    <div v-if="filteredItems.length" class="mt-2 text-xs text-slate-500">
      {{ t('pages.po.showingItems', { count: filteredItems.length }) }}
    </div>
    <template #footer>
      <div class="po-dialog-footer">
        <el-button :icon="Close" @click="$emit('update:modelValue', false)">{{ t('common.cancel') }}</el-button>
        <el-button type="primary" :icon="Check" :disabled="!selectedCount" @click="$emit('add-selected')">
          {{ t('pages.po.addSelectedItems') }} ({{ selectedCount }})
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup>
import { Check, Close } from '@element-plus/icons-vue'
import { useI18n } from 'vue-i18n'

defineProps({
  modelValue: { type: Boolean, default: false },
  customers: { type: Array, default: () => [] },
  customerId: { type: [Number, String, null], default: null },
  search: { type: String, default: '' },
  sourceItems: { type: Array, default: () => [] },
  filteredItems: { type: Array, default: () => [] },
  selectedCount: { type: Number, default: 0 },
  formatCustomerOption: { type: Function, required: true },
})

defineEmits([
  'update:modelValue',
  'update:customerId',
  'update:search',
  'selection-change',
  'add-selected',
])

const { t } = useI18n()
</script>
