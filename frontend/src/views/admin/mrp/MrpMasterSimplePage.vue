<template>
  <AdminSection :title="pageTitle" :subtitle="pageSubtitle">
    <template #actions>
      <span v-if="loading" class="text-xs text-slate-500">{{ t('common.loadingData') }}</span>
      <el-button :icon="Refresh" :loading="loading" @click="reload">{{ t('common.refresh') }}</el-button>
      <el-button v-if="canImport" :loading="importing" @click="triggerImport">
        {{ t('pages.mrpMasterImport.importRaw') }}
      </el-button>
      <el-button
        v-if="canImport && (kind === 'kimia' || kind === 'rp')"
        :loading="importingPage1"
        @click="importPage1"
      >
        {{ t('pages.mrpMasterImport.importPage1') }}
      </el-button>
      <input
        ref="fileInput"
        type="file"
        accept=".xls,.xlsx,application/vnd.ms-excel"
        class="hidden"
        @change="onFilePicked"
      />
      <el-button type="primary" @click="goInventory">{{ t('pages.mrpMasterCatalog.manageInventory') }}</el-button>
    </template>

    <p class="text-sm text-slate-500 mb-2">
      <el-tag size="small" type="info" effect="plain" class="mr-1 align-middle">{{ t('common.nav.viewOnly') }}</el-tag>
      {{ t('pages.mrpMasterCatalog.sourceHint') }}
      · {{ t('pages.mrpMasterCatalog.crudHint') }}
    </p>

    <div class="admin-inner-card">
      <div class="admin-inner-card__head">
        <div>
          <h3 class="admin-inner-card__title">{{ t('pages.mrpMasterCatalog.listSectionTitle') }}</h3>
          <p class="admin-inner-card__sub">{{ t('pages.mrpMasterCatalog.listSubtitle') }}</p>
        </div>
      </div>
      <div class="mkt-section-body">
        <p class="admin-scroll-hint">{{ t('pages.mrpMasterCatalog.scrollHint') }}</p>
        <div class="admin-table-scroll">
      <el-table :data="rows" v-loading="loading" border stripe size="small" class="admin-table" :empty-text="t('pages.mrpMasterCatalog.tableEmpty')">
        <el-table-column type="index" width="56" :label="t('common.noLabel')" align="center" />
        <el-table-column
          v-for="col in columns"
          :key="col.prop"
          :prop="col.prop"
          :label="col.label"
          :min-width="col.minWidth || 120"
        />
      </el-table>
        </div>
      </div>
    </div>
  </AdminSection>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Refresh } from '@element-plus/icons-vue'
import AdminSection from '../../../components/AdminSection.vue'
import { can } from '../../../security/permissions'
import {
  mrpImportRawMaterial,
  mrpImportPage1Stock,
  mrpListMasterKimia,
  mrpListMasterKulit,
  mrpListMasterMaterialLain,
  mrpListMasterRp,
} from '../../../api/client'

const { t } = useI18n()
const route = useRoute()
const router = useRouter()
const kind = computed(() => route.meta.mrpMaster || 'kulit')
const loading = ref(false)
const importing = ref(false)
const importingPage1 = ref(false)
const fileInput = ref(null)
const rows = ref([])

/** Katalog ERP-only: local create/edit/delete dinonaktifkan (API create/delete → 403). */
const canCreate = computed(() => false)
const canImport = computed(() => can('mrpShopfloor', 'create') && !canCreate.value)

const pageTitle = computed(() => {
  if (kind.value === 'kimia') return t('pages.mrpMasterKimia.title')
  if (kind.value === 'rp') return t('pages.mrpMasterRp.title')
  if (kind.value === 'material') return t('pages.mrpMasterMaterialLain.title')
  return t('pages.mrpMasterKulit.title')
})
const pageSubtitle = computed(() => {
  if (kind.value === 'kimia') return t('pages.mrpMasterKimia.subtitle')
  if (kind.value === 'rp') return t('pages.mrpMasterRp.subtitle')
  if (kind.value === 'material') return t('pages.mrpMasterMaterialLain.subtitle')
  return t('pages.mrpMasterKulit.subtitle')
})

