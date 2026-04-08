<template>
  <div class="min-h-screen bg-gray-100 p-6">
    <div class="mx-auto max-w-6xl overflow-hidden rounded-2xl bg-white shadow">
      <div class="flex gap-3 bg-gray-100 p-4">
        <button class="btn-top">F7 Query</button>
        <button class="btn-top">F2 New</button>
        <button class="btn-top">F9 Export</button>
        <button class="btn-top">F6 Close</button>
      </div>

      <div class="bg-blue-600 px-6 py-4 text-white">
        <h1 class="font-semibold">B-25 – Tarik C/R (Delivery List)</h1>
      </div>

      <div class="space-y-6 p-6">
        <div class="grid grid-cols-1 gap-6 md:grid-cols-4">
          <Field label="Customer" v-model="filter.customer" />
          <Field label="Order No" v-model="filter.order_no" />
          <Field label="From Date" type="date" v-model="filter.from_date" />
          <Field label="To Date" type="date" v-model="filter.to_date" />
        </div>

        <div class="flex gap-4">
          <button class="btn-blue">Search</button>
          <button class="btn-green">Tarik C/R</button>
        </div>

        <div class="overflow-x-auto">
          <table class="w-full border text-sm">
            <thead class="bg-gray-200">
              <tr>
                <th v-for="h in headers" :key="h" class="border p-2">{{ h }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="r in rows" :key="r.no">
                <td class="border p-2">{{ r.no }}</td>
                <td class="border p-2">{{ r.sj }}</td>
                <td class="border p-2">{{ r.customer }}</td>
                <td class="border p-2">{{ r.material }}</td>
                <td class="border p-2">{{ r.thickness }}</td>
                <td class="border p-2">{{ r.color }}</td>
                <td class="border p-2">{{ r.qty }}</td>
                <td class="border p-2">{{ r.roll }}</td>
                <td class="border p-2">{{ r.pcs }}</td>
                <td class="border p-2 text-center">
                  <button class="btn-select">Select</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <div class="flex items-center justify-between pt-6">
          <span class="text-sm text-gray-500">Setting tanggal hari ini sebelum tarik C/R</span>
          <div class="flex gap-3">
            <button class="btn-gray">Cancel</button>
            <button class="btn-blue">Confirm Tarik C/R</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive } from 'vue'
import Field from '../components/InputField.vue'

const filter = reactive({ customer: '', order_no: '', from_date: '', to_date: '' })
const headers = ['No', 'SJ No', 'Customer', 'Material', 'Thickness', 'Color', 'Qty', 'Roll', 'Pcs', 'Action']
const rows = [
  { no: 1, sj: 'THI-M26026001', customer: 'PT. CUSTOMER', material: 'Split Suede', thickness: '1.2 - 1.4', color: 'Grey', qty: 327.8, roll: 2, pcs: 15 },
  { no: 2, sj: 'THI-M26026002', customer: 'PT. CUSTOMER', material: 'Split Suede', thickness: '1.2 - 1.4', color: 'Grey', qty: 327.8, roll: 2, pcs: 15 },
  { no: 3, sj: 'THI-M26026003', customer: 'PT. CUSTOMER', material: 'Split Suede', thickness: '1.2 - 1.4', color: 'Grey', qty: 327.8, roll: 2, pcs: 15 },
]
</script>

<style scoped>
.btn-top { background: #eee; padding: 8px 12px; border-radius: 8px; }
.btn-blue { background: #2563eb; color: #fff; padding: 10px 16px; border-radius: 12px; }
.btn-green { background: #16a34a; color: #fff; padding: 10px 16px; border-radius: 12px; }
.btn-gray { background: #ccc; padding: 10px 16px; border-radius: 12px; }
.btn-select { background: #3b82f6; color: #fff; padding: 4px 10px; border-radius: 8px; }
</style>
