<template>
  <AdminSection :title="t('pages.delivery.title')" :subtitle="t('pages.delivery.subtitle')">
    <template #actions>
      <el-input v-model="keyword" :placeholder="t('pages.delivery.searchPlaceholder')" clearable class="delivery-toolbar-search" />
      <el-button :icon="Van" @click="ElMessage.info('Alur: QC OK → Packing done → Delivery + detail → status sent → Invoice.')">{{ t('menu.deliveryPull') }}</el-button>
      <el-button :icon="Document" @click="ElMessage.info('Surat jalan: cetak dari detail delivery.')">{{ t('menu.suratJalan') }}</el-button>
      <el-button type="primary" :icon="Plus" :loading="loading" @click="openCreate">{{ t('common.create') }}</el-button>
    </template>

    <p class="mb-3 text-sm text-slate-600">
      Buat delivery hanya dari <b>packing selesai (done)</b>. Isi baris detail (QC OK) lalu set status <code class="rounded bg-slate-100 px-1">sent</code> sebelum invoice.
    </p>

    <el-table :data="filteredRows" v-loading="loading" border stripe size="small" class="admin-table" :empty-text="t('pages.delivery.tableEmpty')">
      <el-table-column type="index" :label="t('common.noLabel')" width="56" align="center" />
      <el-table-column prop="delivery_number" :label="t('common.deliveryNo')" min-width="160" />
      <el-table-column prop="customer_name" :label="t('common.customer')" min-width="200" />
      <el-table-column prop="delivery_date" :label="t('common.date')" width="120" />
      <el-table-column prop="vehicle_number" :label="t('common.vehicle')" min-width="120" />
      <el-table-column prop="driver_name" :label="t('common.driver')" min-width="120" />
      <el-table-column prop="status" :label="t('common.status')" width="100" />
      <el-table-column :label="t('common.actions')" width="100" fixed="right">
        <template #default="{ row }">
          <el-button :icon="View" link type="primary" @click="openDetail(row)" />
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="formVisible" :title="`${t('common.create')} ${t('menu.delivery')}`" width="560px" destroy-on-close>
      <el-form label-position="top">
        <el-form-item :label="t('common.customer')" required>
          <el-select v-model="form.customer_id" filterable class="w-full">
            <el-option
              v-for="c in customers"
              :key="c.id"
              :label="(c.code || '') + ' — ' + (c.name || '') + (c.city ? ' · ' + c.city : '')"
              :value="c.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="Packing (wajib, status done)" required>
          <el-select v-model="form.packing_id" filterable class="w-full" placeholder="Pilih packing selesai">
            <el-option
              v-for="p in packingsDone"
              :key="p.id"
              :label="`${p.packing_number || p.id} (${p.status})`"
              :value="p.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item :label="t('common.date')">
          <el-date-picker v-model="form.delivery_date" type="date" class="w-full" value-format="YYYY-MM-DD" />
        </el-form-item>
        <el-form-item :label="t('common.vehicle')">
          <el-input v-model="form.vehicle_number" />
        </el-form-item>
        <el-form-item :label="t('common.driver')">
          <el-input v-model="form.driver_name" />
        </el-form-item>
        <el-form-item :label="t('common.status')">
          <el-select v-model="form.status" class="w-full" disabled>
            <el-option :label="t('status.draft')" value="draft" />
          </el-select>
          <span class="mt-1 block text-xs text-slate-500">Setelah ada detail, buka detail delivery dan klik «Tandai terkirim».</span>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="formVisible = false">{{ t('common.cancel') }}</el-button>
        <el-button type="primary" :loading="saving" @click="submit">{{ t('common.save') }}</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="detailVisible" :title="t('pages.delivery.dialogDetail')" width="640px" destroy-on-close @closed="resetDetail">
      <template v-if="detailRow">
        <el-descriptions :column="1" border size="small" class="mb-4">
          <el-descriptions-item :label="t('common.deliveryNo')">{{ detailRow.delivery_number }}</el-descriptions-item>
          <el-descriptions-item :label="t('common.customer')">{{ detailRow.customer_name }}</el-descriptions-item>
          <el-descriptions-item :label="t('common.date')">{{ detailRow.delivery_date }}</el-descriptions-item>
          <el-descriptions-item :label="t('common.vehicle')">{{ detailRow.vehicle_number }}</el-descriptions-item>
          <el-descriptions-item :label="t('common.driver')">{{ detailRow.driver_name }}</el-descriptions-item>
          <el-descriptions-item :label="t('common.status')">{{ detailRow.status }}</el-descriptions-item>
        </el-descriptions>

        <div class="mb-2 flex flex-wrap items-center gap-2">
          <el-button
            type="primary"
            :disabled="(detailRow.status || '').toLowerCase() === 'sent' || detailLines.length === 0"
            :loading="markingSent"
            @click="markSent"
          >
            Tandai terkirim (sent)
          </el-button>
          <el-button @click="openSjPrint">Cetak Surat Jalan</el-button>
          <el-button type="success" plain :loading="markingSj" @click="markSjPrinted">Tandai SJ dicetak</el-button>
          <span v-if="detailLines.length === 0" class="text-xs text-amber-600">Tambah minimal satu baris detail dulu.</span>
        </div>

        <h4 class="mb-2 text-sm font-medium text-slate-700">Baris delivery</h4>
        <el-table :data="detailLines" border size="small" class="mb-4" empty-text="Belum ada baris">
          <el-table-column prop="id" label="ID" width="64" />
          <el-table-column prop="production_detail_id" label="Prod. detail ID" min-width="120" />
          <el-table-column prop="qty" label="Qty" width="100" align="right" />
        </el-table>

        <el-form v-if="candidateProdDetails.length" label-position="top" class="border-t border-slate-100 pt-3">
          <el-form-item label="Tambah baris (hanya QC OK — validasi server)">
            <el-select v-model="lineForm.production_detail_id" filterable clearable class="w-full" placeholder="Production detail">
              <el-option
                v-for="pd in candidateProdDetails"
                :key="pd.id"
                :label="`#${pd.id} · aktual ${pd.qty_actual ?? '—'}`"
                :value="pd.id"
              />
            </el-select>
          </el-form-item>
          <el-form-item label="Qty">
            <el-input v-model="lineForm.qty" type="number" step="0.01" />
          </el-form-item>
          <el-button type="primary" :loading="addingLine" @click="addLine">Tambah ke delivery</el-button>
        </el-form>
        <p v-else-if="detailRow && detailLoading === false" class="text-sm text-slate-500">
          Tidak ada daftar baris produksi (pastikan packing punya production).
        </p>
      </template>
      <template #footer>
        <el-button type="primary" @click="detailVisible = false">{{ t('pages.delivery.closeDetail') }}</el-button>
      </template>
    </el-dialog>
  </AdminSection>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Plus, View, Van, Document } from '@element-plus/icons-vue'
