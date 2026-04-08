<template>
  <div class="min-h-screen bg-gray-100 p-6">
    <div class="mx-auto max-w-5xl bg-white p-10 text-sm shadow">
      <div class="text-center leading-tight">
        <h1 class="text-xl font-bold">PT. TONG HONG TANNERY INDONESIA</h1>
        <p>Kawasan Industri Modern II Jl. Modern Industri XIV-1 Ds. Barengkok Kec. Kibin Serang-Banten</p>
        <p>Telp. 0254-8480870 Fax. 0254-8480743</p>
        <h2 class="mt-4 font-semibold">SURAT JALAN (DELIVERY SHEET)</h2>
      </div>

      <div class="my-6 border-t" />

      <div class="grid grid-cols-1 gap-10 md:grid-cols-2">
        <div class="space-y-1">
          <p><b>Delivered To :</b> PT. HARDASES ABADI INDONESIA</p>
          <p><b>Address :</b> Jl. Raya Wangandowo, Pekalongan</p>
          <p><b>Telp No :</b> 0877-6553-7707</p>
          <p><b>P.O No :</b> 5500002436-FOC</p>
          <p><b>Inv No :</b> THIN-C26026001</p>
        </div>
        <div class="space-y-1">
          <p><b>Surat Jalan No :</b> THI-C26026001</p>
          <p><b>Date :</b> Feb 06, 2026</p>
          <p><b>Car No :</b> B 1234 CD</p>
          <p><b>Driver's Name :</b> Ahmad</p>
          <p><b>Page :</b> 1</p>
        </div>
      </div>

      <table class="mt-8 w-full border text-sm">
        <thead class="bg-gray-200">
          <tr>
            <th class="w-10 border p-2">No</th>
            <th class="border p-2">Material Name</th>
            <th class="border p-2">Thickness (MM)</th>
            <th class="border p-2">Color</th>
            <th class="border p-2">Quantity (S/F)</th>
            <th class="border p-2">Rolls</th>
            <th class="border p-2">Pieces</th>
            <th class="border p-2">Remark</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td class="border p-2 text-center">1</td>
            <td class="border p-2">SPLIT SUEDE (MAP-SPLIT SUEDE)</td>
            <td class="border p-2 text-center">1.2-1.4</td>
            <td class="border p-2">GREY ONE (AA2R)</td>
            <td class="border p-2 text-right">327.80</td>
            <td class="border p-2 text-center">2</td>
            <td class="border p-2 text-center">15</td>
            <td class="border p-2" />
          </tr>
          <tr>
            <td colspan="4" class="border p-2 font-semibold">Total</td>
            <td class="border p-2 text-right font-semibold">327.80</td>
            <td class="border p-2 text-center">2</td>
            <td class="border p-2 text-center">15</td>
            <td class="border p-2" />
          </tr>
        </tbody>
      </table>

      <div class="mt-20 grid grid-cols-2 gap-10 text-center md:grid-cols-4">
        <div v-for="title in signatures" :key="title">
          <p class="mb-12">{{ title }}</p>
          <div class="border-b" />
          <p class="mt-2">( )</p>
        </div>
      </div>

      <p class="mt-12 text-xs">
        Note: WHITE(1) ACC, RED(2) CUSTOMER, YELLOW(3) EXIM, GREEN(4) WAREHOUSE, BLUE(5) SECURITY
      </p>
    </div>
  </div>
</template>

<script setup>
const signatures = ['Received By', 'Approved By', 'Security', 'Delivered By']
</script>
