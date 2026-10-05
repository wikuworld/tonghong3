<template>
  <AdminSection :title="pageTitle" :subtitle="pageSubtitle">
    <template #actions>
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
      <el-button v-if="canCreate" type="primary" :icon="Plus" @click="openCreate">
        {{ t('common.create') }}
      </el-button>
      <el-button type="primary" plain @click="goInventory">{{ t('pages.mrpMasterCatalog.manageInventory') }}</el-button>
    </template>

    <p class="text-sm text-gray-500 mb-2">
      <el-tag v-if="!kulitCrudEnabled" size="small" type="info" effect="plain" class="mr-1 align-middle">
        {{ t('common.nav.viewOnly') }}
      </el-tag>
      {{ t('pages.mrpMasterCatalog.sourceHint') }}
      <template v-if="kulitCrudEnabled"> · {{ t('pages.mrpMasterKulit.crudHint') }}</template>
      <template v-else> · {{ t('pages.mrpMasterCatalog.crudHint') }}</template>
    </p>

    <div class="admin-inner-card">
      <el-table :data="rows" v-loading="loading" border stripe size="small" class="admin-table" :empty-text="t('common.tableEmpty')" @sort-change="onSortChange">
        <el-table-column type="index" width="56" :label="t('common.noLabel')" align="center">
          <template #default="{ $index }">{{ (page - 1) * pageSize + $index + 1 }}</template>
        </el-table-column>
        <el-table-column
          v-for="col in columns"
          :key="col.prop"
          :prop="col.prop"
          :label="col.label"
          :min-width="col.minWidth || 120"
          :sortable="col.sortable ? 'custom' : false"
        />
        <el-table-column v-if="canUpdate && kind === 'kulit'" :label="t('common.actions')" width="112" align="center" fixed="right">
          <template #default="{ row }">
            <AdminTableActions
              :show-edit="true"
              :show-delete="true"
              @edit="openEdit(row)"
              @delete="removeRow(row)"
            />
          </template>
        </el-table-column>
      </el-table>
      <div class="mt-3 flex justify-end">
        <el-pagination
          v-model:current-page="page"
          v-model:page-size="pageSize"
          :total="total"
          :page-sizes="[20, 50, 100]"
          layout="total, sizes, prev, pager, next"
          background
          small
          @current-change="reload"
          @size-change="() => { page = 1; reload() }"
        />
      </div>
    </div>

    <el-dialog
      v-model="formOpen"
      :title="formEdit ? t('common.edit') : t('common.create')"
      width="520px"
      destroy-on-close
      append-to-body
    >
      <el-form label-position="top">
        <el-form-item :label="t('pages.mrpMasterCatalog.kode')" required>
          <el-input v-model="form.kode_kulit" :disabled="formEdit" />
        </el-form-item>
        <el-form-item :label="t('pages.mrpMasterCatalog.nama')" required>
          <el-input v-model="form.nama_kulit" />
        </el-form-item>
        <el-form-item :label="t('pages.mrpMasterKulit.kulitType')" required>
          <el-select v-model="form.type" class="w-full" :placeholder="t('pages.mrpMasterKulit.kulitTypePick')">
            <el-option label="PU" value="PU" />
            <el-option label="SUEDE" value="SUEDE" />
          </el-select>
        </el-form-item>
        <el-form-item :label="t('pages.mrpMasterCatalog.satuan')">
          <el-input v-model="form.satuan" placeholder="sqft" />
        </el-form-item>
        <el-form-item :label="t('common.thickness')">
          <el-input v-model="form.thickness" :placeholder="t('pages.inventory.thicknessPlaceholder')" clearable />
        </el-form-item>
        <el-form-item :label="t('common.color')">
          <el-input v-model="form.warna" clearable />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="formOpen = false">{{ t('common.cancel') }}</el-button>
        <el-button type="primary" :loading="saving" @click="submitForm">{{ t('common.save') }}</el-button>
      </template>
    </el-dialog>
  </AdminSection>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Refresh } from '@element-plus/icons-vue'
import AdminSection from '../../../components/AdminSection.vue'
import AdminTableActions from '../../../components/admin/AdminTableActions.vue'
import { can } from '../../../security/permissions'
import {
  mrpCreateMasterKulit,
  mrpDeleteMasterKulit,
  mrpImportRawMaterial,
  mrpImportPage1Stock,
  mrpListMasterKimia,
  mrpListMasterKulit,
  mrpListMasterMaterialLain,
  mrpListMasterRp,
  mrpUpdateMasterKulit,
} from '../../../api/client'
import { buildPageParams, fromElSortChange, normalizePageResult } from '../../../utils/tableQuery'

const { t } = useI18n()
const route = useRoute()
const router = useRouter()
const kind = computed(() => route.meta.mrpMaster || 'kulit')
const loading = ref(false)
const importing = ref(false)
const importingPage1 = ref(false)
const fileInput = ref(null)
const rows = ref([])
const page = ref(1)
const pageSize = ref(50)
const total = ref(0)
const sortBy = ref(null)
const sortDir = ref('asc')

const kulitCrudEnabled = computed(() => kind.value === 'kulit')
const canCreate = computed(() => kulitCrudEnabled.value && can('mrpShopfloor', 'create'))
const canUpdate = computed(() => kulitCrudEnabled.value && can('mrpShopfloor', 'update'))
const canImport = computed(() => can('mrpShopfloor', 'create') && !canCreate.value)

