<template>
  <AdminSection :title="t('pages.mrpPalet.title')" :subtitle="t('pages.mrpPalet.subtitle')">
    <template #actions>
      <el-button :icon="Refresh" :loading="loading" @click="reload">{{ t('common.refresh') }}</el-button>
      <el-button v-if="canCreate" type="primary" :icon="Plus" @click="openIn">{{ t('pages.mrpPalet.paletIn') }}</el-button>
      <el-button v-if="canUpdate" type="warning" @click="openPaletOut">{{ t('pages.mrpPalet.paletOut') }}</el-button>
      <el-button v-if="canUpdate" type="danger" @click="openYlOut">{{ t('pages.mrpPalet.ylOut') }}</el-button>
    </template>

    <div class="admin-inner-card mb-4">
      <h3 class="admin-inner-card__title mb-2">{{ t('pages.mrpPalet.movements') }}</h3>
      <el-table :data="movements" v-loading="loading" border stripe size="small" class="admin-table">
        <el-table-column type="index" width="56" :label="t('common.noLabel')" align="center" />
        <el-table-column prop="kode_palet" :label="t('pages.mrpPalet.kodePalet')" min-width="120" />
        <el-table-column prop="direction" label="IN/OUT" width="90" />
        <el-table-column prop="tanggal" :label="t('common.date')" width="120" />
        <el-table-column prop="jml_yl" label="YL" width="70" />
        <el-table-column prop="keterangan" :label="t('common.notes')" min-width="140" />
        <el-table-column :label="t('common.actions')" width="100">
          <template #default="{ row }">
            <el-button link type="primary" @click="showYl(row.kode_palet)">YL</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <div class="admin-inner-card">
      <h3 class="admin-inner-card__title mb-2">{{ t('pages.mrpPalet.ylStock') }}</h3>
      <el-table :data="ylRows" v-loading="loadingYl" border stripe size="small" class="admin-table">
        <el-table-column prop="kode_palet" :label="t('pages.mrpPalet.kodePalet')" min-width="120" />
        <el-table-column prop="kode_yl" label="YL" min-width="120" />
        <el-table-column prop="thickness" label="Thickness" width="100" />
        <el-table-column prop="warna" :label="t('common.color')" width="120" />
        <el-table-column prop="qty" label="Qty" width="90" />
      </el-table>
    </div>

    <el-dialog v-model="inOpen" :title="t('pages.mrpPalet.paletIn')" width="640px" destroy-on-close>
      <el-form label-position="top">
        <el-form-item :label="t('pages.mrpPalet.kodePalet')" required>
          <el-input v-model="form.kode_palet" />
        </el-form-item>
        <el-form-item :label="t('common.date')">
          <el-date-picker v-model="form.tanggal" type="date" value-format="YYYY-MM-DD" class="w-full" />
        </el-form-item>
        <el-form-item :label="t('common.notes')">
          <el-input v-model="form.keterangan" />
        </el-form-item>
        <div class="mb-2 flex justify-between">
          <strong>YL</strong>
          <el-button size="small" @click="form.items.push({ kode_yl: '', thickness: '', warna: '', qty: 0 })">
            {{ t('common.add') }}
          </el-button>
        </div>
        <div v-for="(item, idx) in form.items" :key="idx" class="mb-2 grid grid-cols-4 gap-2">
          <el-input v-model="item.kode_yl" placeholder="YL" />
          <el-input v-model="item.thickness" placeholder="Thickness" />
          <el-input v-model="item.warna" :placeholder="t('common.color')" />
          <el-input v-model="item.qty" type="number" placeholder="Qty" />
        </div>
      </el-form>
      <template #footer>
        <el-button @click="inOpen = false">{{ t('common.cancel') }}</el-button>
        <el-button type="primary" :loading="saving" @click="submitIn">{{ t('common.save') }}</el-button>
      </template>
    </el-dialog>

    <el-drawer v-model="ylOpen" :title="`YL · ${ylPalet}`" size="40%">
      <el-table :data="ylDetail" border size="small">
        <el-table-column prop="kode_yl" label="YL" />
        <el-table-column prop="thickness" label="Thickness" />
        <el-table-column prop="warna" :label="t('common.color')" />
        <el-table-column prop="qty" label="Qty" />
      </el-table>
    </el-drawer>

    <el-dialog v-model="paletOutOpen" :title="t('pages.mrpPalet.paletOut')" width="480px" destroy-on-close>
      <el-form label-position="top">
        <el-form-item :label="t('pages.mrpPalet.kodePalet')" required>
          <el-select v-model="paletOutForm.kode_palet" filterable allow-create class="w-full">
            <el-option
              v-for="k in paletCodes"
              :key="k"
              :label="k"
              :value="k"
            />
          </el-select>
        </el-form-item>
        <el-form-item :label="t('common.notes')">
          <el-input v-model="paletOutForm.keterangan" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="paletOutOpen = false">{{ t('common.cancel') }}</el-button>
        <el-button type="warning" :loading="saving" @click="submitPaletOut">OUT</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="ylOutOpen" :title="t('pages.mrpPalet.ylOut')" width="480px" destroy-on-close>
      <el-form label-position="top">
        <el-form-item label="YL" required>
          <el-select v-model="ylOutForm.kode_yl" filterable class="w-full" @change="onYlPick">
            <el-option
              v-for="y in ylRows"
              :key="`${y.kode_palet}-${y.kode_yl}`"
              :label="`${y.kode_yl} · ${y.kode_palet}`"
              :value="y.kode_yl"
            />
          </el-select>
        </el-form-item>
        <el-form-item :label="t('pages.mrpPalet.kodePalet')" required>
          <el-input v-model="ylOutForm.kode_palet" />
        </el-form-item>
        <el-form-item label="Qty">
          <el-input v-model.number="ylOutForm.qty" type="number" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="ylOutOpen = false">{{ t('common.cancel') }}</el-button>
        <el-button type="danger" :loading="saving" @click="submitYlOut">OUT</el-button>
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
const canCreate = computed(() => can('mrpShopfloor', 'create'))
const canUpdate = computed(() => can('mrpShopfloor', 'update'))
const paletCodes = computed(() => [...new Set(ylRows.value.map((y) => y.kode_palet).filter(Boolean))])
const inOpen = ref(false)
const ylOpen = ref(false)
const paletOutOpen = ref(false)
const ylOutOpen = ref(false)
const ylPalet = ref('')
const ylDetail = ref([])
const form = reactive({
  kode_palet: '',
  tanggal: new Date().toISOString().slice(0, 10),
  keterangan: '',
  items: [{ kode_yl: '', thickness: '', warna: '', qty: 0 }],
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
  qty: 0,
  tanggal: new Date().toISOString().slice(0, 10),
  direction: 'OUT',
})