const columns = computed(() => {
  if (kind.value === 'kimia') {
    return [
      { prop: 'kode_kimia', label: t('pages.mrpMasterCatalog.kode'), minWidth: 120 },
      { prop: 'nama_kimia', label: t('pages.mrpMasterCatalog.nama'), minWidth: 160 },
      { prop: 'kode_barang', label: t('pages.mrpMasterCatalog.kodeBarang'), minWidth: 120 },
      { prop: 'nama_barang', label: t('pages.mrpMasterCatalog.namaBarang'), minWidth: 160 },
      { prop: 'satuan', label: t('pages.mrpMasterCatalog.satuan'), minWidth: 80 },
      { prop: 'erp_material_id', label: t('pages.mrpMasterCatalog.erpMatId'), minWidth: 100 },
    ]
  }
  if (kind.value === 'rp') {
    return [
      { prop: 'kode_rp', label: t('pages.mrpMasterCatalog.kode'), minWidth: 120 },
      { prop: 'nama_rp', label: t('pages.mrpMasterCatalog.nama'), minWidth: 160 },
      { prop: 'nama_jenis', label: t('pages.mrpMasterCatalog.jenis'), minWidth: 140 },
      { prop: 'satuan', label: t('pages.mrpMasterCatalog.satuan'), minWidth: 80 },
      { prop: 'deskripsi', label: t('pages.mrpMasterCatalog.deskripsi'), minWidth: 160 },
      { prop: 'erp_material_id', label: t('pages.mrpMasterCatalog.erpMatId'), minWidth: 100 },
    ]
  }
  if (kind.value === 'material') {
    return [
      { prop: 'kode_material', label: t('pages.mrpMasterCatalog.kode'), minWidth: 120 },
      { prop: 'nama_material', label: t('pages.mrpMasterCatalog.nama'), minWidth: 160 },
      { prop: 'satuan', label: t('pages.mrpMasterCatalog.satuan'), minWidth: 80 },
      { prop: 'deskripsi', label: t('pages.mrpMasterCatalog.deskripsi'), minWidth: 160 },
      { prop: 'erp_material_id', label: t('pages.mrpMasterCatalog.erpMatId'), minWidth: 100 },
    ]
  }
  return [
    { prop: 'kode_kulit', label: t('pages.mrpMasterCatalog.kode'), minWidth: 120 },
    { prop: 'nama_kulit', label: t('pages.mrpMasterCatalog.nama'), minWidth: 160 },
    { prop: 'thickness', label: t('pages.mrpMasterCatalog.thickness'), minWidth: 100 },
    { prop: 'warna', label: t('common.color'), minWidth: 120 },
    { prop: 'erp_material_id', label: t('pages.mrpMasterCatalog.erpMatId'), minWidth: 100 },
  ]
})

function goInventory() {
  router.push({ path: '/admin/inventory', query: { tab: 'material' } })
}

async function reload() {
  loading.value = true
  try {
    if (kind.value === 'kimia') rows.value = await mrpListMasterKimia()
    else if (kind.value === 'rp') rows.value = await mrpListMasterRp()
    else if (kind.value === 'material') rows.value = await mrpListMasterMaterialLain()
    else rows.value = await mrpListMasterKulit()
  } catch (e) {
    ElMessage.error(e.message || String(e))
  } finally {
    loading.value = false
  }
}

function triggerImport() {
  ElMessageBox.confirm(t('pages.mrpMasterImport.confirmDefault'), {
    type: 'info',
    distinguishCancelAndClose: true,
    confirmButtonText: t('pages.mrpMasterImport.useDefault'),
    cancelButtonText: t('pages.mrpMasterImport.pickFile'),
  })
    .then(() => runImport(null))
    .catch((action) => {
      if (action === 'cancel') fileInput.value?.click()
    })
}

async function onFilePicked(ev) {
  const file = ev.target?.files?.[0]
  ev.target.value = ''
  if (file) await runImport(file)
}

async function runImport(file) {
  importing.value = true
  try {
    const res = await mrpImportRawMaterial(file)
    const k = res?.kulit || {}
    const c = res?.kimia || {}
    const r = res?.rp || {}
    const m = res?.material || {}
    ElMessage.success(
      t('pages.mrpMasterImport.done', {
        kulit: `${k.inserted || 0}/${k.updated || 0}`,
        kimia: `${c.inserted || 0}/${c.updated || 0}`,
        rp: `${r.inserted || 0}/${r.updated || 0}`,
        material: `${m.inserted || 0}/${m.updated || 0}`,
      }),
    )
    await reload()
  } catch (e) {
    ElMessage.error(e.message || String(e))
  } finally {
    importing.value = false
  }
}

async function importPage1() {
  importingPage1.value = true
  try {
    const res = await mrpImportPage1Stock()
    ElMessage.success(
      t('pages.mrpMasterImport.page1Done', {
        inserted: res?.inserted || 0,
        skipped: res?.skipped_count || (res?.skipped || []).length || 0,
      }),
    )
  } catch (e) {
    ElMessage.error(e.message || String(e))
  } finally {
    importingPage1.value = false
  }
}

onMounted(reload)
</script>
