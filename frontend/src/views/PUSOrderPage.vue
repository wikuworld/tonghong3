<template>
  <div class="min-h-screen bg-gray-100 p-6">
    <div class="mx-auto max-w-6xl overflow-hidden rounded-2xl bg-white shadow">
      <div class="flex justify-between bg-blue-600 px-6 py-4 text-white">
        <h1 class="text-lg font-semibold">PUS Order Maintenance</h1>
        <div>Order No: <b>Auto Generate</b></div>
      </div>

      <div class="space-y-6 p-6">
        <div class="grid grid-cols-1 gap-6 md:grid-cols-3">
          <Field label="Customer Code" v-model="form.customer_code" />
          <Field label="PO Customer" v-model="form.po_customer" />
          <div>
            <label class="text-sm">Order Category</label>
            <select v-model="form.order_category" class="w-full rounded-xl border p-2">
              <option value="production">Production</option>
              <option value="sample">Sample</option>
            </select>
          </div>
          <Field label="Buyer (Auto)" v-model="form.buyer" :disabled="true" />
          <Field label="Order Date" type="date" v-model="form.order_date" />
          <Field label="Update Date" type="date" v-model="form.update_date" />
        </div>

        <div>
          <h2 class="mb-4 text-lg font-semibold">Order Product Detail</h2>
          <div class="overflow-x-auto">
            <table class="w-full border text-sm">
              <thead class="bg-gray-200">
                <tr>
                  <th v-for="h in headers" :key="h" class="border p-2">{{ h }}</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(row, i) in details" :key="i">
                  <td v-for="key in keys" :key="key" class="border p-2">
                    <input
                      v-model="row[key]"
                      class="w-full rounded border p-1"
                    />
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <div class="flex justify-end gap-3">
          <button class="rounded-xl bg-gray-200 px-4 py-2">Cancel</button>
          <button class="rounded-xl bg-blue-600 px-4 py-2 text-white">Save</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive } from 'vue'
import Field from '../components/InputField.vue'

const form = reactive({
  customer_code: '',
  po_customer: '',
  order_category: 'production',
  buyer: '',
  order_date: '',
  update_date: '',
})

const details = reactive([
  { material: '', spec: '', thickness: '', color: '', softness: '', emboss: '', backing: '', qty: '' },
])

const headers = ['Material', 'Spec', 'Thickness', 'Color', 'Softness', 'Emboss', 'Backing', 'Qty']
const keys = ['material', 'spec', 'thickness', 'color', 'softness', 'emboss', 'backing', 'qty']
</script>
