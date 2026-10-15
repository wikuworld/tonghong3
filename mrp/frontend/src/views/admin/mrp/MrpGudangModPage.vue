<template>
  <AdminSection :title="t('pages.mrpGudangMod.title')" :subtitle="t('pages.mrpGudangMod.subtitle')">
    <template #actions>
      <el-button :icon="Refresh" :loading="loading" @click="reload">{{ t('common.refresh') }}</el-button>
    </template>

    <div class="admin-inner-card">
      <div class="admin-inner-card__head">
        <div>
          <h3 class="admin-inner-card__title">{{ t('pages.mrpGudangMod.listTitle') }}</h3>
          <p class="admin-inner-card__sub">{{ t('pages.mrpGudangMod.listSubtitle') }}</p>
        </div>
        <el-input
          v-model="search"
          clearable
          size="small"
          class="w-56"
          :placeholder="t('pages.mrpGudangMod.searchPlaceholder')"
          @keyup.enter="() => { page = 1; reload() }"
          @clear="() => { page = 1; reload() }"
        />
      </div>

      <el-table
        :data="rows"
        v-loading="loading"
        @sort-change="onSortChange"
        border
        stripe
        size="small"
        class="admin-table"
        :empty-text="t('common.tableEmpty')"
      >
        <el-table-column type="index" width="56" :label="t('common.noLabel')" align="center">
          <template #default="{ $index }">{{ (page - 1) * pageSize + $index + 1 }}</template>
        </el-table-column>
        <el-table-column
          prop="kode_mod"
          sortable="custom"
          :label="t('pages.mrpGudangMod.kodeMod')"
          min-width="150"
          show-overflow-tooltip
        />
        <el-table-column prop="kode_wip" label="WIP" min-width="130" show-overflow-tooltip sortable="custom" />
        <el-table-column prop="kode_proses" :label="t('pages.mrpProses.kodeProses')" min-width="120" show-overflow-tooltip />
        <el-table-column prop="kode_palet" :label="t('pages.mrpProses.returnKyLama')" min-width="110" show-overflow-tooltip />
        <el-table-column prop="kode_yl" :label="t('pages.mrpProses.ylCode')" min-width="110" show-overflow-tooltip />
        <el-table-column :label="t('common.status')" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="row.status === 'in_stock' ? 'success' : 'info'" size="small" effect="plain">
              {{ row.status === 'in_stock' ? t('pages.mrpGudangMod.statusInStock') : t('pages.mrpGudangMod.statusOut') }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column :label="t('pages.mrpProses.rejectSf')" width="90" align="right">
          <template #default="{ row }">{{ formatQty(row.reject_qty) }}</template>
        </el-table-column>
        <el-table-column :label="t('pages.mrpProses.rejectLembar')" width="100" align="right">
          <template #default="{ row }">{{ formatQty(row.reject_lembar) }}</template>
        </el-table-column>
        <el-table-column :label="t('pages.mrpProses.treatmentList')" min-width="140" show-overflow-tooltip>
          <template #default="{ row }">{{ dash(row.treatment_list) }}</template>
        </el-table-column>
        <el-table-column prop="created_at" :label="t('common.date')" min-width="140" show-overflow-tooltip sortable="custom" />
        <el-table-column :label="t('common.actions')" width="140" align="center" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="openRejectLabel(row.id)">
              {{ t('pages.mrpGudangMod.rejectLabelPrint') }}
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      <div class="mt-3 flex justify-end">
        <el-pagination
          v-model:current-page="page"
          v-model:page-size="pageSize"
          :total="total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next"
          background
          small
          @current-change="reload"
          @size-change="() => { page = 1; reload() }"
        />
      </div>
    </div>

    <el-dialog
      v-model="labelOpen"
      :title="t('pages.mrpGudangMod.rejectLabelTitle')"
      width="480px"
      destroy-on-close
      append-to-body
      class="mrp-mod-label-dialog"
    >
      <div v-loading="labelLoading" class="mrp-mod-label-dialog__body">
        <div v-if="labelPayload" class="mrp-mod-label-preview">
          <div class="mrp-mod-label-preview__card">
            <div class="mrp-mod-label-sheet">
              <div class="mrp-mod-label-sheet__head">
                <h3>{{ labelPayload.title }}</h3>
                <img
                  v-if="labelPayload.qrDataUrl"
                  :src="labelPayload.qrDataUrl"
                  class="mrp-mod-label-sheet__qr"
                  :alt="dash(labelPayload.m.kode_mod)"
                />
              </div>
              <table class="mrp-mod-label-sheet__table">
                <tr><td>{{ t('pages.mrpProses.returnKyLama') }}</td><td><strong>{{ dash(labelPayload.m.kode_palet) }}</strong></td></tr>
                <tr><td>{{ t('pages.mrpProses.ylCode') }}</td><td><strong>{{ dash(labelPayload.m.kode_yl) }}</strong></td></tr>
                <tr><td>{{ t('pages.mrpGudangMod.kodeMod') }}</td><td><strong>{{ dash(labelPayload.m.kode_mod) }}</strong></td></tr>
                <tr><td>WIP</td><td><strong>{{ dash(labelPayload.m.kode_wip) }}</strong></td></tr>
                <tr><td>{{ t('pages.mrpGudangMod.materialName') }}</td><td><strong>{{ dash(labelPayload.m.material_name) }}</strong></td></tr>
                <tr><td>{{ t('pages.mrpGudangMod.backingColor') }}</td><td><strong>{{ dash(labelPayload.m.backer) }}</strong></td></tr>
                <tr><td>{{ t('pages.mrpGudangMod.thickness') }}</td><td><strong>{{ dash(labelPayload.m.thickness) }}</strong></td></tr>
                <tr>
                  <td colspan="2" class="mrp-mod-label-sheet__tx">
                    <div class="mrp-mod-label-sheet__tx-title">{{ t('pages.mrpProses.treatmentList') }}</div>
                    <ul v-if="treatmentItems(labelPayload.m.treatment_list).length" class="mrp-mod-label-sheet__tx-list">
                      <li v-for="(name, ti) in treatmentItems(labelPayload.m.treatment_list)" :key="ti">
                        <span>{{ name }}</span>
                        <span class="mrp-mod-label-sheet__box" aria-hidden="true" />
                      </li>
                    </ul>
                    <div v-else class="mrp-mod-label-sheet__tx-empty">—</div>
                  </td>
                </tr>
                <tr><td>{{ t('pages.mrpProses.rejectSf') }}</td><td><strong>{{ formatQty(labelPayload.m.reject_qty) }}</strong></td></tr>
                <tr><td>{{ t('pages.mrpProses.rejectLembar') }}</td><td><strong>{{ formatQty(labelPayload.m.reject_lembar) }}</strong></td></tr>
                <tr><td>{{ t('common.date') }}</td><td>{{ dash(labelPayload.tanggal) }}</td></tr>
              </table>
            </div>
          </div>
        </div>
      </div>
      <template #footer>
        <el-button @click="labelOpen = false">{{ t('common.cancel') }}</el-button>
        <el-button type="primary" :loading="labelPrinting" :disabled="!labelPayload" @click="confirmPrintLabel">
          {{ t('pages.mrpGudangMod.rejectLabelPrintAction') }}
        </el-button>
      </template>
    </el-dialog>
  </AdminSection>
</template>

<script setup>
import { onMounted, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessage } from 'element-plus'
import { Refresh } from '@element-plus/icons-vue'
import QRCode from 'qrcode'
import AdminSection from '../../../components/AdminSection.vue'
import { mrpGudangModLabel, mrpListGudangMod } from '../../../api/client'
import { buildPageParams, fromElSortChange, normalizePageResult } from '../../../utils/tableQuery'

const { t } = useI18n()
const loading = ref(false)
const rows = ref([])
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)
const sortBy = ref('date_created')
const sortDir = ref('desc')
const search = ref('')
const labelOpen = ref(false)
const labelLoading = ref(false)
const labelPrinting = ref(false)
const labelPayload = ref(null)

