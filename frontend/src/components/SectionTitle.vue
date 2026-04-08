<template>
  <h2 class="font-semibold text-gray-700">{{ title }}</h2>
</template>

<script setup>
defineProps({
  title: { type: String, required: true },
})
</script>
