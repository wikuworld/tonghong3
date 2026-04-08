<template>
  <AdminSection :title="t('pages.printSuratJalan.title')" :subtitle="t('pages.printSuratJalan.subtitle')">
    <div class="mb-4 flex justify-end">
      <el-button type="primary" @click="printPage">{{ t('common.print') }}</el-button>
    </div>

    <div class="print-sheet">
      <div class="text-center leading-tight">
        <h1 class="text-xl font-bold">PT. TONG HONG TANNERY INDONESIA</h1>
        <p>Kawasan Industri Modern II Jl. Modern Industri XIV-1 Ds. Barengkok Kec. Kibin Serang-Banten</p>
        <p>Telp. 0254-8480870 Fax. 0254-8480743</p>
        <h2 class="mt-4 font-semibold">SURAT JALAN (DELIVERY SHEET)</h2>
      </div>

      <el-divider />

      <el-row :gutter="24">
        <el-col :xs="24" :md="12">
          <p><b>Delivered To:</b> PT. HARDASES ABADI INDONESIA</p>
          <p><b>Address:</b> Jl. Raya Wangandowo, Pekalongan</p>
          <p><b>Telp No:</b> 0877-6553-7707</p>
          <p><b>P.O No:</b> 5500002436-FOC</p>
          <p><b>Inv No:</b> THIN-C26026001</p>
        </el-col>
        <el-col :xs="24" :md="12">
          <p><b>Surat Jalan No:</b> THI-C26026001</p>
          <p><b>Date:</b> Feb 06, 2026</p>
          <p><b>Car No:</b> B 1234 CD</p>
          <p><b>Driver's Name:</b> Ahmad</p>
          <p><b>Page:</b> 1</p>
        </el-col>
      </el-row>

      <el-table :data="rows" border class="mt-5" size="small">
        <el-table-column prop="no" :label="t('common.noLabel')" width="60" />
        <el-table-column prop="material" :label="t('common.material')" min-width="220" />
        <el-table-column prop="thickness" :label="t('common.thickness')" min-width="120" />
        <el-table-column prop="color" :label="t('common.color')" min-width="130" />
        <el-table-column prop="qty" :label="t('common.quantity')" min-width="130" align="right" />
        <el-table-column prop="roll" :label="t('common.roll')" min-width="80" align="center" />
        <el-table-column prop="pcs" :label="t('common.pieces')" min-width="80" align="center" />
      </el-table>
    </div>
  </AdminSection>
</template>

<script setup>
import { reactive } from 'vue'
import { useI18n } from 'vue-i18n'
import AdminSection from '../../components/AdminSection.vue'

const { t } = useI18n()

const rows = reactive([
  { no: 1, material: 'SPLIT SUEDE (MAP-SPLIT SUEDE)', thickness: '1.2-1.4', color: 'GREY ONE (AA2R)', qty: 327.8, roll: 2, pcs: 15 },
])

const printPage = () => window.print()
</script>

<style scoped>
.print-sheet {
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 24px;
}
</style>
