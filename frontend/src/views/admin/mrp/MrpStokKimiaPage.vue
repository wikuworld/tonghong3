<template>
  <AdminSection :title="t('pages.mrpStokKimia.title')" :subtitle="t('pages.mrpStokKimia.subtitle')">
    <template #actions>
      <el-button :icon="Refresh" :loading="loading" @click="reload">{{ t('common.refresh') }}</el-button>
    </template>

    <div v-if="canCreate" class="admin-inner-card mb-4">
      <h3 class="admin-inner-card__title mb-2">IN</h3>
      <div class="flex flex-wrap gap-2">
        <el-select v-model="inForm.kimia_id" filterable :placeholder="t('pages.mrpStokKimia.kimia')" class="max-w-xs">
          <el-option v-for="k in kimiaList" :key="k.id" :label="`${k.kode_barang} — ${k.nama_barang}`" :value="k.id" />
        </el-select>
        <el-input v-model.number="inForm.qty" type="number" placeholder="Qty" class="max-w-[120px]" />
        <el-input v-model.number="inForm.jumlah_kemasan" type="number" :placeholder="t('pages.mrpStokKimia.kemasan')" class="max-w-[120px]" />
        <el-date-picker v-model="inForm.tanggal" type="date" value-format="YYYY-MM-DD" />
        <el-button type="primary" :loading="saving" @click="doIn">IN</el-button>
      </div>
    </div>

    <div v-if="canUpdate" class="admin-inner-card mb-4">
      <h3 class="admin-inner-card__title mb-2">OUT</h3>
      <div class="flex flex-wrap gap-2">
        <el-select v-model="outForm.stok_in_id" filterable placeholder="Lot" class="max-w-md">
          <el-option v-for="s in stokIn" :key="s.id" :label="`${s.kode_internal} · ${s.nama_barang} · sisa ${s.qty_sisa}`" :value="s.id" />
        </el-select>
        <el-input v-model.number="outForm.qty" type="number" placeholder="Qty" class="max-w-[120px]" />
        <el-select v-model="outForm.tujuan" class="max-w-[140px]">
          <el-option label="mixing" value="mixing" />
          <el-option label="produksi" value="produksi" />
          <el-option label="return" value="return" />
        </el-select>
        <el-input v-model="outForm.kode_wip" placeholder="WIP" class="max-w-xs" />
        <el-button type="danger" :loading="saving" @click="doOut">OUT</el-button>
      </div>
    </div>

    <div class="admin-inner-card mb-4">
      <h3 class="admin-inner-card__title mb-2">{{ t('pages.mrpStokKimia.stokIn') }}</h3>
      <el-table :data="stokIn" v-loading="loading" border stripe size="small">
        <el-table-column prop="kode_internal" label="BC" min-width="140" />
        <el-table-column prop="kode_barang" label="Kode" width="110" />
        <el-table-column prop="nama_barang" label="Nama" min-width="140" />
        <el-table-column prop="qty_sisa" label="Sisa" width="90" />
        <el-table-column prop="gudang" label="Gudang" width="90" />
        <el-table-column prop="tanggal_in" :label="t('common.date')" width="120" />
      </el-table>
    </div>
    <div class="admin-inner-card">
      <h3 class="admin-inner-card__title mb-2">{{ t('pages.mrpStokKimia.stokOut') }}</h3>
      <el-table :data="stokOut" border stripe size="small">
        <el-table-column prop="nama_barang" label="Nama" min-width="140" />
        <el-table-column prop="qty" label="Qty" width="90" />
        <el-table-column prop="tujuan" label="Tujuan" width="100" />
        <el-table-column prop="kode_wip" label="WIP" min-width="120" />
        <el-table-column prop="tanggal" :label="t('common.date')" width="120" />
      </el-table>
    </div>
  </AdminSection>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessage } from 'element-plus'
import { Refresh } from '@element-plus/icons-vue'
import AdminSection from '../../../components/AdminSection.vue'
import { can } from '../../../security/permissions'
import { mrpStokKimia, mrpStokKimiaAction } from '../../../api/client'

const { t } = useI18n()
const loading = ref(false)
const saving = ref(false)
const stokIn = ref([])
const stokOut = ref([])
const kimiaList = ref([])
const canCreate = computed(() => can('mrpShopfloor', 'create'))
const canUpdate = computed(() => can('mrpShopfloor', 'update'))
const inForm = reactive({ kimia_id: null, qty: 0, jumlah_kemasan: null, tanggal: new Date().toISOString().slice(0, 10) })
const outForm = reactive({ stok_in_id: null, qty: 0, tujuan: 'mixing', kode_wip: '', tanggal: new Date().toISOString().slice(0, 10) })

async function reload() {
  loading.value = true
  try {
    const data = await mrpStokKimia()
    stokIn.value = data.stok_in || []
    stokOut.value = data.stok_out || []
    kimiaList.value = data.kimia_list || []
  } catch (e) {
    ElMessage.error(e.message || String(e))
  } finally {
    loading.value = false
  }
}
async function doIn() {
  saving.value = true
  try {
    await mrpStokKimiaAction({ action: 'in', ...inForm })
    ElMessage.success(t('common.saved'))
    await reload()
  } catch (e) {
    ElMessage.error(e.message || String(e))
  } finally {
    saving.value = false
  }
}
async function doOut() {
  saving.value = true
  try {
    await mrpStokKimiaAction({ action: 'out', ...outForm })
    ElMessage.success(t('common.saved'))
    await reload()
  } catch (e) {
    ElMessage.error(e.message || String(e))
  } finally {
    saving.value = false
  }
}
onMounted(reload)
</script>
