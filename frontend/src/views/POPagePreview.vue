<template>
  <div class="min-h-screen bg-gray-100 p-6">
    <div class="mx-auto max-w-5xl space-y-6 rounded-2xl bg-white p-6 shadow">
      <h1 class="text-2xl font-bold">Input PO to System</h1>

      <div class="grid grid-cols-1 gap-6 md:grid-cols-2">
        <div class="space-y-4">
          <Field label="Customer Code" v-model="form.customer_code" />
          <Field label="PO Number" v-model="form.po_number" />
          <div>
            <label class="text-sm text-gray-600">PO Category</label>
            <select v-model="form.po_category" class="w-full rounded-xl border p-2">
              <option value="production">Production</option>
              <option value="sample">Sample</option>
            </select>
          </div>
          <Field label="Buyer" v-model="form.buyer" />
          <Field label="Material Name" v-model="form.material_name" />
          <Field label="Thickness (e.g 1.2 - 1.4)" v-model="form.thickness" />
          <Field label="Color" v-model="form.color" />
        </div>

        <div class="space-y-4">
          <Field label="Softness" v-model="form.softness" />
          <Field label="Color Standard / Reference" v-model="form.color_reference" />
          <Field label="Backing" v-model="form.backing" />
          <Field label="Quantity Order" v-model="form.quantity" />
          <Field label="Style / Article" v-model="form.style" />
          <Field label="Model" v-model="form.model" />
          <Field label="ETD" type="date" v-model="form.etd" />
        </div>
      </div>

      <div>
        <label class="text-sm text-gray-600">Remark</label>
        <textarea v-model="form.remark" class="h-24 w-full rounded-xl border p-2" />
      </div>

      <div class="flex justify-end gap-3">
        <button class="rounded-xl bg-gray-200 px-4 py-2">Cancel</button>
        <button class="rounded-xl bg-blue-600 px-4 py-2 text-white">Save PO</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive } from 'vue'
import Field from '../components/InputField.vue'

const form = reactive({
  customer_code: '',
  po_number: '',
  po_category: 'production',
  buyer: '',
  material_name: '',
  thickness: '',
  color: '',
  softness: '',
  color_reference: '',
  backing: '',
  quantity: '',
  style: '',
  model: '',
  etd: '',
  remark: '',
})
</script>
