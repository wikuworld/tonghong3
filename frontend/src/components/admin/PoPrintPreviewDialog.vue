<template>
  <el-dialog
    :model-value="modelValue"
    :title="`${t('common.print')} ${t('menu.po')}`"
    width="760px"
    destroy-on-close
    align-center
    class="po-dialog"
    @update:model-value="$emit('update:modelValue', $event)"
  >
    <div v-if="row" class="rounded border border-slate-200 p-4">
      <h3 class="mb-2 text-lg font-semibold">{{ row.po_number }}</h3>
      <p><b>{{ t('common.customer') }}:</b> {{ row.customerName }}</p>
      <p><b>{{ t('common.buyer') }}:</b> {{ row.buyer }}</p>
      <p><b>{{ t('common.poCategory') }}:</b> {{ statusLabel(row.po_category) }}</p>
      <p><b>{{ t('common.material') }}:</b> {{ row.material_hint }}</p>
      <p><b>{{ t('common.etd') }}:</b> {{ row.etd }}</p>
    </div>
    <template #footer>
      <div class="po-dialog-footer">
        <el-button :icon="Close" @click="$emit('update:modelValue', false)">{{ t('common.cancel') }}</el-button>
        <el-button type="primary" :icon="Printer" @click="$emit('print')">{{ t('common.print') }}</el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup>
import { Close, Printer } from '@element-plus/icons-vue'
import { useI18n } from 'vue-i18n'

import { statusLabel } from '../../utils/format'

defineProps({
  modelValue: { type: Boolean, default: false },
  row: { type: Object, default: null },
})

defineEmits(['update:modelValue', 'print'])

const { t } = useI18n()
</script>
