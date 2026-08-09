<template>
  <AdminSection :title="t('pages.mrpUsage.title')" :subtitle="t('pages.mrpUsage.subtitle')">
    <template #actions>
      <el-button :icon="Refresh" :loading="loading" @click="reload">{{ t('common.refresh') }}</el-button>
    </template>
    <el-tabs v-model="tab">
      <el-tab-pane :label="t('pages.mrpUsage.color')" name="color">
        <div v-if="canCreate" class="admin-inner-card mb-4">
          <div class="flex flex-wrap gap-2 mb-2">
            <el-input v-model="colorForm.kode_lot_warna" :placeholder="t('pages.mrpUsage.scanLot')" class="max-w-xs" @keyup.enter="scanLot" />
            <el-button @click="scanLot">Scan</el-button>
            <el-select v-model="colorForm.kode_wip" filterable allow-create :placeholder="'WIP'" class="max-w-xs">
              <el-option v-for="w in colorWip" :key="w" :label="w" :value="w" />
            </el-select>
            <el-input v-model.number="colorForm.qty_digunakan" type="number" placeholder="Qty" class="max-w-[120px]" />
            <el-select v-model="colorForm.stok_in_id" clearable filterable :placeholder="t('pages.mrpUsage.stokLot')" class="max-w-xs">
              <el-option
                v-for="s in kimiaLots"
                :key="s.id"
                :label="`${s.kode_internal} · ${s.nama_barang} · ${s.qty_sisa}`"
                :value="s.id"
              />
            </el-select>
            <el-button type="primary" :loading="saving" @click="saveColor">{{ t('common.save') }}</el-button>
          </div>
          <p v-if="lotInfo" class="text-sm text-slate-500">{{ lotInfo.kode_lot_warna }} — {{ lotInfo.nama_lot_warna }} ({{ lotInfo.qty_pembuatan }})</p>
        </div>
        <el-table :data="colorRows" v-loading="loading" border stripe size="small">
          <el-table-column prop="kode_wip" label="WIP" min-width="120" />
          <el-table-column prop="kode_lot_warna" label="Lot" min-width="120" />
          <el-table-column prop="nama_warna" label="Warna" min-width="120" />
          <el-table-column prop="qty_pembuatan" label="Pembuatan" width="100" />
          <el-table-column prop="qty_digunakan" label="Digunakan" width="100" />
          <el-table-column prop="date_created" :label="t('common.date')" min-width="140" />
        </el-table>
      </el-tab-pane>
      <el-tab-pane :label="t('pages.mrpUsage.rp')" name="rp">
        <div v-if="canCreate" class="admin-inner-card mb-4">
          <div class="flex flex-wrap gap-2 mb-2">
            <el-input v-model="rpForm.jenis_rp" :placeholder="t('pages.mrpUsage.scanRp')" class="max-w-xs" @keyup.enter="scanRp" />
            <el-button @click="scanRp">Scan</el-button>
            <el-select v-model="rpForm.kode_wip" filterable allow-create :placeholder="'WIP'" class="max-w-xs">
              <el-option v-for="w in rpWip" :key="w" :label="w" :value="w" />
            </el-select>
            <el-input v-model.number="rpForm.qty_used" type="number" placeholder="Qty" class="max-w-[120px]" />
            <el-input v-model="rpForm.satuan" placeholder="Satuan" class="max-w-[100px]" />
            <el-select v-model="rpForm.stok_in_id" clearable filterable :placeholder="t('pages.mrpUsage.stokLot')" class="max-w-xs">
              <el-option
                v-for="s in rpLots"
                :key="s.id"
                :label="`${s.kode_internal} · ${s.nama_jenis} · ${s.qty_sisa}`"
                :value="s.id"
              />
            </el-select>
            <el-button type="primary" :loading="saving" @click="saveRp">{{ t('common.save') }}</el-button>
          </div>
          <p v-if="rpInfo" class="text-sm text-slate-500">{{ rpInfo.kode_rp }} — {{ rpInfo.nama_jenis }}</p>
        </div>
        <el-table :data="rpRows" v-loading="loading" border stripe size="small">
          <el-table-column prop="kode_wip" label="WIP" min-width="120" />
          <el-table-column prop="jenis_rp" label="RP" min-width="140" />
          <el-table-column prop="qty_used" label="Qty" width="90" />
          <el-table-column prop="satuan" label="Satuan" width="90" />
          <el-table-column prop="date_created" :label="t('common.date')" min-width="140" />
        </el-table>
      </el-tab-pane>
      <el-tab-pane :label="t('pages.mrpUsage.material')" name="material">
        <div v-if="canCreate" class="admin-inner-card mb-4">
          <div class="flex flex-wrap gap-2 mb-2">
            <el-input v-model="matForm.kode_material" :placeholder="t('pages.mrpUsage.scanMaterial')" class="max-w-xs" @keyup.enter="scanMat" />
            <el-button @click="scanMat">Scan</el-button>
            <el-select v-model="matForm.kode_wip" filterable allow-create :placeholder="'WIP'" class="max-w-xs">
              <el-option v-for="w in matWip" :key="w" :label="w" :value="w" />
            </el-select>
            <el-input v-model.number="matForm.qty_used" type="number" placeholder="Qty" class="max-w-[120px]" />
            <el-input v-model="matForm.satuan" placeholder="Satuan" class="max-w-[100px]" />
            <el-select v-model="matForm.stok_in_id" clearable filterable :placeholder="t('pages.mrpUsage.stokLot')" class="max-w-xs">
              <el-option
                v-for="s in matLots"
                :key="s.id"
                :label="`${s.kode_internal} · ${s.nama_material} · ${s.qty_sisa}`"
                :value="s.id"
              />
            </el-select>
            <el-button type="primary" :loading="saving" @click="saveMat">{{ t('common.save') }}</el-button>
          </div>
          <p v-if="matInfo" class="text-sm text-slate-500">{{ matInfo.kode_material }} — {{ matInfo.nama_material }}</p>
        </div>
        <el-table :data="matRows" v-loading="loading" border stripe size="small">
          <el-table-column prop="kode_wip" label="WIP" min-width="120" />
          <el-table-column prop="kode_material" label="Kode" min-width="120" />
          <el-table-column prop="nama_material" label="Nama" min-width="140" />
          <el-table-column prop="qty_used" label="Qty" width="90" />
          <el-table-column prop="satuan" label="Satuan" width="90" />
          <el-table-column prop="date_created" :label="t('common.date')" min-width="140" />
        </el-table>
      </el-tab-pane>
    </el-tabs>
  </AdminSection>
