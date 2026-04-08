<template>
  <div class="min-h-screen bg-gray-100 p-6">
    <div class="mx-auto max-w-6xl overflow-hidden rounded-2xl bg-white shadow">
      <div class="bg-blue-700 px-6 py-4 text-white">
        <h1 class="text-lg font-semibold">Laporan PO – Order Description</h1>
        <p class="text-sm opacity-90">PT. Tong Hong Tannery Indonesia</p>
      </div>

      <div class="border-b p-6">
        <div class="grid grid-cols-1 items-end gap-4 md:grid-cols-5">
          <input type="date" class="w-full rounded-xl border p-2" />
          <input type="date" class="w-full rounded-xl border p-2" />
          <select class="rounded-xl border p-2"><option>All Customer</option></select>
          <select class="rounded-xl border p-2"><option>All Status</option></select>
          <button class="btn-blue w-full">Generate Report</button>
        </div>
      </div>

      <div class="space-y-8 p-6">
        <SectionTitle title="Revise Thickness" />
        <ReportTable :headers="reviseHeaders" :rows="reviseRows" :highlight-index="4" />

        <SectionTitle title="Production Order" />
        <ReportTable :headers="productionHeaders" :rows="productionRows" status />
        <div class="text-right font-semibold">Total Production Order: 7,835</div>

        <SectionTitle title="Sample" />
        <ReportTable :headers="sampleHeaders" :rows="sampleRows" sample />
        <div class="text-right font-semibold">Total Sample: 435</div>

        <div class="flex justify-end gap-3 pt-4">
          <button class="btn-gray">Export Excel</button>
          <button class="btn-blue">Print Report</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import ReportTable from '../components/ReportTable.vue'
import SectionTitle from '../components/SectionTitle.vue'

const reviseHeaders = ['PO No', 'Customer', 'Material', 'Old Thickness', 'New Thickness', 'Qty']
const reviseRows = [
  ['PO-0001', 'PT Customer', 'Split Suede', '1.2 - 1.4', '1.4 - 1.6', '500'],
  ['PO-0002', 'PT Customer', 'Split Suede', '1.2 - 1.4', '1.4 - 1.6', '500'],
]
const productionHeaders = ['PO No', 'Customer', 'Material', 'Color', 'Qty', 'Status']
const productionRows = [
  ['PO-1001', 'PT Customer', 'Split Suede', 'Black', '1200', 'Production'],
  ['PO-1002', 'PT Customer', 'Split Suede', 'Black', '1200', 'Production'],
  ['PO-1003', 'PT Customer', 'Split Suede', 'Black', '1200', 'Production'],
]
const sampleHeaders = ['PO No', 'Material', 'Color', 'Qty', 'Status']
const sampleRows = [
  ['SMP-2001', 'Split Suede', 'Grey', '250', 'Sample'],
  ['SMP-2002', 'Split Suede', 'Grey', '250', 'Sample'],
]
</script>

<style scoped>
.btn-blue { background: #2563eb; color: #fff; padding: 10px 16px; border-radius: 12px; }
.btn-gray { background: #d1d5db; padding: 10px 16px; border-radius: 12px; }
</style>
