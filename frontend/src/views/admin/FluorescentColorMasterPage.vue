<template>
  <AdminSection title="Master Fluorescent Color" subtitle="Referensi warna fluorescent/metallic per buyer dan season">
    <template #actions>
      <el-select v-model="filterBuyer" clearable filterable placeholder="Buyer" style="width: 170px">
        <el-option label="GLOBAL" value="GLOBAL" />
        <el-option label="NB" value="NB" />
        <el-option label="ADIDAS" value="ADIDAS" />
        <el-option label="UA" value="UA" />
        <el-option label="NIKE" value="NIKE" />
      </el-select>
      <el-select v-model="filterClass" clearable placeholder="Class" style="width: 150px">
        <el-option label="fluorescent" value="fluorescent" />
        <el-option label="metallic" value="metallic" />
      </el-select>
      <el-input v-model="keyword" clearable placeholder="Cari code/name/season" style="width: 260px" />
      <el-button :icon="Refresh" @click="reloadFromFirstPage">Refresh</el-button>
    </template>

    <div class="mb-3 flex items-center gap-2">
      <el-tag type="info">Total: {{ total }}</el-tag>
      <el-tag>GLOBAL: {{ summary.GLOBAL }}</el-tag>
      <el-tag>NB: {{ summary.NB }}</el-tag>
      <el-tag>ADIDAS: {{ summary.ADIDAS }}</el-tag>
      <el-tag>UA: {{ summary.UA }}</el-tag>
    </div>

    <el-table :data="rows" v-loading="loading" border stripe size="small" table-layout="fixed">
      <el-table-column type="index" label="No" width="56" align="center" />
      <el-table-column prop="buyer_code" label="Buyer" width="110" align="center" />
      <el-table-column prop="season_label" label="Season" min-width="130" />
      <el-table-column prop="season_year" label="Year" width="80" align="center" />
      <el-table-column prop="season_type" label="Type" width="80" align="center" />
      <el-table-column prop="color_code" label="Color Code" width="140" />
      <el-table-column prop="color_name" label="Color Name" min-width="220" show-overflow-tooltip />
      <el-table-column prop="color_class" label="Class" width="120" align="center" />
      <el-table-column prop="source_file" label="Source" min-width="150" show-overflow-tooltip />
    </el-table>
    <div class="mt-3 flex justify-end">
      <el-pagination
        v-model:current-page="page"
        v-model:page-size="pageSize"
        size="small"
        layout="total, sizes, prev, pager, next"
        :total="total"
        :page-sizes="[20, 50, 100, 200]"
      />
    </div>
  </AdminSection>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { Refresh } from '@element-plus/icons-vue'
import AdminSection from '../../components/AdminSection.vue'
import { listFluorescentColorsPage } from '../../api/client'

const loading = ref(false)
const rows = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)
const keyword = ref('')
const filterBuyer = ref('')
const filterClass = ref('')
const summary = ref({
  GLOBAL: 0,
  NB: 0,
  ADIDAS: 0,
  UA: 0,
})

async function loadSummary() {
  try {
    const [g, nb, adidas, ua] = await Promise.all([
      listFluorescentColorsPage({ buyer_code: 'GLOBAL', limit: 1, offset: 0 }),
      listFluorescentColorsPage({ buyer_code: 'NB', limit: 1, offset: 0 }),
      listFluorescentColorsPage({ buyer_code: 'ADIDAS', limit: 1, offset: 0 }),
      listFluorescentColorsPage({ buyer_code: 'UA', limit: 1, offset: 0 }),
    ])
    summary.value = {
      GLOBAL: Number(g?.total || 0),
      NB: Number(nb?.total || 0),
      ADIDAS: Number(adidas?.total || 0),
      UA: Number(ua?.total || 0),
    }
  } catch {
    summary.value = { GLOBAL: 0, NB: 0, ADIDAS: 0, UA: 0 }
  }
}

async function load() {
  loading.value = true
  try {
    const result = await listFluorescentColorsPage({
      buyer_code: filterBuyer.value || undefined,
      color_class: filterClass.value || undefined,
      q: keyword.value || undefined,
      limit: pageSize.value,
      offset: (page.value - 1) * pageSize.value,
    })
    rows.value = result.items || []
    total.value = Number(result.total || 0)
  } catch (e) {
    ElMessage.error(e.message || 'Gagal memuat master fluorescent.')
  } finally {
    loading.value = false
  }
}

function reloadFromFirstPage() {
  page.value = 1
  load()
}

watch([page, pageSize], () => {
  load()
})

watch([filterBuyer, filterClass, keyword], () => {
  page.value = 1
  load()
})

onMounted(load)
onMounted(loadSummary)
</script>

