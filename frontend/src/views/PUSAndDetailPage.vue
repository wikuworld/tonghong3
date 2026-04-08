<template>
  <div class="space-y-4 p-4">
    <div class="flex gap-2">
      <button class="rounded bg-gray-200 px-3 py-2" @click="page = 'pus'">PUS</button>
      <button class="rounded bg-gray-200 px-3 py-2" @click="page = 'detail'">DETAIL</button>
    </div>
    <PUSOrderPage v-if="page === 'pus'" />
    <OrderDetailPage v-else />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import PUSOrderPage from './PUSOrderPage.vue'
import OrderDetailPage from './OrderDetailPage.vue'

const page = ref('pus')
</script>
