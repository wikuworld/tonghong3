<template>
  <div class="min-h-screen bg-gray-100 p-6">
    <div class="mx-auto max-w-7xl overflow-hidden rounded-2xl bg-white shadow">
      <div class="flex gap-3 border-b bg-gray-100 p-4">
        <button class="btn-top">F7 Query</button>
        <button class="btn-top">F2 New</button>
        <button class="btn-top">F10 Save</button>
        <button class="btn-top">F9 Print</button>
        <button class="btn-top">F6 Close</button>
      </div>

      <div class="flex items-center justify-between bg-blue-700 px-6 py-4 text-white">
        <h1 class="text-lg font-semibold">Input Surat Jalan (PU Delivery Note)</h1>
        <div class="text-sm">No SJ: <b>THI-M26026001</b></div>
      </div>

      <div class="space-y-6 p-6">
        <div class="grid grid-cols-1 gap-6 md:grid-cols-4">
          <Field label="Factory Code" v-model="form.factory" :disabled="true" />
          <Field label="Customer Name" v-model="form.customer" />
          <Field label="Delivery Date" type="date" v-model="form.delivery_date" />
          <div>
            <label class="text-sm text-gray-600">Delivery Type</label>
            <select v-model="form.delivery_type" class="w-full rounded-xl border p-2">
              <option>Production</option>
              <option>Sample</option>
            </select>
          </div>
          <div>
            <label class="text-sm text-gray-600">Warehouse</label>
            <select v-model="form.warehouse" class="w-full rounded-xl border p-2">
              <option>Finished Goods</option>
            </select>
          </div>
          <Field label="Vehicle No" v-model="form.vehicle" />
          <Field label="Driver Name" v-model="form.driver" />
          <Field label="Remark" v-model="form.remark" />
        </div>

        <div class="overflow-x-auto">
          <table class="w-full border text-sm">
            <thead class="bg-gray-200">
              <tr>
                <th v-for="h in headers" :key="h" class="border p-2 text-left">{{ h }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="r in rows" :key="r.no">
                <td class="border p-2">{{ r.no }}</td>
                <td class="border p-2">{{ r.order_no }}</td>
                <td class="border p-2">{{ r.material }}</td>
                <td class="border p-2">{{ r.thickness }}</td>
                <td class="border p-2">{{ r.color }}</td>
                <td class="border p-2">{{ r.order_qty }}</td>
                <td class="border p-2 font-medium">{{ r.delivered_qty }}</td>
                <td class="border p-2">{{ r.roll }}</td>
                <td class="border p-2">{{ r.pcs }}</td>
              </tr>
            </tbody>
          </table>
        </div>

        <div class="flex justify-end gap-4 pt-4">
          <button class="btn-gray">Cancel</button>
          <button class="btn-blue">Save Surat Jalan</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive } from 'vue'
import Field from '../components/InputField.vue'

const form = reactive({
  factory: 'SD047',
  customer: '',
  delivery_date: '',
  delivery_type: 'Production',
  warehouse: 'Finished Goods',
  vehicle: '',
  driver: '',
  remark: '',
})

const headers = ['No', 'Order No', 'Material', 'Thickness', 'Color', 'Order Qty', 'Delivered Qty', 'Roll', 'Pcs']
const rows = [
  {
    no: 1,
    order_no: 'PS25122909',
    material: 'Split Suede',
    thickness: '1.2 - 1.4',
    color: 'Grey One',
    order_qty: 28639,
    delivered_qty: 4137.6,
    roll: 2,
    pcs: 15,
  },
]
</script>

<style scoped>
.btn-top { background: #f1f1f1; padding: 8px 12px; border-radius: 8px; }
.btn-blue { background: #2563eb; color: #fff; padding: 10px 18px; border-radius: 14px; }
.btn-gray { background: #d1d5db; padding: 10px 18px; border-radius: 14px; }
</style>