async function reload() {
  loading.value = true
  loadingYl.value = true
  try {
    ;[movements.value, ylRows.value] = await Promise.all([mrpListPaletMovements(), mrpListYl()])
  } catch (e) {
    ElMessage.error(e.message || String(e))
  } finally {
    loading.value = false
    loadingYl.value = false
  }
}

function openIn() {
  form.kode_palet = ''
  form.tanggal = new Date().toISOString().slice(0, 10)
  form.keterangan = ''
  form.items = [{ kode_yl: '', thickness: '', warna: '', qty: 0 }]
  inOpen.value = true
}

async function submitIn() {
  saving.value = true
  try {
    await mrpPaletIn({ ...form })
    ElMessage.success(t('common.saved'))
    inOpen.value = false
    await reload()
  } catch (e) {
    ElMessage.error(e.message || String(e))
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
    ElMessage.error(e.message || String(e))
  }
}

function openPaletOut() {
  paletOutForm.kode_palet = paletCodes.value[0] || ''
  paletOutForm.tanggal = new Date().toISOString().slice(0, 10)
  paletOutForm.keterangan = ''
  paletOutOpen.value = true
}

async function submitPaletOut() {
  if (!paletOutForm.kode_palet.trim()) return
  saving.value = true
  try {
    await mrpPaletOut({ ...paletOutForm })
    ElMessage.success(t('common.saved'))
    paletOutOpen.value = false
    await reload()
  } catch (e) {
    ElMessage.error(e.message || String(e))
  } finally {
    saving.value = false
  }
}

function openYlOut() {
  ylOutForm.kode_yl = ''
  ylOutForm.kode_palet = ''
  ylOutForm.thickness = ''
  ylOutForm.warna = ''
  ylOutForm.qty = 0
  ylOutForm.tanggal = new Date().toISOString().slice(0, 10)
  ylOutOpen.value = true
}

function onYlPick(kode) {
  const y = ylRows.value.find((r) => r.kode_yl === kode)
  if (!y) return
  ylOutForm.kode_palet = y.kode_palet
  ylOutForm.thickness = y.thickness
  ylOutForm.warna = y.warna
  ylOutForm.qty = y.qty
}

async function submitYlOut() {
  saving.value = true
  try {
    await mrpYlMovement({ ...ylOutForm, direction: 'OUT' })
    ElMessage.success(t('common.saved'))
    ylOutOpen.value = false
    await reload()
  } catch (e) {
    ElMessage.error(e.message || String(e))
  } finally {
    saving.value = false
  }
}

onMounted(reload)
</script>
