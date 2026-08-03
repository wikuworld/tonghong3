<template>
  <div class="out-col-head">
    <span class="out-col-head__title">{{ label }}</span>
    <el-select
      :model-value="modelValue || undefined"
      size="small"
      clearable
      filterable
      allow-create
      default-first-option
      class="out-col-head__select"
      :placeholder="t('pages.marketingFlow.colFilterPlaceholder')"
      @update:model-value="onUpdate"
      @click.stop
      @mousedown.stop
    >
      <el-option
        v-for="opt in options"
        :key="opt"
        :label="opt"
        :value="opt"
      />
    </el-select>
  </div>
</template>

<script setup>
import { useI18n } from 'vue-i18n'

defineProps({
  label: { type: String, default: '' },
  modelValue: { type: String, default: '' },
  options: { type: Array, default: () => [] },
})

const emit = defineEmits(['update:modelValue'])

const { t } = useI18n()

function onUpdate(val) {
  emit('update:modelValue', val == null ? '' : String(val))
}
</script>

<style scoped>
.out-col-head {
  display: flex;
  flex-direction: column;
  gap: 4px;
  line-height: 1.25;
  width: 100%;
}

.out-col-head__title {
  font-weight: 600;
  font-size: 12px;
  color: #334155;
  white-space: normal;
}

.out-col-head__select {
  width: 100%;
}

.out-col-head__select :deep(.el-select__wrapper) {
  min-height: 24px;
  padding: 0 6px;
  font-size: 12px;
}
</style>
