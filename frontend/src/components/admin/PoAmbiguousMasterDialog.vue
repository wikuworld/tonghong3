<template>
  <el-dialog
    :model-value="modelValue"
    :title="t('pages.po.ambiguousMasterTitle')"
    width="520px"
    destroy-on-close
    append-to-body
    @update:model-value="$emit('update:modelValue', $event)"
  >
    <p class="text-sm text-slate-600 mb-3">{{ t('pages.po.ambiguousMasterHint') }}</p>
    <el-radio-group
      :model-value="selectedId"
      class="flex flex-col gap-2"
      @update:model-value="$emit('update:selectedId', $event)"
    >
      <el-radio v-for="c in candidates" :key="c.id" :value="c.id" class="!items-start !h-auto whitespace-normal">
        <span class="font-mono text-sm">{{ c.item_code }}</span>
        <span class="text-sm text-slate-700"> — {{ c.material_name || '—' }} / {{ c.thickness_range || c.thickness_mm || '—' }} / {{ c.color || '—' }} / {{ c.emboss || '—' }}</span>
      </el-radio>
    </el-radio-group>
    <template #footer>
      <el-button @click="$emit('update:modelValue', false)">{{ t('common.cancel') }}</el-button>
      <el-button type="primary" :disabled="!selectedId" @click="$emit('confirm')">
        {{ t('common.confirm') }}
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { useI18n } from 'vue-i18n'

defineProps({
  modelValue: { type: Boolean, default: false },
  candidates: { type: Array, default: () => [] },
  selectedId: { type: [Number, String, null], default: null },
})

defineEmits(['update:modelValue', 'update:selectedId', 'confirm'])

const { t } = useI18n()
</script>
