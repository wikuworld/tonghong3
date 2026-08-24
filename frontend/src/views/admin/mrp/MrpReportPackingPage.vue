<template>
  <AdminSection :title="t('pages.mrpReportPacking.title')" :subtitle="t('pages.mrpReportPacking.subtitle')">
    <template #actions>
      <el-button :icon="Refresh" :loading="loading" @click="reload">{{ t('common.refresh') }}</el-button>
    </template>
    <div class="admin-inner-card mb-4 flex flex-wrap gap-2 items-end">
      <el-date-picker v-model="range" type="daterange" value-format="YYYY-MM-DD" />
      <el-button type="primary" @click="reload">{{ t('common.search') }}</el-button>
      <span class="text-sm text-slate-500">Pack: {{ totals.pack }} · Lembar: {{ totals.lembar }} · Ukuran: {{ totals.ukuran }}</span>
    </div>
    <div class="admin-inner-card">
      <el-table :data="rows" v-loading="loading" border stripe size="small">
        <el-table-column prop="tanggal" :label="t('common.date')" width="120" />
        <el-table-column prop="no_po" :label="t('pages.mrpRencana.poCustomerRef')" min-width="120" />
        <el-table-column prop="no_so" :label="t('pages.mrpRencana.soRef')" min-width="120" />
        <el-table-column prop="kode_process" :label="t('pages.mrpPacking.kodePacking')" min-width="140" />
        <el-table-column prop="pack" label="Pack" width="80" />
        <el-table-column prop="qty" label="Lembar" width="90" />
        <el-table-column prop="size" label="Ukuran" width="90" />
        <el-table-column prop="status" :label="t('common.status')" width="110" />
      </el-table>
    </div>
  </AdminSection>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessage } from 'element-plus'
import { Refresh } from '@element-plus/icons-vue'
import AdminSection from '../../../components/AdminSection.vue'
import { mrpReportPacking } from '../../../api/client'

const { t } = useI18n()
const loading = ref(false)
const rows = ref([])
const today = new Date().toISOString().slice(0, 10)
const range = ref([today, today])
const totals = reactive({ pack: 0, lembar: 0, ukuran: 0 })

async function reload() {
  loading.value = true
  try {
    const [start_date, end_date] = range.value || [today, today]
    const data = await mrpReportPacking({ start_date, end_date })
    rows.value = data.rows || []
    totals.pack = data.total_all_pack || 0
    totals.lembar = data.total_all_lembar || 0
    totals.ukuran = data.total_all_ukuran || 0
  } catch (e) {
    ElMessage.error(e.message || String(e))
  } finally {
    loading.value = false
  }
}
onMounted(reload)
</script>