let searchTimer = null
watch(search, () => {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(() => {
    page.value = 1
    reload()
  }, 350)
})

function dash(v) {
  const s = (v == null ? '' : String(v)).trim()
  return s || '—'
}

function formatQty(v) {
  const n = Number(v)
  if (!Number.isFinite(n)) return '—'
  return Number.isInteger(n) ? String(n) : n.toLocaleString(undefined, { maximumFractionDigits: 2 })
}

function treatmentItems(raw) {
  if (!raw) return []
  if (Array.isArray(raw)) return raw.filter(Boolean)
  return String(raw)
    .split(',')
    .map((s) => s.trim())
    .filter(Boolean)
}

function escHtml(v) {
  return String(v ?? '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
}

async function qrForCode(code) {
  if (!code) return ''
  try {
    return await QRCode.toDataURL(code, { width: 120, margin: 0, errorCorrectionLevel: 'M' })
  } catch {
    return ''
  }
}

function rejectLabelNames() {
  return {
    material: t('pages.mrpGudangMod.materialName'),
    backing: t('pages.mrpGudangMod.backingColor'),
    thickness: t('pages.mrpGudangMod.thickness'),
  }
}

function buildRejectLabelHtml(m, title, tanggal, qrDataUrl = '', labels = rejectLabelNames()) {
  const txItems = treatmentItems(m.treatment_list)
  const txHtml = txItems.length
    ? `<ul class="tx-list">${txItems.map((name) => `<li><span>${escHtml(name)}</span><span class="tx-box"></span></li>`).join('')}</ul>`
    : '<div class="tx-empty">—</div>'
  const qrImg = qrDataUrl ? `<img class="label-qr" src="${qrDataUrl}" alt="${escHtml(m.kode_mod)}" />` : ''
  return `<!DOCTYPE html>
<html lang="id"><head><meta charset="UTF-8"/>
<title>${escHtml(title)}</title>
<style>
  @page { size: 4in 4in; margin: 0; }
  body { font-family: Arial, sans-serif; margin: 0; padding: 8px; }
  .label { width: 4in; height: 4in; border: 2px solid #000; padding: 0.14in; background: #fff; margin: 0 auto; }
  .label-head { display: flex; justify-content: space-between; gap: 8px; margin-bottom: 4px; }
  .label-head h2 { margin: 0; font-size: 12px; flex: 1; }
  .label-qr { width: 0.72in; height: 0.72in; }
  table { width: 100%; border-collapse: collapse; font-size: 9px; }
  td { padding: 1px 0; vertical-align: top; }
  td:first-child:not([colspan]) { width: 38%; }
  .tx-title { font-weight: 700; margin-bottom: 2px; }
  .tx-list { list-style: none; margin: 0; padding: 0; }
  .tx-list li { display: flex; justify-content: space-between; padding: 1px 0; }
  .tx-box { width: 10px; height: 10px; border: 1px solid #000; display: inline-block; }
</style></head><body>
<div class="label">
  <div class="label-head"><h2>${escHtml(title)}</h2>${qrImg}</div>
  <table>
    <tr><td>KY lama</td><td><strong>${escHtml(m.kode_palet)}</strong></td></tr>
    <tr><td>Kode YL</td><td><strong>${escHtml(m.kode_yl)}</strong></td></tr>
    <tr><td>Kode MOD</td><td><strong>${escHtml(m.kode_mod)}</strong></td></tr>
    <tr><td>WIP</td><td><strong>${escHtml(m.kode_wip)}</strong></td></tr>
    <tr><td>${escHtml(labels.material)}</td><td><strong>${escHtml(m.material_name || '')}</strong></td></tr>
    <tr><td>${escHtml(labels.backing)}</td><td><strong>${escHtml(m.backer || '')}</strong></td></tr>
    <tr><td>${escHtml(labels.thickness)}</td><td><strong>${escHtml(m.thickness || '')}</strong></td></tr>
    <tr><td colspan="2"><div class="tx-title">Daftar Treatment</div>${txHtml}</td></tr>
    <tr><td>SF</td><td><strong>${escHtml(m.reject_qty)}</strong></td></tr>
    <tr><td>Qty lembar</td><td><strong>${escHtml(m.reject_lembar ?? '')}</strong></td></tr>
    <tr><td>Tanggal</td><td>${escHtml(tanggal)}</td></tr>
  </table>
</div>
</body></html>`
}

async function openRejectLabel(id) {
  labelOpen.value = true
  labelLoading.value = true
  labelPayload.value = null
  try {
    const data = await mrpGudangModLabel(id)
    const m = data.mod || {}
    const qrDataUrl = await qrForCode(m.kode_mod || m.kode_wip)
    labelPayload.value = {
      title: data.title || 'LABEL REJECT KULIT',
      m,
      tanggal: (m.created_at || '').slice(0, 10) || new Date().toISOString().slice(0, 10),
      qrDataUrl,
    }
  } catch (e) {
    ElMessage.error(e.message || String(e))
    labelOpen.value = false
  } finally {
    labelLoading.value = false
  }
}

function confirmPrintLabel() {
  if (!labelPayload.value) return
  labelPrinting.value = true
  try {
    const { m, title, tanggal, qrDataUrl } = labelPayload.value
    const html = buildRejectLabelHtml(m, title, tanggal, qrDataUrl)
    const win = window.open('', '_blank', 'width=520,height=640')
    if (!win) {
      ElMessage.warning(t('pages.mrpProses.popupBlocked'))
      return
    }
    win.document.write(html)
    win.document.close()
    win.focus()
    setTimeout(() => win.print(), 300)
  } finally {
    labelPrinting.value = false
  }
}

function onSortChange(payload) {
  const mapped = fromElSortChange(payload)
  sortBy.value = mapped.sortBy || 'date_created'
  sortDir.value = mapped.sortDir || 'desc'
  page.value = 1
  reload()
}

async function reload() {
  loading.value = true
  try {
    const data = await mrpListGudangMod(
      buildPageParams({
        page: page.value,
        pageSize: pageSize.value,
        sortBy: sortBy.value,
        sortDir: sortDir.value,
        extra: { q: search.value.trim() },
      }),
    )
    const pageData = normalizePageResult(data, { page: page.value, pageSize: pageSize.value })
    rows.value = pageData.items
    total.value = pageData.total
  } catch (e) {
    ElMessage.error(e.message || String(e))
  } finally {
    loading.value = false
  }
}

onMounted(() => reload())
</script>

<style scoped>
.mrp-mod-label-sheet__table {
  width: 100%;
  border-collapse: collapse;
  font-size: 11px;
}
.mrp-mod-label-sheet__table td {
  padding: 2px 0;
  vertical-align: top;
}
.mrp-mod-label-sheet__tx-list {
  list-style: none;
  margin: 0;
  padding: 0;
}
.mrp-mod-label-sheet__tx-list li {
  display: flex;
  justify-content: space-between;
  gap: 6px;
  padding: 1px 0;
}
.mrp-mod-label-sheet__box {
  width: 10px;
  height: 10px;
  border: 1px solid #333;
  flex-shrink: 0;
}
.mrp-mod-label-preview__card {
  border: 1px dashed var(--el-border-color);
  padding: 8px;
  background: #fafafa;
}
.mrp-mod-label-sheet__head {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 8px;
  margin-bottom: 6px;
}
.mrp-mod-label-sheet__head h3 {
  margin: 0;
  font-size: 13px;
}
.mrp-mod-label-sheet__qr {
  width: 72px;
  height: 72px;
}
</style>
