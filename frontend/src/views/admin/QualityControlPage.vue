<template>
  <AdminSection :title="t('pages.qc.title')" :subtitle="t('pages.qc.subtitle')">
    <template #actions>
      <el-input
        v-model="keyword"
        :placeholder="t('pages.qc.searchPlaceholder')"
        clearable
        class="qc-toolbar-search"
      />
    </template>

    <el-alert class="mb-3" type="info" :closable="false" show-icon>
      <template #title>
        <span>{{ t('pages.qc.bookHint') }}</span>
        <router-link class="ml-2 text-primary underline" to="/admin/mrp/checkpoint">
          {{ t('pages.qc.openMrpCheckpoint') }}
        </router-link>
      </template>
    </el-alert>

    <div class="mb-3">
      <el-switch v-model="filterMrpOnly" :active-text="t('pages.qc.filterMrpOnly')" />
    </div>

    <el-table :data="filteredRows" v-loading="loading" border stripe size="small" class="admin-table" table-layout="fixed" :empty-text="t('pages.qc.tableEmpty')">
      <el-table-column type="index" :label="t('common.noLabel')" width="56" align="center" />
      <el-table-column prop="qc_number" :label="t('common.qcNo')" min-width="130">
        <template #default="{ row }">
          <span>{{ row.qc_number }}</span>
          <el-tag v-if="isMrpBook(row)" size="small" type="warning" class="ml-1">{{ t('pages.qc.mrpBadge') }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="production_label" :label="t('common.productionNo')" min-width="160" show-overflow-tooltip />
      <el-table-column prop="qc_date" :label="t('common.date')" width="120" />
      <el-table-column :label="t('common.result')" width="100" align="center">
        <template #default="{ row }">
          <el-tag v-if="row.sample_result" :type="row.sample_result === 'ok' ? 'success' : 'danger'" size="small">
            {{ row.sample_result === 'ok' ? t('status.ok') : t('status.ng') }}
          </el-tag>
          <span v-else>{{ t('common.emptyValue') }}</span>
        </template>
      </el-table-column>
      <el-table-column :label="t('common.actions')" width="90" align="center" fixed="right">
        <template #default="{ row }">
          <el-tooltip :content="t('common.detail')" placement="top">
            <el-button :icon="View" link type="primary" :aria-label="t('common.detail')" @click="openDetail(row)" />
          </el-tooltip>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="detailVisible" :title="t('pages.qc.dialogDetail')" width="640px" destroy-on-close align-center>
      <el-descriptions v-if="detailHdr" :column="1" border size="small">
        <el-descriptions-item :label="t('common.qcNo')">{{ detailHdr.qc_number }}</el-descriptions-item>
        <el-descriptions-item :label="t('common.productionNo')">{{ detailHdr.production_id }}</el-descriptions-item>
        <el-descriptions-item :label="t('common.date')">{{ detailHdr.qc_date || t('common.emptyValue') }}</el-descriptions-item>
      </el-descriptions>
      <el-table v-if="detailLines.length" :data="detailLines" class="mt-3" border size="small" table-layout="auto" max-height="280">
        <el-table-column prop="thickness_actual" :label="t('common.actual')" width="100" />
        <el-table-column prop="thickness_min" :label="t('common.min')" width="80" />
        <el-table-column prop="thickness_max" :label="t('common.max')" width="80" />
        <el-table-column prop="is_ok" :label="t('common.result')" width="90">
          <template #default="{ row }">
            <el-tag :type="row.is_ok ? 'success' : 'danger'" size="small">{{ row.is_ok ? t('status.ok') : t('status.ng') }}</el-tag>
          </template>
        </el-table-column>
      </el-table>
      <template #footer>
        <el-button type="primary" @click="detailVisible = false">{{ t('pages.qc.closeDetail') }}</el-button>
      </template>
    </el-dialog>
  </AdminSection>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { View } from '@element-plus/icons-vue'
import AdminSection from '../../components/AdminSection.vue'
import {
  listProduction,
  listQc,
  listQcDetails,
} from '../../api/client'

const { t } = useI18n()
const route = useRoute()
const loading = ref(false)
const keyword = ref('')
const filterMrpOnly = ref(false)
const rows = ref([])

async function load() {
  loading.value = true
  try {
    const [qc, pr] = await Promise.all([listQc(), listProduction()])
    const detailLists = await Promise.all(qc.map((q) => listQcDetails(q.id).catch(() => [])))
    rows.value = qc.map((q, i) => {
      const lines = detailLists[i]
      const ok = lines.find((l) => l.is_ok)
      const ng = lines.find((l) => l.is_ok === false)
      return {
        ...q,
        qc_date: q.qc_date ? String(q.qc_date).slice(0, 10) : '',
        production_label: `${pr.find((x) => x.id === q.production_id)?.production_number || q.production_id}`,
        sample_result: ok ? 'ok' : ng ? 'ng' : null,
      }
    })
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  await load()
  const qcIdRaw = route.query.qc_id
  const qcId = Number(qcIdRaw)
  if (!Number.isNaN(qcId) && qcId > 0) {
    const target = rows.value.find((r) => Number(r.id) === qcId)
    if (target) await openDetail(target)
  }
})

function isMrpBook(row) {
  const prod = String(row?.production_label || '').toUpperCase()
  const qcNo = String(row?.qc_number || '').toUpperCase()
  return prod.startsWith('MRP-') || qcNo.startsWith('MRP-')
}

const filteredRows = computed(() => {
  const q = keyword.value.trim().toLowerCase()
  return rows.value.filter((r) => {
    if (filterMrpOnly.value && !isMrpBook(r)) return false
    if (!q) return true
    return JSON.stringify(r).toLowerCase().includes(q)
  })
})

const detailVisible = ref(false)
const detailHdr = ref(null)
const detailLines = ref([])

async function openDetail(row) {
  detailHdr.value = row
  detailLines.value = await listQcDetails(row.id).catch(() => [])
  detailVisible.value = true
}
</script>

<style scoped>
</style>
