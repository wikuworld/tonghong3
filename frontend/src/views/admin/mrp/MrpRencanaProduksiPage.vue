<template>
  <AdminSection :title="t('pages.mrpRencana.title')" :subtitle="t('pages.mrpRencana.subtitle')">
    <template #actions>
      <el-button :icon="Refresh" :loading="loading" @click="reload">{{ t('common.refresh') }}</el-button>
      <el-button v-if="canCreate" :loading="syncing" @click="syncPo">{{ t('pages.mrpRencana.syncPo') }}</el-button>
      <el-button v-if="canCreate" type="primary" :icon="Plus" @click="openCreate">{{ t('common.create') }}</el-button>
    </template>

    <div class="admin-inner-card">
      <el-table :data="rows" v-loading="loading" border stripe size="small" class="admin-table">
        <el-table-column type="index" :label="t('common.noLabel')" width="56" align="center" />
        <el-table-column prop="kode_rencana" :label="t('pages.mrpRencana.code')" min-width="140" />
        <el-table-column prop="nama_rencana" :label="t('pages.mrpRencana.name')" min-width="180" />
        <el-table-column prop="tanggal_rencana" :label="t('pages.mrpRencana.date')" width="120" />
        <el-table-column prop="status" :label="t('common.status')" width="100" />
        <el-table-column :label="t('common.actions')" width="160" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="openDetail(row)">{{ t('common.detail') }}</el-button>
            <el-button link @click="printRencana(row)">{{ t('pages.mrpRencana.print') }}</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <el-drawer v-model="detailOpen" size="55%" :title="detail?.rencana?.nama_rencana || t('common.detail')">
      <template v-if="detail">
        <p class="text-sm text-slate-500 mb-3">
          {{ detail.rencana.kode_rencana }} · {{ detail.rencana.tanggal_rencana }} · {{ detail.rencana.status }}
        </p>
        <el-table :data="detail.items || []" border size="small">
          <el-table-column prop="kode_rencana_item" label="Item" min-width="130" />
          <el-table-column prop="kode_lot_wip" label="WIP" min-width="130" />
          <el-table-column prop="nama_customer" :label="t('common.customer')" min-width="120" />
          <el-table-column prop="material_name" label="Material" min-width="120" />
          <el-table-column prop="thickness" label="Thickness" width="90" />
          <el-table-column prop="color" label="Color" width="100" />
          <el-table-column prop="emboss" label="Emboss" width="100" />
          <el-table-column prop="jml_po" label="PO" width="60" />
          <el-table-column :label="t('common.actions')" width="160" fixed="right">
            <template #default="{ row }">
              <el-button link type="primary" @click="openPo(row)">PO</el-button>
              <el-button link @click="showBarcode(row)">Barcode</el-button>
            </template>
          </el-table-column>
        </el-table>
      </template>
    </el-drawer>

    <el-dialog v-model="poOpen" :title="t('pages.mrpRencana.listPo')" width="720px" destroy-on-close>
      <el-table :data="poList" border size="small" @selection-change="onPoSelect">
        <el-table-column type="selection" width="40" />
        <el-table-column prop="no_po" label="PO" min-width="120" />
        <el-table-column prop="item_name" label="Item" min-width="140" />
        <el-table-column prop="qty_outstanding" label="Outstanding" width="110" />
        <el-table-column :label="'Qty'" width="120">
          <template #default="{ row }">
            <el-input v-model.number="poQty[row.id]" type="number" size="small" />
          </template>
        </el-table-column>
      </el-table>
      <template #footer>
        <el-button @click="poOpen = false">{{ t('common.cancel') }}</el-button>
        <el-button type="primary" :loading="savingPo" @click="savePo">{{ t('common.save') }}</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="barcodeOpen" title="Barcode" width="420px">
      <div v-if="barcodeData" class="text-center space-y-2">
        <div class="text-2xl font-mono font-bold">{{ barcodeData.barcode }}</div>
        <div class="text-sm">{{ barcodeData.item?.kode_rencana_item }} · {{ barcodeData.item?.nama_customer }}</div>
        <div class="text-sm text-slate-500">
          {{ barcodeData.item?.thickness }} / {{ barcodeData.item?.color }} / {{ barcodeData.item?.emboss }}
        </div>
      </div>
    </el-dialog>

    <el-dialog v-model="printOpen" :title="t('pages.mrpRencana.print')" width="640px">
      <template v-if="printData">
        <h3 class="font-semibold mb-2">{{ printData.rencana?.nama_rencana }} ({{ printData.rencana?.kode_rencana }})</h3>
        <el-table :data="printData.items || []" border size="small">
          <el-table-column prop="kode_rencana_item" label="Item" />
          <el-table-column prop="nama_customer" :label="t('common.customer')" />
          <el-table-column prop="material_name" label="Material" />
          <el-table-column prop="total_qty_so" label="Qty SO" width="90" />
          <el-table-column prop="schedule_text" label="SO/PO" min-width="120" />
        </el-table>
      </template>
    </el-dialog>

    <el-dialog v-model="createOpen" :title="t('pages.mrpRencana.createTitle')" width="720px" destroy-on-close>
      <el-form label-position="top">
        <el-form-item :label="t('pages.mrpRencana.name')" required>
          <el-input v-model="form.nama_rencana" />
        </el-form-item>
        <el-form-item :label="t('pages.mrpRencana.date')">
          <el-date-picker v-model="form.tanggal_rencana" type="date" value-format="YYYY-MM-DD" class="w-full" />
        </el-form-item>
        <div class="mb-2 flex items-center justify-between">
          <strong>{{ t('pages.mrpRencana.items') }}</strong>
          <el-button size="small" @click="addItem">{{ t('common.add') }}</el-button>
        </div>
        <div v-for="(item, idx) in form.items" :key="idx" class="mb-3 grid grid-cols-2 gap-2 rounded border p-3">
          <el-select v-model="item.thickness" filterable allow-create :placeholder="'Thickness'" @change="onItemFieldChange(item)">
            <el-option v-for="o in options.thickness" :key="o" :label="o" :value="o" />
          </el-select>
          <el-select v-model="item.material_name" filterable allow-create :placeholder="'Material'" @change="onItemFieldChange(item)">
            <el-option v-for="o in options.materials" :key="o" :label="o" :value="o" />
          </el-select>
          <el-select v-model="item.color" filterable allow-create :placeholder="'Color'" @change="onItemFieldChange(item)">
            <el-option v-for="o in options.colors" :key="o" :label="o" :value="o" />
          </el-select>
          <el-select v-model="item.emboss" filterable allow-create :placeholder="'Emboss'">
            <el-option v-for="o in options.emboss" :key="o" :label="o" :value="o" />
          </el-select>
          <el-select v-model="item.customer" filterable allow-create :placeholder="t('common.customer')">
            <el-option v-for="o in options.customers" :key="o" :label="o" :value="o" />
          </el-select>
          <el-select v-model="item.color_swatch" filterable allow-create :placeholder="'Color Swatch'">
            <el-option v-for="o in options.color_swatch" :key="o" :label="o" :value="o" />
          </el-select>
          <el-button link type="danger" @click="form.items.splice(idx, 1)">{{ t('common.delete') }}</el-button>
        </div>
      </el-form>
      <template #footer>
        <el-button @click="createOpen = false">{{ t('common.cancel') }}</el-button>
        <el-button type="primary" :loading="saving" @click="submitCreate">{{ t('common.save') }}</el-button>
      </template>
    </el-dialog>
  </AdminSection>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessage } from 'element-plus'
