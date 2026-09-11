<template>
  <AdminSection :title="t('pages.mrpReportPacking.title')" :subtitle="t('pages.mrpReportPacking.subtitle')">
    <template #actions>
      <span v-if="loading" class="text-xs text-slate-500">{{ t('common.loadingData') }}</span>
      <el-button :icon="Refresh" :loading="loading" @click="reload">{{ t('common.refresh') }}</el-button>
    </template>

    <div class="admin-inner-card">
      <div class="admin-inner-card__head">
        <div>
          <h3 class="admin-inner-card__title">{{ t('pages.mrpReportPacking.listSectionTitle') }}</h3>
          <p class="admin-inner-card__sub">{{ t('pages.mrpReportPacking.listSubtitle') }}</p>
        </div>
      </div>
      <div class="mkt-section-body">
        <div class="filter-panel mb-4">
          <p class="filter-panel__title">{{ t('pages.mrpReportPacking.filterTitle') }}</p>
          <el-form class="filter-form" label-position="top">
            <el-row :gutter="12">
              <el-col :xs="24" :sm="12" :md="10" :lg="8">
                <el-form-item :label="t('pages.mrpReportPacking.dateRange')">
                  <el-date-picker v-model="range" type="daterange" value-format="YYYY-MM-DD" class="w-full" />
                </el-form-item>
              </el-col>
              <el-col :xs="24" :sm="8" :md="4" :lg="3">
                <el-form-item label="&nbsp;">
                  <el-button class="w-full" type="primary" @click="reload">{{ t('common.search') }}</el-button>
                </el-form-item>
              </el-col>
            </el-row>
          </el-form>
        </div>

        <div class="admin-stats-grid admin-stats-grid--3 mb-4">
          <div class="admin-stat-card admin-stat-card--info">
            <span class="admin-stat-card__value">{{ totals.pack }}</span>
            <span class="admin-stat-card__label">{{ t('pages.mrpReportPacking.totalPack') }}</span>
          </div>
          <div class="admin-stat-card">
            <span class="admin-stat-card__value">{{ totals.lembar }}</span>
            <span class="admin-stat-card__label">{{ t('pages.mrpReportPacking.totalLembar') }}</span>
          </div>
          <div class="admin-stat-card admin-stat-card--success">
            <span class="admin-stat-card__value">{{ totals.ukuran }}</span>
            <span class="admin-stat-card__label">{{ t('pages.mrpReportPacking.totalUkuran') }}</span>
          </div>
        </div>

        <p class="admin-scroll-hint">{{ t('pages.mrpReportPacking.scrollHint') }}</p>
        <div class="admin-table-scroll">
          <el-table :data="rows" v-loading="loading" border stripe size="small" class="admin-table" :empty-text="t('pages.mrpReportPacking.tableEmpty')">
            <el-table-column prop="tanggal" :label="t('common.date')" width="120" />
            <el-table-column prop="no_po" :label="t('pages.mrpRencana.poCustomerRef')" min-width="120" />
            <el-table-column prop="no_so" :label="t('pages.mrpRencana.soRef')" min-width="120" />
            <el-table-column prop="kode_process" :label="t('pages.mrpPacking.kodePacking')" min-width="140" />
            <el-table-column prop="pack" :label="t('pages.mrpReportPacking.pack')" width="80" />
            <el-table-column prop="qty" :label="t('pages.mrpReportPacking.lembar')" width="90" />
            <el-table-column prop="size" :label="t('pages.mrpReportPacking.ukuran')" width="90" />
            <el-table-column prop="status" :label="t('common.status')" width="110" />
          </el-table>
        </div>
      </div>
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
