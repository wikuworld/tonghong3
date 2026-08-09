<template>
  <AdminSection :title="pageTitle" :subtitle="pageSubtitle">
    <template #actions>
      <el-button :icon="Refresh" :loading="loading" @click="reload">{{ t('common.refresh') }}</el-button>
      <el-button v-if="canCreate" :loading="importing" @click="triggerImport">
        {{ t('pages.mrpMasterImport.importRaw') }}
      </el-button>
      <input
        ref="fileInput"
        type="file"
        accept=".xls,.xlsx,application/vnd.ms-excel"
        class="hidden"
        @change="onFilePicked"
      />
      <el-button v-if="canCreate" type="primary" :icon="Plus" @click="openCreate">{{ t('common.create') }}</el-button>
    </template>
    <div class="admin-inner-card">
      <el-table :data="rows" v-loading="loading" border stripe size="small" class="admin-table">
        <el-table-column type="index" width="56" :label="t('common.noLabel')" align="center" />
        <el-table-column
          v-for="col in columns"
          :key="col.prop"
          :prop="col.prop"
          :label="col.label"
          :min-width="col.minWidth || 120"
        />
        <el-table-column v-if="canUpdate || canDelete" :label="t('common.actions')" width="140" fixed="right">
          <template #default="{ row }">
            <el-button v-if="canUpdate && kind !== 'material'" link type="primary" @click="openEdit(row)">
              {{ t('common.edit') }}
            </el-button>
            <el-button v-if="canDelete" link type="danger" @click="remove(row)">{{ t('common.delete') }}</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <el-dialog v-model="dialogOpen" :title="editingId ? t('common.edit') : t('common.create')" width="480px" destroy-on-close>
      <el-form label-position="top">
        <el-form-item v-for="field in createFields" :key="field.key" :label="field.label" :required="field.required">
          <el-input v-model="form[field.key]" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogOpen = false">{{ t('common.cancel') }}</el-button>
        <el-button type="primary" :loading="saving" @click="submit">{{ t('common.save') }}</el-button>
      </template>
    </el-dialog>
  </AdminSection>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Refresh } from '@element-plus/icons-vue'
import AdminSection from '../../../components/AdminSection.vue'
import { can } from '../../../security/permissions'
import {
  mrpCreateMasterKimia,
  mrpCreateMasterKulit,
  mrpCreateMasterMaterialLain,
  mrpCreateMasterRp,
  mrpDeleteMasterKimia,
  mrpDeleteMasterKulit,
  mrpDeleteMasterMaterialLain,
  mrpDeleteMasterRp,
  mrpImportRawMaterial,
  mrpListMasterKimia,
  mrpListMasterKulit,
  mrpListMasterMaterialLain,
  mrpListMasterRp,
  mrpUpdateMasterKimia,
  mrpUpdateMasterKulit,
  mrpUpdateMasterRp,
} from '../../../api/client'

const { t } = useI18n()
const route = useRoute()
const kind = computed(() => route.meta.mrpMaster || 'kulit')
const loading = ref(false)
const saving = ref(false)
const importing = ref(false)
const fileInput = ref(null)
const rows = ref([])
const dialogOpen = ref(false)
const editingId = ref(null)
const canCreate = computed(() => can('mrpShopfloor', 'create'))
const canUpdate = computed(() => can('mrpShopfloor', 'update'))
const canDelete = computed(() => can('mrpShopfloor', 'update'))
const form = reactive({})

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
      { prop: 'kode_kimia', label: 'Kode', minWidth: 120 },
      { prop: 'nama_kimia', label: 'Nama', minWidth: 160 },
      { prop: 'kode_barang', label: 'Kode Barang', minWidth: 120 },
      { prop: 'nama_barang', label: 'Nama Barang', minWidth: 160 },
      { prop: 'satuan', label: 'Satuan', minWidth: 80 },
    ]
  }
  if (kind.value === 'rp') {
    return [
      { prop: 'kode_rp', label: 'Kode', minWidth: 120 },
      { prop: 'nama_rp', label: 'Nama', minWidth: 160 },
      { prop: 'nama_jenis', label: 'Jenis', minWidth: 140 },
      { prop: 'satuan', label: 'Satuan', minWidth: 80 },
      { prop: 'deskripsi', label: 'Deskripsi', minWidth: 160 },
    ]
  }
  if (kind.value === 'material') {
    return [
      { prop: 'kode_material', label: 'Kode', minWidth: 120 },
      { prop: 'nama_material', label: 'Nama', minWidth: 160 },
      { prop: 'satuan', label: 'Satuan', minWidth: 80 },
      { prop: 'deskripsi', label: 'Deskripsi', minWidth: 160 },
    ]
  }
  return [
    { prop: 'kode_kulit', label: 'Kode', minWidth: 120 },
    { prop: 'nama_kulit', label: 'Nama', minWidth: 160 },
    { prop: 'thickness', label: 'Thickness', minWidth: 100 },
    { prop: 'warna', label: t('common.color'), minWidth: 120 },
  ]
})