import AdminSection from '../../components/AdminSection.vue'
import {
  addDeliveryDetail,
  createDelivery,
  getPacking,
  listCustomers,
  listDelivery,
  listDeliveryDetails,
  listPacking,
  listProductionDetails,
  markSuratJalanPrinted,
  toIsoDate,
  updateDelivery,
} from '../../api/client'

const { t } = useI18n()
const route = useRoute()
const loading = ref(false)
const saving = ref(false)
const keyword = ref('')
const rows = ref([])
const customers = ref([])
const packings = ref([])

const packingsDone = computed(() =>
  (packings.value || []).filter((p) => (p.status || '').toLowerCase() === 'done'),
)

function custName(id) {
  const c = customers.value.find((x) => x.id === id)
  return c ? `${c.name}` : '—'
}

async function load() {
  loading.value = true
  try {
    const [del, cust, pack] = await Promise.all([listDelivery(), listCustomers(), listPacking()])
    customers.value = cust
    packings.value = pack
    rows.value = del.map((r) => ({
      ...r,
      customer_name: custName(r.customer_id),
      delivery_date: r.delivery_date ? String(r.delivery_date).slice(0, 10) : '',
    }))
  } catch (e) {
    ElMessage.error(e.message || 'Error')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  const kw = route.query.keyword
  if (kw != null && String(kw).trim()) keyword.value = String(kw).trim()
  load()
})

