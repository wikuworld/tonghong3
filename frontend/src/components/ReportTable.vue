<template>
  <table class="w-full border text-sm">
    <thead class="bg-gray-200">
      <tr>
        <th v-for="h in headers" :key="h" class="border p-2 text-left">{{ h }}</th>
      </tr>
    </thead>
    <tbody>
      <tr v-for="(row, rowIndex) in rows" :key="rowIndex">
        <td
          v-for="(cell, colIndex) in row"
          :key="colIndex"
          class="border p-2"
          :class="cellClass(colIndex)"
        >
          {{ cell }}
        </td>
      </tr>
    </tbody>
  </table>
</template>

<script setup>
const props = defineProps({
  headers: { type: Array, required: true },
  rows: { type: Array, required: true },
  highlightIndex: { type: Number, default: -1 },
  status: { type: Boolean, default: false },
  sample: { type: Boolean, default: false },
})

const cellClass = (index) => {
  if (props.highlightIndex === index) return 'font-medium text-orange-500'
  if (props.status && index === 5) return 'font-medium text-green-600'
  if (props.sample && index === 4) return 'font-medium text-blue-600'
  return ''
}
</script>