const formOpen = ref(false)
const formEdit = ref(false)
const saving = ref(false)
const form = reactive({
  id: null,
  kode_kulit: '',
  nama_kulit: '',
  satuan: 'sqft',
  type: 'PU',
  thickness: '',
  warna: '',
})

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
      { prop: 'kode_kimia', label: 'Kode', minWidth: 120, sortable: true },
      { prop: 'nama_kimia', label: 'Nama', minWidth: 160, sortable: true },
      { prop: 'kode_barang', label: 'Kode Barang', minWidth: 120, sortable: true },
      { prop: 'nama_barang', label: 'Nama Barang', minWidth: 160 },
      { prop: 'satuan', label: 'Satuan', minWidth: 80 },
      { prop: 'erp_material_id', label: 'ERP Mat ID', minWidth: 100 },
    ]
  }
  if (kind.value === 'rp') {
    return [
      { prop: 'kode_rp', label: 'Kode', minWidth: 120, sortable: true },
      { prop: 'nama_rp', label: 'Nama', minWidth: 160, sortable: true },
      { prop: 'nama_jenis', label: 'Jenis', minWidth: 140 },
      { prop: 'satuan', label: 'Satuan', minWidth: 80 },
      { prop: 'deskripsi', label: 'Deskripsi', minWidth: 160 },
      { prop: 'erp_material_id', label: 'ERP Mat ID', minWidth: 100 },
    ]
  }
  if (kind.value === 'material') {
    return [
      { prop: 'kode_material', label: 'Kode', minWidth: 120, sortable: true },
      { prop: 'nama_material', label: 'Nama', minWidth: 160, sortable: true },
      { prop: 'satuan', label: 'Satuan', minWidth: 80 },
      { prop: 'deskripsi', label: 'Deskripsi', minWidth: 160 },
      { prop: 'erp_material_id', label: 'ERP Mat ID', minWidth: 100 },
    ]
  }
  return [
    { prop: 'kode_kulit', label: 'Kode', minWidth: 120, sortable: true },
    { prop: 'nama_kulit', label: 'Nama', minWidth: 160, sortable: true },
    { prop: 'type', label: t('pages.mrpMasterKulit.kulitType'), minWidth: 88, sortable: true },
    { prop: 'satuan', label: t('pages.mrpMasterCatalog.satuan'), minWidth: 80 },
    { prop: 'thickness', label: t('common.thickness'), minWidth: 100 },
    { prop: 'warna', label: t('common.color'), minWidth: 120 },
    { prop: 'erp_material_id', label: 'ERP Mat ID', minWidth: 100 },
  ]
})

function resetForm() {
  form.id = null
  form.kode_kulit = ''
  form.nama_kulit = ''
  form.satuan = 'sqft'
  form.type = 'PU'
  form.thickness = ''
  form.warna = ''
}

function openCreate() {
  formEdit.value = false
  resetForm()
  formOpen.value = true
}

function openEdit(row) {
  formEdit.value = true
  form.id = row.id
  form.kode_kulit = row.kode_kulit || ''
  form.nama_kulit = row.nama_kulit || ''
  form.satuan = row.satuan || 'sqft'
  form.type = row.type || row.leather_type || 'PU'
  form.thickness = row.thickness || ''
  form.warna = row.warna || row.color || ''
  formOpen.value = true
}

async function submitForm() {
  if (!form.kode_kulit.trim() || !form.nama_kulit.trim() || !form.type) {
    ElMessage.warning(t('common.fillRequired'))
    return
  }
  saving.value = true
  try {
    const body = {
      kode_kulit: form.kode_kulit.trim(),
      nama_kulit: form.nama_kulit.trim(),
      type: form.type,
      satuan: form.satuan.trim() || 'sqft',
      thickness: form.thickness.trim() || null,
      warna: form.warna.trim() || null,
    }
    if (formEdit.value) {
      await mrpUpdateMasterKulit(form.id, body)
    } else {
      await mrpCreateMasterKulit(body)
    }
    formOpen.value = false
    await reload()
    ElMessage.success(t('common.saveSuccess'))
  } catch (e) {
    ElMessage.error(e.message || String(e))
  } finally {
    saving.value = false
  }
}

async function removeRow(row) {
  try {
    await ElMessageBox.confirm(t('pages.mrpMasterKulit.deleteConfirm'), { type: 'warning' })
  } catch {
    return
  }
  try {
    await mrpDeleteMasterKulit(row.id)
    await reload()
    ElMessage.success(t('common.saveSuccess'))
  } catch (e) {
    ElMessage.error(e.message || String(e))
  }
}

function goInventory() {
  router.push({ path: '/admin/inventory', query: { tab: 'material' } })
}

async function reload() {
  loading.value = true
  try {
    const params = buildPageParams({
      page: page.value,
      pageSize: pageSize.value,
      sortBy: sortBy.value,
      sortDir: sortDir.value,
    })
    let data
    if (kind.value === 'kimia') data = await mrpListMasterKimia(params)
    else if (kind.value === 'rp') data = await mrpListMasterRp(params)
    else if (kind.value === 'material') data = await mrpListMasterMaterialLain(params)
    else data = await mrpListMasterKulit(params)
    const pageData = normalizePageResult(data, { page: page.value, pageSize: pageSize.value })
    rows.value = pageData.items
    total.value = pageData.total
  } catch (e) {
    ElMessage.error(e.message || String(e))
  } finally {
    loading.value = false
  }
}

function onSortChange(payload) {
  const mapped = fromElSortChange(payload)
  sortBy.value = mapped.sortBy
  sortDir.value = mapped.sortDir
  page.value = 1
  reload()
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
