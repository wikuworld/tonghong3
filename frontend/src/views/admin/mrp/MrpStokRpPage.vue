<template>
  <AdminSection :title="t('pages.mrpStokRp.title')" :subtitle="t('pages.mrpStokRp.subtitle')">
    <template #actions>
      <el-button :icon="Refresh" :loading="loading" @click="reload">{{ t('common.refresh') }}</el-button>
    </template>
    <div v-if="canCreate" class="admin-inner-card mb-4">
      <h3 class="admin-inner-card__title mb-2">IN</h3>
      <div class="flex flex-wrap gap-2">
        <el-select v-model="inForm.rp_id" filterable placeholder="RP" class="max-w-xs">
          <el-option v-for="r in rpList" :key="r.id" :label="`${r.kode_rp} — ${r.nama_rp}`" :value="r.id" />
        </el-select>
        <el-input v-model.number="inForm.meter_roll" type="number" placeholder="Meter" class="max-w-[120px]" />
        <el-date-picker v-model="inForm.tanggal" type="date" value-format="YYYY-MM-DD" />
        <el-button type="primary" :loading="saving" @click="doIn">IN</el-button>
      </div>
    </div>
    <div v-if="canUpdate" class="admin-inner-card mb-4">
      <h3 class="admin-inner-card__title mb-2">OUT</h3>
      <div class="flex flex-wrap gap-2">
        <el-select v-model="outForm.stok_in_id" filterable placeholder="Lot" class="max-w-md">
          <el-option v-for="s in stokIn" :key="s.id" :label="`${s.kode_internal} · ${s.nama_jenis} · sisa ${s.qty_sisa}`" :value="s.id" />
        </el-select>
        <el-input v-model.number="outForm.meter_roll" type="number" placeholder="Meter" class="max-w-[120px]" />
        <el-input v-model="outForm.kode_wip" placeholder="WIP" class="max-w-xs" />
        <el-button type="danger" :loading="saving" @click="doOut">OUT</el-button>
      </div>
    </div>
    <div class="admin-inner-card mb-4">
      <h3 class="admin-inner-card__title mb-2">{{ t('pages.mrpStokRp.stokIn') }}</h3>
      <el-table :data="stokIn" v-loading="loading" border stripe size="small">
        <el-table-column prop="kode_internal" label="BC" min-width="140" />
        <el-table-column prop="nama_jenis" label="RP" min-width="140" />
        <el-table-column prop="qty_sisa" label="Sisa" width="90" />
        <el-table-column prop="tanggal_in" :label="t('common.date')" width="120" />
      </el-table>
    </div>
    <div class="admin-inner-card">
      <h3 class="admin-inner-card__title mb-2">{{ t('pages.mrpStokRp.stokOut') }}</h3>
      <el-table :data="stokOut" border stripe size="small">
        <el-table-column prop="nama_jenis" label="RP" min-width="140" />
        <el-table-column prop="meter_roll" label="Meter" width="90" />
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
import { mrpStokRp, mrpStokRpAction } from '../../../api/client'

const { t } = useI18n()
const loading = ref(false)
const saving = ref(false)
const stokIn = ref([])
const stokOut = ref([])
const rpList = ref([])
const canCreate = computed(() => can('mrpShopfloor', 'create'))
const canUpdate = computed(() => can('mrpShopfloor', 'update'))
const inForm = reactive({ rp_id: null, meter_roll: 0, tanggal: new Date().toISOString().slice(0, 10) })
const outForm = reactive({ stok_in_id: null, meter_roll: 0, kode_wip: '', tanggal: new Date().toISOString().slice(0, 10) })

async function reload() {
  loading.value = true
  try {
    const data = await mrpStokRp()
    stokIn.value = data.stok_in || []
    stokOut.value = data.stok_out || []
    rpList.value = data.rp_list || []
  } catch (e) {
    ElMessage.error(e.message || String(e))
  } finally {
    loading.value = false
  }
}
async function doIn() {
  saving.value = true
  try {
    await mrpStokRpAction({ action: 'in', ...inForm })
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
    await mrpStokRpAction({ action: 'out', ...outForm })
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
