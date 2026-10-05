<template>
  <div class="space-y-4">
    <el-alert class="mb-3" type="info" :closable="false" show-icon>
      <template #title>
        <span>{{ t('pages.packing.bookHint') }}</span>
        <router-link class="ml-2 text-primary underline" to="/admin/mrp/packing">
          {{ t('pages.packing.openMrpPacking') }}
        </router-link>
      </template>
    </el-alert>
    <AdminSection :title="t('pages.packing.title')" :subtitle="t('pages.packing.subtitle')">
      <template #actions>
        <el-select
          v-model="statusTableFilter"
          clearable
          :placeholder="t('pages.packing.filterPackingStatus')"
          class="w-36 mr-2"
        >
          <el-option :label="t('status.draft')" value="draft" />
          <el-option :label="t('status.done')" value="done" />
        </el-select>
        <el-switch
          v-model="filterMrpOnly"
          class="mr-2"
          :active-text="t('pages.packing.filterMrpOnly')"
        />
        <el-checkbox v-if="canPrint" v-model="invplFoc" class="mr-2">
          {{ t('pages.packing.invplFoc') }}
        </el-checkbox>
      </template>

      <div class="admin-inner-card">
        <div class="admin-inner-card__head">
          <div>
            <h3 class="admin-inner-card__title">{{ t('pages.packing.listSectionTitle') }}</h3>
            <p class="admin-inner-card__sub">{{ t('pages.packing.listSectionSub') }}</p>
          </div>
          <el-tooltip placement="top-start" :show-after="200">
            <template #content>{{ t('pages.packing.pageHint') }}</template>
            <el-icon class="packing-hint" :size="16" tabindex="0" :aria-label="t('pages.packing.pageHint')">
              <InfoFilled />
            </el-icon>
          </el-tooltip>
        </div>

        <p class="admin-scroll-hint px-4">{{ t('pages.packing.scrollHint') }}</p>

        <div class="admin-table-scroll px-4 pb-4">
          <el-table :data="displayRows" v-loading="loading" border stripe size="small" class="admin-table" table-layout="fixed" :empty-text="t('pages.packing.tableEmpty')">
            <el-table-column type="index" :label="t('common.noLabel')" width="56" align="center" />
            <el-table-column prop="packing_number" :label="t('pages.packing.packingNo')" min-width="180">
              <template #default="{ row }">
                <span>{{ row.packing_number }}</span>
                <el-tag v-if="isMrpStub(row)" size="small" type="warning" class="ml-1">{{ t('pages.packing.mrpBadge') }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column :label="t('pages.packing.production')" min-width="180" show-overflow-tooltip>
              <template #default="{ row }">{{ prodLabel(row.production_id) }}</template>
            </el-table-column>
            <el-table-column :label="t('pages.packing.qc')" min-width="160" show-overflow-tooltip>
              <template #default="{ row }">{{ qcLabel(row.qc_header_id) }}</template>
            </el-table-column>
            <el-table-column prop="status" :label="t('common.status')" width="100" />
            <el-table-column prop="created_at" :label="t('pages.packing.createdAt')" min-width="160" />
            <el-table-column :label="t('common.actions')" width="220" fixed="right" align="center">
              <template #default="{ row }">
                <div class="flex flex-wrap items-center justify-center gap-0">
                  <el-tooltip v-if="canPrint" :content="t('pages.packing.printInvpl')" placement="top">
                    <el-button :icon="Printer" type="primary" link size="small" @click="openInvpl(row.id)" />
                  </el-tooltip>
                  <el-tooltip v-if="canPrint" :content="t('pages.packing.pdf')" placement="top">
                    <el-button :icon="Document" link size="small" @click="downloadInvplPdf(row.id)" />
                  </el-tooltip>
                  <el-tooltip v-if="canPrint" :content="t('pages.packing.excel')" placement="top">
                    <el-button :icon="Grid" link size="small" @click="downloadInvplExcel(row.id)" />
                  </el-tooltip>
                  <el-tooltip v-if="canUpdate" :content="t('pages.packing.markInvpl')" placement="top">
                    <el-button :icon="Stamp" link size="small" :loading="markInvplId === row.id" @click="markInvpl(row)" />
                  </el-tooltip>
                </div>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </div>
    </AdminSection>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessage } from 'element-plus'
import { Document, Grid, InfoFilled, Printer, Stamp } from '@element-plus/icons-vue'
import AdminSection from '../../components/AdminSection.vue'
import { can } from '../../security/permissions'
import {
  fetchAuthenticatedDocument,
  listPacking,
  listProduction,
  listQc,
  markInvplPrinted,
} from '../../api/client'

const { t } = useI18n()
const rows = ref([])
const statusTableFilter = ref('')

const filterMrpOnly = ref(false)
const displayRows = computed(() => {
  const f = (statusTableFilter.value || '').toLowerCase()
  return (rows.value || []).filter((r) => {
    const statusOk = !f || (r.status || '').toLowerCase() === f
    const mrpOk = !filterMrpOnly.value || isMrpStub(r)
    return statusOk && mrpOk
  })
})
function isMrpStub(row) {
  return String(row?.source || '').toLowerCase() === 'mrp' || Boolean(row?.mrp_fg_id)
}
const canUpdate = can('packing', 'update')
const canPrint = can('packing', 'print')
const productions = ref([])
const qcs = ref([])
const loading = ref(false)
const markInvplId = ref(null)
const invplFoc = ref(false)

function invplPath(id, suffix = '') {
  const q = invplFoc.value ? '?foc=1' : ''
  return `/documents/invpl/${id}${suffix}${q}`
}

function prodLabel(pid) {
  const p = productions.value.find((x) => x.id === pid)
  return p ? `${p.production_number || p.id}` : pid
}

function qcLabel(qid) {
  const q = qcs.value.find((x) => x.id === qid)
  return q ? `${q.qc_number || q.id}` : qid
}

async function load() {
  loading.value = true
  try {
    const [pk, pr, qc] = await Promise.all([listPacking(), listProduction(), listQc()])
    rows.value = pk
    productions.value = pr
    qcs.value = qc
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  } finally {
    loading.value = false
  }
}

onMounted(load)

async function openInvpl(id) {
  try {
    await fetchAuthenticatedDocument(invplPath(id), { mode: 'open' })
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  }
}

async function downloadInvplPdf(id) {
  try {
    await fetchAuthenticatedDocument(invplPath(id, '/pdf'), { mode: 'open' })
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  }
}

async function downloadInvplExcel(id) {
  try {
    await fetchAuthenticatedDocument(invplPath(id, '/xlsx'), {
      mode: 'download',
      downloadFallbackName: `invpl_${id}.xlsx`,
    })
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  }
}

async function markInvpl(row) {
  markInvplId.value = row.id
  try {
    await markInvplPrinted(row.id)
    ElMessage.success(t('pages.packing.invplMarked'))
    await load()
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  } finally {
    markInvplId.value = null
  }
}
</script>

<style scoped>
.packing-hint {
  color: #64748b;
  cursor: help;
}
</style>
