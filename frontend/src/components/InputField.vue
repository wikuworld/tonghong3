<template>
  <div class="flex flex-col gap-1">
    <label class="text-sm text-gray-600">{{ label }}</label>
    <input
      :type="type"
      :disabled="disabled"
      :placeholder="placeholder || label"
      :value="modelValue"
      class="w-full rounded-xl border bg-white p-2 disabled:bg-gray-100"
      @input="$emit('update:modelValue', $event.target.value)"
    />
  </div>
</template>

<script setup>
defineProps({
  label: { type: String, default: '' },
  modelValue: { type: [String, Number], default: '' },
  type: { type: String, default: 'text' },
  disabled: { type: Boolean, default: false },
  placeholder: { type: String, default: '' },
})

defineEmits(['update:modelValue'])
</script>