const filteredRows = computed(() => {
  const q = keyword.value.trim().toLowerCase()
  if (!q) return rows.value
  return rows.value.filter((r) => JSON.stringify(r).toLowerCase().includes(q))
})

const formVisible = ref(false)
const form = reactive({
  customer_id: null,
  packing_id: null,
  delivery_date: '',
  vehicle_number: '',
  driver_name: '',
  status: 'draft',
})

function openCreate() {
  form.customer_id = null
  form.packing_id = null
  form.delivery_date = ''
  form.vehicle_number = ''
  form.driver_name = ''
  form.status = 'draft'
  formVisible.value = true
}

async function submit() {
  if (!form.customer_id) {
    ElMessage.warning('Pilih customer')
    return
  }
  if (!form.packing_id) {
    ElMessage.warning('Pilih packing (status done)')
    return
  }
  saving.value = true
  try {
    await createDelivery({
      customer_id: form.customer_id,
      packing_id: form.packing_id,
      delivery_date: toIsoDate(form.delivery_date) || undefined,
      vehicle_number: form.vehicle_number || undefined,
      driver_name: form.driver_name || undefined,
      status: 'draft',
    })
    ElMessage.success(t('pages.delivery.saved'))
    formVisible.value = false
    await load()
  } catch (e) {
    ElMessage.error(e.message || 'Error')
  } finally {
    saving.value = false
  }
}

const detailVisible = ref(false)
const detailRow = ref(null)
const detailLines = ref([])
const candidateProdDetails = ref([])
const detailLoading = ref(false)
const markingSent = ref(false)
const markingSj = ref(false)
const addingLine = ref(false)

const lineForm = reactive({
  production_detail_id: null,
  qty: '',
})

function resetDetail() {
  detailLines.value = []
  candidateProdDetails.value = []
  lineForm.production_detail_id = null
  lineForm.qty = ''
}

async function openDetail(row) {
  detailRow.value = { ...row, customer_name: custName(row.customer_id) }
  detailVisible.value = true
  detailLoading.value = true
  resetDetail()
  try {
    const lines = await listDeliveryDetails(row.id)
    detailLines.value = lines
    if (row.packing_id) {
      const pk = await getPacking(row.packing_id)
      if (pk?.production_id) {
        const pds = await listProductionDetails(pk.production_id)
        candidateProdDetails.value = pds
      }
    }
  } catch (e) {
    ElMessage.error(e.message || 'Error')
  } finally {
    detailLoading.value = false
  }
}

function openSjPrint() {
  if (!detailRow.value?.id) return
  window.open(`${window.location.origin}/api/v1/documents/surat-jalan/${detailRow.value.id}`, '_blank')
}

async function markSjPrinted() {
  if (!detailRow.value?.id) return
  markingSj.value = true
  try {
    await markSuratJalanPrinted(detailRow.value.id)
    ElMessage.success('Surat jalan ditandai sudah dicetak')
  } catch (e) {
    ElMessage.error(e.message || 'Error')
  } finally {
    markingSj.value = false
  }
}

async function markSent() {
  if (!detailRow.value?.id) return
  markingSent.value = true
  try {
    await updateDelivery(detailRow.value.id, { status: 'sent' })
    ElMessage.success('Delivery ditandai terkirim')
    detailVisible.value = false
    await load()
  } catch (e) {
    ElMessage.error(e.message || 'Error')
  } finally {
    markingSent.value = false
  }
}

async function addLine() {
  if (!detailRow.value?.id || !lineForm.production_detail_id) {
    ElMessage.warning('Pilih production detail')
    return
  }
  addingLine.value = true
  try {
    await addDeliveryDetail(detailRow.value.id, {
      production_detail_id: lineForm.production_detail_id,
      qty: lineForm.qty ? Number(lineForm.qty) : undefined,
    })
    ElMessage.success('Baris ditambahkan')
    detailLines.value = await listDeliveryDetails(detailRow.value.id)
    lineForm.production_detail_id = null
    lineForm.qty = ''
  } catch (e) {
    ElMessage.error(e.message || 'Error')
  } finally {
    addingLine.value = false
  }
}
</script>

<style scoped>
.admin-table {
  width: 100%;
}
</style>