import { Plus, Refresh } from '@element-plus/icons-vue'
import AdminSection from '../../../components/AdminSection.vue'
import { can } from '../../../security/permissions'
import {
  mrpCreateRencana,
  mrpErpFields,
  mrpErpOptions,
  mrpGetRencana,
  mrpListRencana,
  mrpRencanaItemBarcode,
  mrpRencanaItemListPo,
  mrpRencanaItemSavePo,
  mrpRencanaPrint,
  mrpSyncPo,
} from '../../../api/client'

const { t } = useI18n()
const loading = ref(false)
const saving = ref(false)
const savingPo = ref(false)
const syncing = ref(false)
const rows = ref([])
const detailOpen = ref(false)
const detail = ref(null)
const createOpen = ref(false)
const poOpen = ref(false)
const barcodeOpen = ref(false)
const printOpen = ref(false)
const poList = ref([])
const poQty = reactive({})
const selectedPos = ref([])
const currentItemId = ref(null)
const barcodeData = ref(null)
const printData = ref(null)
const canCreate = computed(() => can('mrpShopfloor', 'create'))
const options = reactive({
  thickness: [],
  materials: [],
  colors: [],
  emboss: [],
  customers: [],
  color_swatch: [],
})
const form = reactive({
  nama_rencana: '',
  tanggal_rencana: new Date().toISOString().slice(0, 10),
  items: [],
})

