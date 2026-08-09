<template>
  <AdminSection :title="t('pages.mrpPalet.title')" :subtitle="t('pages.mrpPalet.subtitle')">
    <template #actions>
      <el-button :icon="Refresh" :loading="loading" @click="reload">{{ t('common.refresh') }}</el-button>
      <el-button v-if="canCreate" type="primary" :icon="Plus" @click="openIn">{{ t('pages.mrpPalet.paletIn') }}</el-button>
      <el-button v-if="canUpdate" type="warning" @click="openPaletOut">{{ t('pages.mrpPalet.paletOut') }}</el-button>
      <el-button v-if="canUpdate" type="danger" @click="openYlOut">{{ t('pages.mrpPalet.ylOut') }}</el-button>
    </template>

    <div class="admin-inner-card mb-4">
      <div class="mrp-palet-list-head mb-3">
        <div>
          <h3 class="admin-inner-card__title mb-1">{{ t('pages.mrpPalet.movements') }}</h3>
          <p class="text-xs text-slate-500 mb-0">
            {{ t('pages.mrpPalet.statsMovements', { in: stats.in, out: stats.out, yl: ylRows.length }) }}
          </p>
        </div>
        <div class="flex gap-2 flex-wrap items-center">
          <el-radio-group v-model="directionFilter" size="small" @change="reload">
            <el-radio-button value="">{{ t('pages.mrpPalet.filterAll') }}</el-radio-button>
            <el-radio-button value="IN">IN</el-radio-button>
            <el-radio-button value="OUT">OUT</el-radio-button>
          </el-radio-group>
          <el-input
            v-model="searchMov"
            clearable
            size="small"
            class="w-52"
            :placeholder="t('pages.mrpPalet.searchMovements')"
          />
        </div>
      </div>
      <el-table
        :data="filteredMovements"
        v-loading="loading"
        border
        stripe
        size="small"
        class="admin-table"
        empty-text="—"
      >
        <el-table-column type="index" width="56" :label="t('common.noLabel')" align="center" />
        <el-table-column prop="kode_palet" :label="t('pages.mrpPalet.kodePalet')" min-width="130" show-overflow-tooltip />
        <el-table-column :label="t('pages.mrpPalet.direction')" width="90" align="center">
          <template #default="{ row }">
            <el-tag :type="row.direction === 'IN' ? 'success' : 'warning'" size="small" effect="plain">
              {{ row.direction || '—' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column :label="t('common.date')" width="120">
          <template #default="{ row }">{{ formatDate(row.tanggal) }}</template>
        </el-table-column>
        <el-table-column :label="t('pages.mrpPalet.ylCount')" width="80" align="right">
          <template #default="{ row }">{{ formatQty(row.jml_yl) }}</template>
        </el-table-column>
        <el-table-column :label="t('common.notes')" min-width="140" show-overflow-tooltip>
          <template #default="{ row }">{{ dash(row.keterangan) }}</template>
        </el-table-column>
        <el-table-column :label="t('common.actions')" width="100" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="showYl(row.kode_palet)">YL</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <div class="admin-inner-card">
      <div class="mrp-palet-list-head mb-3">
        <h3 class="admin-inner-card__title mb-0">{{ t('pages.mrpPalet.ylStock') }}</h3>
        <el-input
          v-model="searchYl"
          clearable
          size="small"
          class="w-56"
          :placeholder="t('pages.mrpPalet.searchYl')"
        />
      </div>
      <el-table
        :data="filteredYl"
        v-loading="loadingYl"
        border
        stripe
        size="small"
        class="admin-table"
        empty-text="—"
      >
        <el-table-column prop="kode_palet" :label="t('pages.mrpPalet.kodePalet')" min-width="120" show-overflow-tooltip />
        <el-table-column prop="kode_yl" label="YL" min-width="120" show-overflow-tooltip />
        <el-table-column :label="t('pages.mrpPalet.thickness')" width="100" show-overflow-tooltip>
          <template #default="{ row }">{{ dash(row.thickness) }}</template>
        </el-table-column>
        <el-table-column :label="t('common.color')" width="120" show-overflow-tooltip>
          <template #default="{ row }">{{ dash(row.warna) }}</template>
        </el-table-column>
        <el-table-column :label="t('pages.mrpPalet.qty')" width="90" align="right">
          <template #default="{ row }">{{ formatQty(row.qty) }}</template>
        </el-table-column>
        <el-table-column v-if="canUpdate" :label="t('common.actions')" width="100" fixed="right">
          <template #default="{ row }">
            <el-button link type="danger" @click="ylOutFromRow(row)">OUT</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <el-dialog v-model="inOpen" :title="t('pages.mrpPalet.paletIn')" width="720px" destroy-on-close append-to-body>
      <p class="text-sm text-slate-500 mb-3">{{ t('pages.mrpPalet.paletInHint') }}</p>
      <el-form label-position="top">
        <el-form-item :label="t('pages.mrpPalet.kodePalet')" required>
          <el-input v-model="form.kode_palet" :placeholder="t('pages.mrpPalet.kodePaletPlaceholder')" />
        </el-form-item>
        <el-form-item :label="t('common.date')">
          <el-date-picker v-model="form.tanggal" type="date" value-format="YYYY-MM-DD" class="w-full" />
        </el-form-item>
        <el-form-item :label="t('common.notes')">
          <el-input v-model="form.keterangan" />
        </el-form-item>
        <div class="mb-2 flex justify-between items-center">
          <strong>{{ t('pages.mrpPalet.ylItems') }}</strong>
          <el-button size="small" @click="form.items.push({ kode_yl: '', thickness: '', warna: '', qty: null })">
            {{ t('common.add') }}
          </el-button>
        </div>
        <div v-for="(item, idx) in form.items" :key="idx" class="mb-2 grid gap-2" style="grid-template-columns: 1.2fr 1fr 1fr 0.8fr auto;">
          <el-input v-model="item.kode_yl" placeholder="YL" />
          <el-input v-model="item.thickness" :placeholder="t('pages.mrpPalet.thickness')" />
          <el-input v-model="item.warna" :placeholder="t('common.color')" />
          <el-input v-model="item.qty" type="number" :placeholder="t('pages.mrpPalet.qty')" />
          <el-button
            link
            type="danger"
            :disabled="form.items.length <= 1"
            @click="form.items.splice(idx, 1)"
          >
            {{ t('common.delete') }}
          </el-button>
        </div>
      </el-form>
      <template #footer>
        <el-button @click="inOpen = false">{{ t('common.cancel') }}</el-button>
        <el-button type="primary" :loading="saving" @click="submitIn">{{ t('common.save') }}</el-button>
      </template>
    </el-dialog>

    <el-drawer v-model="ylOpen" :title="`${t('pages.mrpPalet.ylStock')} · ${ylPalet}`" size="42%">
      <el-table :data="ylDetail" border size="small" empty-text="—">
        <el-table-column prop="kode_yl" label="YL" min-width="110" />
        <el-table-column :label="t('pages.mrpPalet.thickness')" width="100">
          <template #default="{ row }">{{ dash(row.thickness) }}</template>
        </el-table-column>
        <el-table-column :label="t('common.color')" min-width="100">
          <template #default="{ row }">{{ dash(row.warna) }}</template>
        </el-table-column>
        <el-table-column :label="t('pages.mrpPalet.qty')" width="90" align="right">
          <template #default="{ row }">{{ formatQty(row.qty) }}</template>
        </el-table-column>
      </el-table>
    </el-drawer>

    <el-dialog v-model="paletOutOpen" :title="t('pages.mrpPalet.paletOut')" width="480px" destroy-on-close append-to-body>
      <p class="text-sm text-slate-500 mb-3">{{ t('pages.mrpPalet.paletOutHint') }}</p>
      <el-form label-position="top">
        <el-form-item :label="t('pages.mrpPalet.kodePalet')" required>
          <el-select v-model="paletOutForm.kode_palet" filterable allow-create default-first-option class="w-full">
            <el-option v-for="k in paletCodes" :key="k" :label="k" :value="k" />
          </el-select>
        </el-form-item>
        <el-form-item :label="t('common.notes')">
          <el-input v-model="paletOutForm.keterangan" />
        </el-form-item>
        <el-checkbox v-model="paletOutForm.clear_yl">{{ t('pages.mrpPalet.clearYl') }}</el-checkbox>
      </el-form>
      <template #footer>
        <el-button @click="paletOutOpen = false">{{ t('common.cancel') }}</el-button>
        <el-button type="warning" :loading="saving" @click="submitPaletOut">{{ t('pages.mrpPalet.paletOut') }}</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="ylOutOpen" :title="t('pages.mrpPalet.ylOut')" width="480px" destroy-on-close append-to-body>
      <p class="text-sm text-slate-500 mb-3">{{ t('pages.mrpPalet.ylOutHint') }}</p>
      <el-form label-position="top">
        <el-form-item label="YL" required>
          <el-select v-model="ylOutKey" filterable class="w-full" @change="onYlPick">
            <el-option
              v-for="y in ylRows"
              :key="`${y.kode_palet}::${y.kode_yl}`"
              :label="`${y.kode_yl} · ${y.kode_palet} (${formatQty(y.qty)})`"
              :value="`${y.kode_palet}::${y.kode_yl}`"
            />
          </el-select>
        </el-form-item>
        <el-form-item :label="t('pages.mrpPalet.kodePalet')" required>
          <el-input v-model="ylOutForm.kode_palet" disabled />
        </el-form-item>
        <el-form-item :label="t('pages.mrpPalet.qty')" required>
          <el-input v-model.number="ylOutForm.qty" type="number" :min="0" />
          <p v-if="ylOutForm.stok != null" class="text-xs text-slate-500 mt-1 mb-0">
            {{ t('pages.mrpPalet.stokHint', { qty: formatQty(ylOutForm.stok) }) }}
          </p>
        </el-form-item>
        <el-form-item :label="t('common.notes')">
          <el-input v-model="ylOutForm.keterangan" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="ylOutOpen = false">{{ t('common.cancel') }}</el-button>
        <el-button type="danger" :loading="saving" @click="submitYlOut">{{ t('pages.mrpPalet.ylOut') }}</el-button>
      </template>
    </el-dialog>
  </AdminSection>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Refresh } from '@element-plus/icons-vue'
import AdminSection from '../../../components/AdminSection.vue'
import { can } from '../../../security/permissions'
import {
  mrpListPaletMovements,
  mrpListYl,
  mrpPaletIn,
  mrpPaletOut,
  mrpPaletYl,
  mrpYlMovement,
} from '../../../api/client'

const { t } = useI18n()
const loading = ref(false)
const loadingYl = ref(false)
const saving = ref(false)
const movements = ref([])
const ylRows = ref([])
const searchMov = ref('')
const searchYl = ref('')
const directionFilter = ref('')
const canCreate = computed(() => can('mrpShopfloor', 'create'))
const canUpdate = computed(() => can('mrpShopfloor', 'update'))
const paletCodes = computed(() => [...new Set(ylRows.value.map((y) => y.kode_palet).filter(Boolean))])
const inOpen = ref(false)
const ylOpen = ref(false)
const paletOutOpen = ref(false)
const ylOutOpen = ref(false)
const ylPalet = ref('')
const ylDetail = ref([])
const ylOutKey = ref('')
const form = reactive({
  kode_palet: '',
  tanggal: new Date().toISOString().slice(0, 10),
  keterangan: '',
  items: [{ kode_yl: '', thickness: '', warna: '', qty: null }],
})
const paletOutForm = reactive({
  kode_palet: '',
  tanggal: new Date().toISOString().slice(0, 10),
  keterangan: '',
  clear_yl: true,
})
const ylOutForm = reactive({
  kode_yl: '',
  kode_palet: '',
  thickness: '',
  warna: '',
  qty: null,
  stok: null,
  tanggal: new Date().toISOString().slice(0, 10),
  keterangan: '',
  direction: 'OUT',
})

const filteredMovements = computed(() => {
  const q = searchMov.value.trim().toLowerCase()
  if (!q) return movements.value
  return movements.value.filter((r) =>
    [r.kode_palet, r.direction, r.keterangan].filter(Boolean).join(' ').toLowerCase().includes(q),
  )
})

const filteredYl = computed(() => {
  const q = searchYl.value.trim().toLowerCase()
  if (!q) return ylRows.value
  return ylRows.value.filter((r) =>
    [r.kode_palet, r.kode_yl, r.thickness, r.warna].filter(Boolean).join(' ').toLowerCase().includes(q),
  )
})

const stats = computed(() => ({
  in: (movements.value || []).filter((r) => r.direction === 'IN').length,
  out: (movements.value || []).filter((r) => r.direction === 'OUT').length,
}))

function dash(v) {
  const s = (v == null ? '' : String(v)).trim()
  return s || '—'
}

function formatQty(v) {
  const n = Number(v)
  if (!Number.isFinite(n)) return '—'
  return Number.isInteger(n) ? String(n) : n.toLocaleString(undefined, { maximumFractionDigits: 2 })
}

function formatDate(v) {
  if (!v) return '—'
  return String(v).slice(0, 10)
}

function errMsg(e) {
  const raw = e?.message || String(e)
  try {
    const j = JSON.parse(raw)
    const d = j?.detail
    if (typeof d === 'string') return d
    if (d && typeof d === 'object' && typeof d.detail === 'string') return d.detail
    if (typeof j?.message === 'string') return j.message
    return raw
  } catch {
    return raw
  }
}

async function reload() {
  loading.value = true
  loadingYl.value = true
  try {
    const params = {}
    if (directionFilter.value) params.direction = directionFilter.value
    ;[movements.value, ylRows.value] = await Promise.all([
      mrpListPaletMovements(params),
      mrpListYl(),
    ])
  } catch (e) {
    ElMessage.error(errMsg(e))
  } finally {
    loading.value = false
    loadingYl.value = false
  }
}

function openIn() {
  form.kode_palet = ''
  form.tanggal = new Date().toISOString().slice(0, 10)
  form.keterangan = ''
  form.items = [{ kode_yl: '', thickness: '', warna: '', qty: null }]
  inOpen.value = true
}

async function submitIn() {
  if (!form.kode_palet.trim()) {
    ElMessage.warning(t('pages.mrpPalet.kodePaletPlaceholder'))
    return
  }
  const items = form.items
    .map((it) => ({
      kode_yl: (it.kode_yl || '').trim(),
      thickness: (it.thickness || '').trim(),
      warna: (it.warna || '').trim(),
      qty: Number(it.qty),
    }))
    .filter((it) => it.kode_yl)
  if (!items.length || items.some((it) => !Number.isFinite(it.qty) || it.qty <= 0)) {
    ElMessage.warning(t('pages.mrpPalet.ylItemsInvalid'))
    return
  }
  saving.value = true
  try {
    const res = await mrpPaletIn({
      kode_palet: form.kode_palet.trim(),
      tanggal: form.tanggal,
      keterangan: form.keterangan.trim() || null,
      items,
    })
    ElMessage.success(t('pages.mrpPalet.paletInOk', { n: res?.yl_count || items.length }))
    inOpen.value = false
    await reload()
  } catch (e) {
    ElMessage.error(errMsg(e))
  } finally {
    saving.value = false
  }
}

async function showYl(kode) {
  ylPalet.value = kode
  try {
    ylDetail.value = await mrpPaletYl(kode)
    ylOpen.value = true
  } catch (e) {
    ElMessage.error(errMsg(e))
  }
}

function openPaletOut() {
  paletOutForm.kode_palet = paletCodes.value[0] || ''
  paletOutForm.tanggal = new Date().toISOString().slice(0, 10)
  paletOutForm.keterangan = ''
  paletOutForm.clear_yl = true
  paletOutOpen.value = true
}

async function submitPaletOut() {
  const kode = (paletOutForm.kode_palet || '').trim()
  if (!kode) {
    ElMessage.warning(t('pages.mrpPalet.kodePaletPlaceholder'))
    return
  }
  try {
    await ElMessageBox.confirm(
      t('pages.mrpPalet.paletOutConfirm', { kode }),
      t('pages.mrpPalet.paletOut'),
      { type: 'warning', confirmButtonText: t('pages.mrpPalet.paletOut'), cancelButtonText: t('common.cancel') },
    )
  } catch {
    return
  }
  saving.value = true
  try {
    const res = await mrpPaletOut({
      kode_palet: kode,
      tanggal: paletOutForm.tanggal,
      keterangan: paletOutForm.keterangan.trim() || null,
      clear_yl: !!paletOutForm.clear_yl,
    })
    ElMessage.success(
      t('pages.mrpPalet.paletOutOk', { n: res?.yl_cleared ?? 0 }),
    )
    paletOutOpen.value = false
    await reload()
  } catch (e) {
    ElMessage.error(errMsg(e))
  } finally {
    saving.value = false
  }
}

function openYlOut() {
  ylOutKey.value = ''
  ylOutForm.kode_yl = ''
  ylOutForm.kode_palet = ''
  ylOutForm.thickness = ''
  ylOutForm.warna = ''
  ylOutForm.qty = null
  ylOutForm.stok = null
  ylOutForm.keterangan = ''
  ylOutForm.tanggal = new Date().toISOString().slice(0, 10)
  ylOutOpen.value = true
}

function ylOutFromRow(row) {
  openYlOut()
  ylOutKey.value = `${row.kode_palet}::${row.kode_yl}`
  onYlPick(ylOutKey.value)
}

function onYlPick(key) {
  const [kodePalet, kodeYl] = String(key || '').split('::')
  const y = ylRows.value.find((r) => r.kode_palet === kodePalet && r.kode_yl === kodeYl)
  if (!y) return
  ylOutForm.kode_yl = y.kode_yl
  ylOutForm.kode_palet = y.kode_palet
  ylOutForm.thickness = y.thickness
  ylOutForm.warna = y.warna
  ylOutForm.stok = Number(y.qty) || 0
  ylOutForm.qty = ylOutForm.stok
}

async function submitYlOut() {
  if (!ylOutForm.kode_yl || !ylOutForm.kode_palet) {
    ElMessage.warning(t('pages.mrpPalet.ylPickRequired'))
    return
  }
  const qty = Number(ylOutForm.qty)
  if (!Number.isFinite(qty) || qty <= 0) {
    ElMessage.warning(t('pages.mrpPalet.qtyInvalid'))
    return
  }
  if (ylOutForm.stok != null && qty > Number(ylOutForm.stok)) {
    ElMessage.warning(t('pages.mrpPalet.qtyExceed', { stok: formatQty(ylOutForm.stok) }))
    return
  }
  saving.value = true
  try {
    await mrpYlMovement({
      kode_yl: ylOutForm.kode_yl,
      kode_palet: ylOutForm.kode_palet,
      thickness: ylOutForm.thickness,
      warna: ylOutForm.warna,
      qty,
      tanggal: ylOutForm.tanggal,
      keterangan: ylOutForm.keterangan.trim() || null,
      direction: 'OUT',
    })
    ElMessage.success(t('common.saved'))
    ylOutOpen.value = false
    await reload()
  } catch (e) {
    ElMessage.error(errMsg(e))
  } finally {
    saving.value = false
  }
}

onMounted(reload)
</script>

<style scoped>
.w-52 {
  width: 13rem;
}
.w-56 {
  width: 14rem;
}
.mrp-palet-list-head {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  align-items: flex-start;
  justify-content: space-between;
}
</style>
