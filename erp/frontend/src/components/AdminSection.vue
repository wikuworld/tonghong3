<template>
  <el-card shadow="never" class="admin-section-card">
    <template #header>
      <div class="admin-section-header">
        <div class="admin-section-title">
          <h2 class="text-lg font-semibold text-slate-800">{{ title }}</h2>
          <p v-if="subtitle" class="mt-0.5 text-sm text-slate-500">{{ subtitle }}</p>
        </div>
        <div class="admin-section-actions">
          <slot name="actions" />
        </div>
      </div>
    </template>
    <div class="admin-section-body">
      <slot />
    </div>
  </el-card>
</template>

<script setup>
defineProps({
  title: { type: String, required: true },
  subtitle: { type: String, default: '' },
})
</script>
