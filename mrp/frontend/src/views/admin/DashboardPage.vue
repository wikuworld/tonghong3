<template>
  <div class="space-y-5">
    <el-alert v-if="apiError" type="warning" :title="apiError" show-icon class="mb-2" />

    <el-card shadow="never" class="bg-gradient-to-br from-blue-50 to-blue-100 border-blue-200">
      <div class="flex flex-wrap items-center justify-between gap-3">
        <div>
          <div class="text-xl font-semibold text-slate-800">{{ t('dashboard.title') }}</div>
          <div class="mt-1 text-sm text-slate-500">{{ t('dashboard.subtitle') }}</div>
        </div>
        <el-button :icon="Refresh" :loading="loading" @click="reload">{{ t('common.refresh') }}</el-button>
      </div>
    </el-card>

    <el-row :gutter="12">
      <el-col v-for="card in cards" :key="card.key" :md="6" :sm="12" :xs="24">
        <el-card shadow="hover" class="mrp-dash-card" @click="go(card.path)">
          <div class="flex items-start justify-between">
            <div>
              <div class="text-xs font-medium uppercase tracking-wide text-slate-500">{{ card.label }}</div>
              <div class="mt-2 text-3xl font-semibold text-slate-800">{{ card.value }}</div>
              <div v-if="card.note" class="mt-2 text-xs text-slate-500">{{ card.note }}</div>
            </div>
            <el-icon class="rounded-lg p-2 text-white" :class="card.iconBg">
              <component :is="card.icon" />
            </el-icon>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="12">
      <el-col :md="12" :xs="24">
        <AdminSection :title="t('dashboard.recentRencana')">
          <el-table
            :data="summary.recent_rencana"
            v-loading="loading"
            border
            stripe
            size="small"
            class="admin-table"
            :empty-text="t('common.tableEmpty')"
            @row-click="openRencana"
          >
            <el-table-column type="index" width="48" :label="t('common.noLabel')" align="center" />
            <el-table-column prop="kode_rencana" :label="t('pages.mrpRencana.code')" min-width="130" show-overflow-tooltip />
            <el-table-column prop="nama_rencana" :label="t('pages.mrpRencana.name')" min-width="180" show-overflow-tooltip />
            <el-table-column prop="status" :label="t('common.status')" width="110">
              <template #default="{ row }">
                <el-tag size="small" :type="rencanaType(row.status)" effect="plain">{{ row.status || '-' }}</el-tag>
              </template>
            </el-table-column>
          </el-table>
        </AdminSection>
      </el-col>
      <el-col :md="12" :xs="24">
        <AdminSection :title="t('dashboard.recentPacking')">
          <el-table
            :data="summary.recent_packing"
            v-loading="loading"
            border
            stripe
            size="small"
            class="admin-table"
            :empty-text="t('common.tableEmpty')"
            @row-click="openPacking"
          >
            <el-table-column type="index" width="48" :label="t('common.noLabel')" align="center" />
            <el-table-column prop="kode_packing" :label="t('pages.mrpPacking.kodePacking')" min-width="130" show-overflow-tooltip />
            <el-table-column prop="customer" :label="t('common.customer')" min-width="160" show-overflow-tooltip />
            <el-table-column prop="status" :label="t('common.status')" width="120">
              <template #default="{ row }">
                <el-tag size="small" :type="row.status === 'finished' ? 'success' : 'warning'" effect="plain">
                  {{ row.status || '-' }}
                </el-tag>
              </template>
            </el-table-column>
          </el-table>
        </AdminSection>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { Box, CollectionTag, Document, Goods, Operation, Refresh } from '@element-plus/icons-vue'
import AdminSection from '../../components/AdminSection.vue'
import { dashboardSummary } from '../../api/client'

const { t } = useI18n()
const router = useRouter()
const loading = ref(false)
const apiError = ref('')
const summary = reactive({
  rencana_total: 0,
  rencana_active: 0,
  po_outstanding: 0,
  proses_open: 0,
  lab_lots: 0,
  packing_in_progress: 0,
  packing_finished: 0,
  fg_in_stock: 0,
  stok_kimia_lots: 0,
  stok_rp_lots: 0,
  recent_rencana: [],
  recent_packing: [],
})

const cards = computed(() => [
  {
    key: 'rencana',
    label: t('dashboard.rencanaActive'),
    value: summary.rencana_active,
    note: t('dashboard.rencanaHint', { n: summary.rencana_total }),
    path: '/admin/mrp/rencana-produksi',
    icon: Document,
    iconBg: 'bg-indigo-500',
  },
  {
    key: 'po',
    label: t('dashboard.poOutstanding'),
    value: summary.po_outstanding,
    path: '/admin/mrp/rencana-produksi',
    icon: Document,
    iconBg: 'bg-amber-500',
  },
  {
    key: 'proses',
    label: t('dashboard.prosesOpen'),
    value: summary.proses_open,
    path: '/admin/mrp/proses',
    icon: Operation,
    iconBg: 'bg-sky-500',
  },
  {
    key: 'lab',
    label: t('dashboard.labLots'),
    value: summary.lab_lots,
    path: '/admin/mrp/lab',
    icon: CollectionTag,
    iconBg: 'bg-violet-500',
  },
  {
    key: 'packing',
    label: t('dashboard.packingProgress'),
    value: summary.packing_in_progress,
    note: t('dashboard.packingFinishedHint', { n: summary.packing_finished }),
    path: '/admin/mrp/packing',
    icon: Box,
    iconBg: 'bg-emerald-500',
  },
  {
    key: 'fg',
    label: t('dashboard.fgInStock'),
    value: summary.fg_in_stock,
    path: '/admin/mrp/gudang-fg',
    icon: Goods,
    iconBg: 'bg-teal-500',
  },
  {
    key: 'kimia',
    label: t('dashboard.stokKimia'),
    value: summary.stok_kimia_lots,
    note: t('dashboard.stokKimiaHint'),
    path: '/admin/mrp/stok-kimia',
    icon: Goods,
    iconBg: 'bg-rose-500',
  },
  {
    key: 'rp',
    label: t('dashboard.stokRp'),
    value: summary.stok_rp_lots,
    note: t('dashboard.stokRpHint'),
    path: '/admin/mrp/stok-rp',
    icon: Goods,
    iconBg: 'bg-orange-500',
  },
])

function go(path) {
  if (path) router.push(path)
}

function openRencana() {
  router.push('/admin/mrp/rencana-produksi')
}

function openPacking(row) {
  if (row?.id) router.push(`/admin/mrp/packing/${row.id}`)
  else router.push('/admin/mrp/packing')
}

function rencanaType(status) {
  if (status === 'completed') return 'success'
  if (status === 'active') return 'primary'
  return 'info'
}

async function reload() {
  loading.value = true
  apiError.value = ''
  try {
    const data = await dashboardSummary()
    Object.assign(summary, {
      ...data,
      recent_rencana: data.recent_rencana || [],
      recent_packing: data.recent_packing || [],
    })
  } catch (e) {
    apiError.value = e.message || String(e)
  } finally {
    loading.value = false
  }
}

onMounted(reload)
</script>

<style scoped>
.mrp-dash-card {
  cursor: pointer;
  margin-bottom: 12px;
}
</style>
