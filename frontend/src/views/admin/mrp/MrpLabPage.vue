<template>
  <AdminSection :title="t('pages.mrpLab.title')" :subtitle="t('pages.mrpLab.subtitle')">
    <template #actions>
      <el-button :icon="Refresh" :loading="loading" @click="reload">{{ t('common.refresh') }}</el-button>
      <el-button v-if="canCreate" type="primary" :icon="Plus" @click="openCreate">{{ t('common.create') }}</el-button>
    </template>

    <div class="admin-inner-card">
      <el-table :data="rows" v-loading="loading" border stripe size="small" class="admin-table" max-height="60vh">
        <el-table-column prop="kode_lot_warna" :label="t('pages.mrpLab.kodeLot')" min-width="130" />
        <el-table-column prop="nama_lot_warna" :label="t('pages.mrpLab.namaLot')" min-width="140" />
        <el-table-column prop="kode_rencana_item" label="RPI" min-width="120" />
        <el-table-column prop="nama_customer" :label="t('common.customer')" min-width="110" />
        <el-table-column prop="kode_kimia" label="Kimia" width="100" />
        <el-table-column prop="nama_kimia" :label="t('common.name')" min-width="120" />
        <el-table-column prop="resep" label="Resep" width="100" />
        <el-table-column prop="qty" label="Qty" width="80" />
        <el-table-column prop="satuan" label="Sat" width="70" />
        <el-table-column prop="status" :label="t('common.status')" width="90" />
      </el-table>
    </div>

    <el-dialog v-model="createOpen" :title="t('pages.mrpLab.createTitle')" width="720px" destroy-on-close>
      <el-form label-position="top">
        <el-form-item :label="t('pages.mrpLab.namaLot')" required>
          <el-input v-model="form.nama_lot_warna" />
        </el-form-item>
        <el-form-item :label="t('pages.mrpLab.linkRpi')">
          <el-select v-model="form.rencana_item_id" clearable filterable class="w-full">
            <el-option
              v-for="it in options.rencana_items"
              :key="it.id"
              :label="`${it.kode_rencana_item} · ${it.nama_customer} · ${it.color || ''}`"
              :value="it.id"
            />
          </el-select>
        </el-form-item>
        <div class="mb-2 flex justify-between">
          <strong>{{ t('pages.mrpLab.items') }}</strong>
          <el-button size="small" @click="addRow">{{ t('common.add') }}</el-button>
        </div>
        <div v-for="(row, idx) in form.items" :key="idx" class="mb-2 grid grid-cols-5 gap-2">
          <el-select v-model="row.kode_kimia" filterable allow-create :placeholder="'Kode kimia'">
            <el-option
              v-for="k in options.kimia_list"
              :key="k.kode_kimia"
              :label="`${k.kode_kimia} · ${k.nama_kimia}`"
              :value="k.kode_kimia"
            />
          </el-select>
          <el-select v-model="row.resep" filterable allow-create clearable :placeholder="'Resep'">
            <el-option v-for="r in options.reseps" :key="r" :label="r" :value="r" />
          </el-select>
          <el-input v-model="row.qty" type="number" placeholder="Qty" />
          <el-input v-model="row.satuan" placeholder="Satuan" />
          <el-button link type="danger" @click="form.items.splice(idx, 1)">{{ t('common.delete') }}</el-button>
        </div>
      </el-form>
      <template #footer>
        <el-button @click="createOpen = false">{{ t('common.cancel') }}</el-button>
        <el-button type="primary" :loading="saving" @click="submit">{{ t('common.save') }}</el-button>
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
import { mrpCreateLab, mrpLabOptions, mrpListLab } from '../../../api/client'

const { t } = useI18n()
const loading = ref(false)
const saving = ref(false)
const createOpen = ref(false)
const rows = ref([])
const canCreate = computed(() => can('mrpShopfloor', 'create'))
const options = reactive({ rencana_items: [], kimia_list: [], reseps: [] })
const form = reactive({
  nama_lot_warna: '',
  rencana_item_id: null,
  items: [],
})

function emptyRow() {
  return { kode_kimia: '', resep: '', qty: 0, satuan: 'kg', remarks: '' }
}

function addRow() {
  form.items.push(emptyRow())
}

async function reload() {
  loading.value = true
  try {
    rows.value = await mrpListLab()
  } catch (e) {
    ElMessage.error(e.message || String(e))
  } finally {
    loading.value = false
  }
}

async function openCreate() {
  form.nama_lot_warna = ''
  form.rencana_item_id = null
  form.items = [emptyRow()]
  try {
    const opt = await mrpLabOptions()
    Object.assign(options, opt)
  } catch (e) {
    ElMessage.error(e.message || String(e))
  }
  createOpen.value = true
}

async function submit() {
  saving.value = true
  try {
    await mrpCreateLab({ ...form })
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
