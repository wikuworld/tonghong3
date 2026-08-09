<template>
  <AdminSection :title="t('pages.mrpCheckpoint.title')" :subtitle="t('pages.mrpCheckpoint.subtitle')">
    <template #actions>
      <el-button :icon="Refresh" :loading="loading" @click="reload">{{ t('common.refresh') }}</el-button>
    </template>

    <div v-if="canCreate" class="admin-inner-card mb-4">
      <h3 class="admin-inner-card__title mb-2">{{ t('common.add') }}</h3>
      <div class="grid gap-2 sm:grid-cols-2 lg:grid-cols-3">
        <el-input v-model="form.kode_wip" :placeholder="t('pages.mrpCheckpoint.wip')" />
        <el-input v-model="form.thickness_actual" :placeholder="t('pages.mrpCheckpoint.thickness')" />
        <el-input v-model="form.softness_actual" :placeholder="t('pages.mrpCheckpoint.softness')" />
        <el-select v-model="form.result" :placeholder="t('pages.mrpCheckpoint.result')" class="w-full">
          <el-option label="OK" value="OK" />
          <el-option label="NG" value="NG" />
        </el-select>
        <el-input v-model="form.remark" :placeholder="t('common.notes')" />
        <el-button type="primary" :loading="saving" @click="save">{{ t('common.save') }}</el-button>
      </div>
    </div>

    <div class="admin-inner-card">
      <el-table :data="rows" v-loading="loading" border stripe size="small" class="admin-table">
        <el-table-column type="index" width="56" :label="t('common.noLabel')" align="center" />
        <el-table-column prop="kode_wip" :label="t('pages.mrpCheckpoint.wip')" min-width="130" />
        <el-table-column prop="thickness_actual" :label="t('pages.mrpCheckpoint.thickness')" width="110" />
        <el-table-column prop="softness_actual" :label="t('pages.mrpCheckpoint.softness')" width="110" />
        <el-table-column prop="result" :label="t('pages.mrpCheckpoint.result')" width="90" />
        <el-table-column prop="erp_production_detail_id" label="Prod Detail" width="110" />
        <el-table-column prop="erp_qc_detail_id" label="QC Detail" width="100" />
        <el-table-column prop="measured_at" :label="t('common.date')" min-width="140" />
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
import { apiFetch } from '../../../api/client'

const { t } = useI18n()
const loading = ref(false)
const saving = ref(false)
const rows = ref([])
const canCreate = computed(() => can('mrpShopfloor', 'create'))
const form = reactive({
  kode_wip: '',
  thickness_actual: '',
  softness_actual: '',
  result: 'OK',
  remark: '',
})

async function reload() {
  loading.value = true
  try {
    rows.value = await apiFetch('/mrp/checkpoint')
  } catch (e) {
    ElMessage.error(e.message || String(e))
  } finally {
    loading.value = false
  }
}

async function save() {
  if (!form.kode_wip.trim()) return
  saving.value = true
  try {
    await apiFetch('/mrp/checkpoint', {
      method: 'POST',
      body: JSON.stringify({
        kode_wip: form.kode_wip.trim(),
        thickness_actual: form.thickness_actual || null,
        softness_actual: form.softness_actual || null,
        result: form.result,
        is_ok: form.result === 'OK',
        remark: form.remark || null,
      }),
    })
    ElMessage.success(t('common.saved'))
    form.kode_wip = ''
    form.thickness_actual = ''
    form.softness_actual = ''
    form.remark = ''
    await reload()
  } catch (e) {
    ElMessage.error(e.message || String(e))
  } finally {
    saving.value = false
  }
}

onMounted(reload)
</script>
