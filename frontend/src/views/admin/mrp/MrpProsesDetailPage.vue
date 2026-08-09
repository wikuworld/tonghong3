<template>
  <AdminSection :title="title" :subtitle="t('pages.mrpProses.detailSubtitle')">
    <template #actions>
      <el-button @click="$router.push('/admin/mrp/proses')">{{ t('common.close') }}</el-button>
      <el-button :icon="Refresh" :loading="loading" @click="reload">{{ t('common.refresh') }}</el-button>
      <el-button v-if="canUpdate && persiapan?.status === 'draft'" type="primary" @click="act('start')">
        Start
      </el-button>
      <el-button v-if="canUpdate && persiapan && persiapan.status !== 'saved'" type="success" @click="act('save')">
        {{ t('common.save') }}
      </el-button>
      <el-button v-if="persiapan" @click="printLabel">Label</el-button>
      <el-button v-if="canUpdate && persiapan" @click="act('reprint')">Reprint</el-button>
    </template>

    <div v-loading="loading" class="space-y-4">
      <div v-if="persiapan" class="admin-inner-card">
        <div class="grid grid-cols-2 md:grid-cols-4 gap-3 text-sm">
          <div><strong>Proses</strong><div>{{ persiapan.kode_proses }}</div></div>
          <div><strong>RPI</strong><div>{{ persiapan.kode_rencana }}</div></div>
          <div><strong>WIP</strong><div>{{ persiapan.kode_wip }}</div></div>
          <div><strong>{{ t('common.status') }}</strong><div>{{ persiapan.status }}</div></div>
          <div><strong>{{ t('common.color') }}</strong><div>{{ persiapan.warna }}</div></div>
          <div><strong>Thickness</strong><div>{{ persiapan.tebal }}</div></div>
          <div><strong>Treatment</strong><div>{{ persiapan.treatment_jenis }} — {{ persiapan.treatment_list }}</div></div>
          <div><strong>Total size</strong><div>{{ persiapan.total_size }}</div></div>
        </div>
      </div>

      <div v-if="canUpdate && persiapan && ['draft', 'started'].includes(persiapan.status)" class="admin-inner-card">
        <h3 class="admin-inner-card__title mb-2">{{ t('pages.mrpProses.kySession') }}</h3>
        <div class="grid grid-cols-2 md:grid-cols-4 gap-2 mb-3">
          <el-input v-model="kyForm.kode_palet" :placeholder="t('pages.mrpPalet.kodePalet')" />
          <el-input v-model="kyForm.kode_yl" placeholder="YL" />
          <el-input v-model="kyForm.target_qty" type="number" placeholder="Target qty" />
          <el-button type="primary" :disabled="!!activeKy" @click="scanKy">Aktifkan KY</el-button>
        </div>
        <div v-if="activeKy" class="grid grid-cols-2 md:grid-cols-4 gap-2">
          <el-input v-model="ukurVal" type="number" placeholder="Size ukur" />
          <el-button @click="addUkur">Tambah ukur</el-button>
          <el-button type="warning" @click="selesaiKy">Selesai KY</el-button>
        </div>
      </div>

      <div class="admin-inner-card">
        <h3 class="admin-inner-card__title mb-2">KY sessions</h3>
        <el-table :data="kySessions" border size="small">
          <el-table-column prop="kode_palet" :label="t('pages.mrpPalet.kodePalet')" />
          <el-table-column prop="kode_yl" label="YL" />
          <el-table-column prop="target_qty" label="Target" width="90" />
          <el-table-column prop="actual_qty" label="Aktual" width="90" />
          <el-table-column prop="status" :label="t('common.status')" width="100" />
        </el-table>
      </div>

      <div class="admin-inner-card">
        <h3 class="admin-inner-card__title mb-2">Ukur</h3>
        <el-table :data="ukurs" border size="small">
          <el-table-column prop="id" label="ID" width="70" />
          <el-table-column prop="ky_id" label="KY ID" width="80" />
          <el-table-column prop="size_val" label="Size" />
          <el-table-column prop="created_at" :label="t('common.date')" />
          <el-table-column v-if="canUpdate" :label="t('common.actions')" width="90">
            <template #default="{ row }">
              <el-button link type="danger" @click="deleteUkur(row.id)">{{ t('common.delete') }}</el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </div>
  </AdminSection>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Refresh } from '@element-plus/icons-vue'
import AdminSection from '../../../components/AdminSection.vue'
import { can } from '../../../security/permissions'
import { mrpGetProses, mrpProsesAction, mrpProsesLabel } from '../../../api/client'

const { t } = useI18n()
const route = useRoute()
const loading = ref(false)
const persiapan = ref(null)
const kySessions = ref([])
const ukurs = ref([])
const activeKy = ref(null)
const ukurVal = ref('')
const canUpdate = computed(() => can('mrpShopfloor', 'update'))
const title = computed(() => persiapan.value?.kode_proses || t('pages.mrpProses.title'))
const kyForm = reactive({ kode_palet: '', kode_yl: '', target_qty: 0 })

async function reload() {
  loading.value = true
  try {
    const data = await mrpGetProses(route.params.id)
    persiapan.value = data.persiapan
    kySessions.value = data.ky_sessions || []
    ukurs.value = data.ukurs || []
    activeKy.value = data.active_ky
  } catch (e) {
    ElMessage.error(e.message || String(e))
  } finally {
    loading.value = false
  }
}

async function act(action, extra = {}) {
  try {
    const res = await mrpProsesAction(route.params.id, { action, ...extra })
    ElMessage.success(res.message || t('common.saved'))
    await reload()
  } catch (e) {
    ElMessage.error(e.message || String(e))
  }
}

function scanKy() {
  return act('scan_ky', { ...kyForm })
}

function addUkur() {
  if (!activeKy.value) return
  return act('add_ukur', { ky_id: activeKy.value.id, size_val: Number(ukurVal.value) })
}

function selesaiKy() {
  if (!activeKy.value) return
  return act('selesai_ky', { ky_id: activeKy.value.id })
}

function deleteUkur(ukurId) {
  return act('delete_ukur', { ukur_id: ukurId })
}

async function printLabel() {
  try {
    const data = await mrpProsesLabel(route.params.id)
    const p = data.persiapan || {}
    const w = window.open('', '_blank')
    w.document.write(`
      <html><head><title>${p.kode_proses}</title>
      <style>body{font-family:sans-serif;padding:24px} h1{font-size:20px}</style></head>
      <body>
        <h1>Label Proses ${p.kode_proses || ''}</h1>
        <p>RPI: ${p.kode_rencana || ''}</p>
        <p>WIP: ${p.kode_wip || ''}</p>
        <p>PO: ${p.no_po || ''}</p>
        <p>Warna: ${p.warna || ''} / ${p.tebal || ''} / ${p.emboss || ''}</p>
        <p>Treatment: ${p.treatment_jenis || ''} — ${p.treatment_list || ''}</p>
        <p>Total size: ${p.total_size || 0}</p>
        <scr` + `ipt>window.print()</scr` + `ipt>
      </body></html>`)
    w.document.close()
  } catch (e) {
    ElMessage.error(e.message || String(e))
  }
}

onMounted(reload)
</script>