</template>

<script setup>
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessage } from 'element-plus'
import { Refresh } from '@element-plus/icons-vue'
import AdminSection from '../../../components/AdminSection.vue'
import { can } from '../../../security/permissions'
import {
  mrpStokKimia,
  mrpStokMaterialLain,
  mrpStokRp,
  mrpUsageColor,
  mrpUsageColorCreate,
  mrpUsageColorScanLot,
  mrpUsageMaterial,
  mrpUsageMaterialCreate,
  mrpUsageMaterialScan,
  mrpUsageRp,
  mrpUsageRpCreate,
  mrpUsageRpScan,
} from '../../../api/client'

const { t } = useI18n()
const tab = ref('color')
const loading = ref(false)
const saving = ref(false)
const canCreate = computed(() => can('mrpShopfloor', 'create'))
const colorRows = ref([])
const colorWip = ref([])
const rpRows = ref([])
const rpWip = ref([])
const matRows = ref([])
const matWip = ref([])
const kimiaLots = ref([])
const rpLots = ref([])
const matLots = ref([])
const lotInfo = ref(null)
const rpInfo = ref(null)
const matInfo = ref(null)
const colorForm = reactive({ kode_lot_warna: '', kode_wip: '', qty_digunakan: 0, stok_in_id: null })
const rpForm = reactive({ jenis_rp: '', kode_wip: '', qty_used: 0, satuan: 'meter', stok_in_id: null })
const matForm = reactive({ kode_material: '', kode_wip: '', qty_used: 0, satuan: 'pcs', stok_in_id: null })

async function reload() {
  loading.value = true
  try {
    if (tab.value === 'color') {
      const [d, stok] = await Promise.all([mrpUsageColor(), mrpStokKimia()])
      colorRows.value = d.usage_list || []
      colorWip.value = d.wip_list || []
      kimiaLots.value = stok.stok_in || []
    } else if (tab.value === 'rp') {
      const [d, stok] = await Promise.all([mrpUsageRp(), mrpStokRp()])
      rpRows.value = d.usage_list || []
      rpWip.value = d.wip_list || []
      rpLots.value = stok.stok_in || []
    } else {
      const [d, stok] = await Promise.all([mrpUsageMaterial(), mrpStokMaterialLain()])
      matRows.value = d.usage_list || []
      matWip.value = d.wip_list || []
      matLots.value = stok.stok_in || []
    }
  } catch (e) {
    ElMessage.error(e.message || String(e))
  } finally {
    loading.value = false
  }
}
async function scanLot() {
  try {
    lotInfo.value = await mrpUsageColorScanLot(colorForm.kode_lot_warna)
  } catch (e) {
    lotInfo.value = null
    ElMessage.error(e.message || String(e))
  }
}
async function scanRp() {
  try {
    rpInfo.value = await mrpUsageRpScan(rpForm.jenis_rp)
    if (rpInfo.value?.satuan) rpForm.satuan = rpInfo.value.satuan
  } catch (e) {
    rpInfo.value = null
    ElMessage.error(e.message || String(e))
  }
}
async function scanMat() {
  try {
    matInfo.value = await mrpUsageMaterialScan(matForm.kode_material)
    if (matInfo.value?.satuan) matForm.satuan = matInfo.value.satuan
  } catch (e) {
    matInfo.value = null
    ElMessage.error(e.message || String(e))
  }
}
async function saveColor() {
  saving.value = true
  try {
    await mrpUsageColorCreate({ ...colorForm })
    ElMessage.success(t('common.saved'))
    await reload()
  } catch (e) {
    ElMessage.error(e.message || String(e))
  } finally {
    saving.value = false
  }
}
async function saveRp() {
  saving.value = true
  try {
    await mrpUsageRpCreate({ ...rpForm })
    ElMessage.success(t('common.saved'))
    await reload()
  } catch (e) {
    ElMessage.error(e.message || String(e))
  } finally {
    saving.value = false
  }
}
async function saveMat() {
  saving.value = true
  try {
    await mrpUsageMaterialCreate({ ...matForm })
    ElMessage.success(t('common.saved'))
    await reload()
  } catch (e) {
    ElMessage.error(e.message || String(e))
  } finally {
    saving.value = false
  }
}
watch(tab, reload)
onMounted(reload)
</script>