function emptyItem() {
  return { thickness: '', material_name: '', color: '', emboss: '', customer: '', color_swatch: '' }
}

function addItem() {
  form.items.push(emptyItem())
}

async function reload() {
  loading.value = true
  try {
    rows.value = await mrpListRencana()
  } catch (e) {
    ElMessage.error(e.message || String(e))
  } finally {
    loading.value = false
  }
}

async function syncPo() {
  syncing.value = true
  try {
    const res = await mrpSyncPo()
    ElMessage.success(
      `${t('pages.mrpRencana.syncPo')}: +${res.inserted || 0} / ~${res.updated || 0} (pull ${res.pulled || res.total || 0})`,
    )
  } catch (e) {
    ElMessage.error(e.message || String(e))
  } finally {
    syncing.value = false
  }
}

async function openDetail(row) {
  try {
    detail.value = await mrpGetRencana(row.id)
    detailOpen.value = true
  } catch (e) {
    ElMessage.error(e.message || String(e))
  }
}

async function printRencana(row) {
  try {
    printData.value = await mrpRencanaPrint(row.id)
    printOpen.value = true
  } catch (e) {
    ElMessage.error(e.message || String(e))
  }
}

async function showBarcode(row) {
  try {
    barcodeData.value = await mrpRencanaItemBarcode(row.id)
    barcodeOpen.value = true
  } catch (e) {
    ElMessage.error(e.message || String(e))
  }
}

async function openPo(row) {
  currentItemId.value = row.id
  selectedPos.value = []
  try {
    const data = await mrpRencanaItemListPo(row.id)
    poList.value = data.po_list || []
    for (const p of poList.value) {
      poQty[p.id] = p.qty_outstanding || 0
    }
    poOpen.value = true
  } catch (e) {
    ElMessage.error(e.message || String(e))
  }
}

function onPoSelect(rowsSel) {
  selectedPos.value = rowsSel
}

async function savePo() {
  if (!selectedPos.value.length) {
    ElMessage.warning(t('pages.mrpRencana.listPo'))
    return
  }
  savingPo.value = true
  try {
    await mrpRencanaItemSavePo(currentItemId.value, {
      pos: selectedPos.value.map((p) => ({ po_id: p.id, qty: poQty[p.id] || 0 })),
    })
    ElMessage.success(t('common.saved'))
    poOpen.value = false
    if (detail.value?.rencana?.id) {
      detail.value = await mrpGetRencana(detail.value.rencana.id)
    }
  } catch (e) {
    ElMessage.error(e.message || String(e))
  } finally {
    savingPo.value = false
  }
}

async function onItemFieldChange(item) {
  try {
    const fields = await mrpErpFields({
      thickness: item.thickness,
      material_name: item.material_name,
      color: item.color,
    })
    if (fields.material_names?.length) options.materials = fields.material_names
    if (fields.colors?.length) options.colors = fields.colors
    if (fields.embosses?.length) options.emboss = fields.embosses
    if (fields.customers?.length) options.customers = fields.customers
  } catch {
    /* cascade optional */
  }
}

async function openCreate() {
  form.nama_rencana = ''
  form.tanggal_rencana = new Date().toISOString().slice(0, 10)
  form.items = [emptyItem()]
  try {
    const opt = await mrpErpOptions()
    Object.assign(options, opt)
  } catch (e) {
    ElMessage.error(e.message || String(e))
  }
  createOpen.value = true
}

async function submitCreate() {
  saving.value = true
  try {
    await mrpCreateRencana({
      nama_rencana: form.nama_rencana,
      tanggal_rencana: form.tanggal_rencana,
      items: form.items,
    })
    ElMessage.success(t('common.saved'))
    createOpen.value = false
    await reload()
  } catch (e) {
    ElMessage.error(e.message || String(e))
  } finally {
    saving.value = false
  }
}

onMounted(reload)
</script>