const createFields = computed(() => {
  if (kind.value === 'kimia') {
    return [
      { key: 'kode_kimia', label: 'Kode', required: true },
      { key: 'nama_kimia', label: 'Nama', required: true },
      { key: 'satuan', label: 'Satuan' },
    ]
  }
  if (kind.value === 'rp') {
    return [
      { key: 'kode_rp', label: 'Kode', required: true },
      { key: 'nama_rp', label: 'Nama', required: true },
      { key: 'deskripsi', label: 'Deskripsi' },
    ]
  }
  if (kind.value === 'material') {
    return [
      { key: 'kode_material', label: 'Kode', required: true },
      { key: 'nama_material', label: 'Nama', required: true },
      { key: 'satuan', label: 'Satuan' },
      { key: 'deskripsi', label: 'Deskripsi' },
    ]
  }
  return [
    { key: 'kode_kulit', label: 'Kode', required: true },
    { key: 'nama_kulit', label: 'Nama', required: true },
    { key: 'thickness', label: 'Thickness' },
    { key: 'warna', label: t('common.color') },
  ]
})

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

function resetForm() {
  for (const f of createFields.value) {
    form[f.key] = f.key === 'satuan' ? (kind.value === 'material' ? 'pcs' : 'kg') : ''
  }
}

function openCreate() {
  editingId.value = null
  resetForm()
  dialogOpen.value = true
}

function openEdit(row) {
  editingId.value = row.id
  resetForm()
  for (const f of createFields.value) {
    form[f.key] = row[f.key] ?? ''
  }
  dialogOpen.value = true
}

async function submit() {
  saving.value = true
  try {
    if (editingId.value) {
      if (kind.value === 'kimia') await mrpUpdateMasterKimia(editingId.value, { ...form })
      else if (kind.value === 'rp') await mrpUpdateMasterRp(editingId.value, { ...form })
      else await mrpUpdateMasterKulit(editingId.value, { ...form })
    } else if (kind.value === 'kimia') await mrpCreateMasterKimia({ ...form })
    else if (kind.value === 'rp') await mrpCreateMasterRp({ ...form })
    else if (kind.value === 'material') await mrpCreateMasterMaterialLain({ ...form })
    else await mrpCreateMasterKulit({ ...form })
    ElMessage.success(t('common.saved'))
    dialogOpen.value = false
    await reload()
  } catch (e) {
    ElMessage.error(e.message || String(e))
  } finally {
    saving.value = false
  }
}

async function remove(row) {
  try {
    await ElMessageBox.confirm(t('common.confirmDelete') || 'Hapus?', { type: 'warning' })
    if (kind.value === 'kimia') await mrpDeleteMasterKimia(row.id)
    else if (kind.value === 'rp') await mrpDeleteMasterRp(row.id)
    else if (kind.value === 'material') await mrpDeleteMasterMaterialLain(row.id)
    else await mrpDeleteMasterKulit(row.id)
    ElMessage.success(t('common.saved'))
    await reload()
  } catch (e) {
    if (e !== 'cancel') ElMessage.error(e.message || String(e))
  }
}

onMounted(reload)
</script>
