<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

const props = defineProps({
  row: { type: Object, default: null },
  /** Compact bullet-only (default). Set false to show short text tag. */
  bulletOnly: { type: Boolean, default: true },
})

const { t } = useI18n()

const visible = computed(() => {
  const r = props.row
  if (!r) return false
  return Boolean(r.item_revised_at || r.item_revised_has_update || r.item_revised_has_delete)
})

const tip = computed(() => {
  const r = props.row || {}
  const hasU = Boolean(r.item_revised_has_update)
  const hasD = Boolean(r.item_revised_has_delete)
  if (hasU && hasD) return t('pages.po.itemRevisedTipBoth')
  if (hasD) return t('pages.po.itemRevisedTipDelete')
  if (hasU) return t('pages.po.itemRevisedTipUpdate')
  return t('pages.po.itemRevisedTipUpdate')
})
</script>

<template>
  <el-tooltip v-if="visible" :content="tip" placement="top">
    <span
      class="po-item-revised"
      :class="{ 'po-item-revised--bullet': bulletOnly }"
      role="img"
      :aria-label="tip"
    >
      <span class="po-item-revised__dot" aria-hidden="true" />
      <span v-if="!bulletOnly" class="po-item-revised__label">{{ t('pages.po.itemRevisedShort') }}</span>
    </span>
  </el-tooltip>
</template>

<style scoped>
.po-item-revised {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  vertical-align: middle;
  cursor: help;
  line-height: 1;
}

.po-item-revised__dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #dc2626;
  box-shadow: 0 0 0 2px rgba(220, 38, 38, 0.2);
  flex-shrink: 0;
}

.po-item-revised__label {
  font-size: 11px;
  font-weight: 700;
  color: #b91c1c;
  letter-spacing: 0.02em;
  text-transform: uppercase;
}
</style>
