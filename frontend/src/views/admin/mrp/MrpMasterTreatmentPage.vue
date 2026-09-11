<template>
  <AdminSection :title="t('pages.mrpMasterTreatment.title')" :subtitle="t('pages.mrpMasterTreatment.subtitle')">
    <template #actions>
      <span v-if="loading" class="text-xs text-slate-500">{{ t('common.loadingData') }}</span>
      <el-button :icon="Refresh" :loading="loading" @click="reload">{{ t('common.refresh') }}</el-button>
      <el-button v-if="canCreate" type="primary" :icon="Plus" @click="openCreate">{{ t('common.create') }}</el-button>
    </template>

    <div class="admin-inner-card">
      <div class="admin-inner-card__head">
        <div>
          <h3 class="admin-inner-card__title">{{ t('pages.mrpMasterTreatment.listSectionTitle') }}</h3>
          <p class="admin-inner-card__sub">{{ t('pages.mrpMasterTreatment.listSubtitle') }}</p>
        </div>
      </div>
      <div class="mkt-section-body">
        <p class="admin-scroll-hint">{{ t('pages.mrpMasterTreatment.scrollHint') }}</p>
        <div class="admin-table-scroll">
      <el-table :data="rows" v-loading="loading" border stripe size="small" class="admin-table" :empty-text="t('pages.mrpMasterTreatment.tableEmpty')">
        <el-table-column type="index" width="56" :label="t('common.noLabel')" align="center" />
        <el-table-column prop="jenis" :label="t('pages.mrpMasterTreatment.jenis')" width="100" />
        <el-table-column prop="nama_treatment" :label="t('common.name')" min-width="180" />
        <el-table-column prop="created_at" :label="t('common.date')" min-width="140" />
        <el-table-column v-if="canCreate" :label="t('common.actions')" width="160" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="openEdit(row)">{{ t('common.edit') }}</el-button>
            <el-button link type="danger" @click="remove(row)">{{ t('common.delete') }}</el-button>
          </template>
        </el-table-column>
      </el-table>
        </div>
      </div>
    </div>

    <el-dialog v-model="dialogOpen" :title="editId ? t('common.edit') : t('common.create')" width="420px" destroy-on-close>
      <el-form label-position="top">
        <el-form-item :label="t('pages.mrpMasterTreatment.jenis')" required>
          <el-select v-model="form.jenis" class="w-full">
            <el-option label="PU" value="PU" />
            <el-option label="Suede" value="Suede" />
          </el-select>
        </el-form-item>
        <el-form-item :label="t('common.name')" required>
          <el-input v-model="form.nama_treatment" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogOpen = false">{{ t('common.cancel') }}</el-button>
        <el-button type="primary" :loading="saving" @click="submit">{{ t('common.save') }}</el-button>
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
  mrpCreateTreatment,
  mrpDeleteTreatment,
  mrpListTreatment,
  mrpUpdateTreatment,
} from '../../../api/client'

const { t } = useI18n()
const loading = ref(false)
const saving = ref(false)
const dialogOpen = ref(false)
const editId = ref(null)
const rows = ref([])
const canCreate = computed(() => can('mrpShopfloor', 'create'))
const form = reactive({ jenis: 'PU', nama_treatment: '' })

async function reload() {
  loading.value = true
  try {
    rows.value = await mrpListTreatment()
  } catch (e) {
    ElMessage.error(e.message || String(e))
  } finally {
    loading.value = false
  }
}

function openCreate() {
  editId.value = null
  form.jenis = 'PU'
  form.nama_treatment = ''
  dialogOpen.value = true
}

function openEdit(row) {
  editId.value = row.id
  form.jenis = row.jenis
  form.nama_treatment = row.nama_treatment
  dialogOpen.value = true
}

async function submit() {
  saving.value = true
  try {
    if (editId.value) await mrpUpdateTreatment(editId.value, { ...form })
    else await mrpCreateTreatment({ ...form })
    ElMessage.success(t('common.saved'))
    dialogOpen.value = false
    await reload()
  } catch (e) {
    ElMessage.error(e.message || String(e))
  } finally {
    saving.value = false
  }
}

async function remove(row) {
  try {
    await ElMessageBox.confirm(t('common.confirm'), { type: 'warning' })
    await mrpDeleteTreatment(row.id)
    ElMessage.success(t('common.saved'))
    await reload()
  } catch (e) {
    if (e !== 'cancel') ElMessage.error(e.message || String(e))
  }
}

onMounted(reload)
</script>
