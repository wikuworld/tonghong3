<template>
  <div class="out-col-head">
    <span class="out-col-head__title">{{ label }}</span>
    <el-select
      :model-value="normalizedValue"
      size="small"
      clearable
      filterable
      multiple
      collapse-tags
      collapse-tags-tooltip
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
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

const props = defineProps({
  label: { type: String, default: '' },
  /** Satu atau banyak nilai filter (string[]). String lama tetap didukung. */
  modelValue: { type: [Array, String], default: () => [] },
  options: { type: Array, default: () => [] },
})

const emit = defineEmits(['update:modelValue'])

const { t } = useI18n()

const normalizedValue = computed(() => {
  const v = props.modelValue
  if (Array.isArray(v)) return v.map((x) => String(x)).filter((x) => x !== '')
  if (v == null || v === '') return []
  return [String(v)]
})

function onUpdate(val) {
  if (val == null || val === '') {
    emit('update:modelValue', [])
    return
  }
  const list = Array.isArray(val) ? val : [val]
  emit(
    'update:modelValue',
    list.map((x) => String(x)).filter((x) => x !== ''),
  )
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
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.out-col-head__select {
  width: 100%;
}

.out-col-head__select :deep(.el-select__wrapper) {
  min-height: 24px;
  padding: 0 6px;
  font-size: 12px;
}

.out-col-head__select :deep(.el-tag) {
  max-width: 7rem;
}
</style>
