<template>
  <div class="min-h-screen bg-gray-100 p-6">
    <div class="mx-auto max-w-6xl overflow-hidden rounded-2xl bg-white shadow">
      <div class="flex justify-between bg-blue-600 px-6 py-4 text-white">
        <h1 class="text-lg font-semibold">Order Detail After Input</h1>
        <div>Lot No: <b>Auto Generate</b></div>
      </div>
      <div class="space-y-6 p-6">
        <div class="grid grid-cols-1 gap-6 md:grid-cols-3">
          <Field label="Buyer" v-model="form.buyer" />
          <Field label="Material Name" v-model="form.material" />
          <Field label="Thickness" v-model="form.thickness" />
          <div>
            <label class="text-sm">Color</label>
            <select v-model="form.color" class="w-full rounded-xl border p-2">
              <option>Black</option>
              <option>Grey</option>
            </select>
          </div>
          <Field label="Softness" v-model="form.softness" :disabled="true" />
          <Field label="Emboss" v-model="form.emboss" />
          <Field label="Color Standard" v-model="form.color_standard" />
          <Field label="Backing" v-model="form.backing" />
          <Field label="Quantity" v-model="form.quantity" />
          <Field label="Style" v-model="form.style" />
          <Field label="Model" v-model="form.model" />
          <Field label="ETD" type="date" v-model="form.etd" />
        </div>
        <div>
          <label class="text-sm">Remark</label>
          <textarea v-model="form.remark" class="h-24 w-full rounded-xl border p-2" />
        </div>
        <div class="flex justify-end gap-3">
          <button class="rounded-xl bg-gray-200 px-4 py-2">Cancel</button>
          <button class="rounded-xl bg-blue-600 px-4 py-2 text-white">Confirm</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive } from 'vue'
import Field from '../components/InputField.vue'

const form = reactive({
  buyer: '',
  material: '',
  thickness: '1.2 - 1.4',
  color: 'Black',
  softness: 'Auto by buyer',
  emboss: '',
  color_standard: '',
  backing: '',
  quantity: '',
  style: '',
  model: '',
  etd: '',
  remark: '',
})
</script>
