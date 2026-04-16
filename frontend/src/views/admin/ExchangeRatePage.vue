<template>
  <div class="space-y-4">
    <AdminSection :title="t('pages.exchangeRate.title')" :subtitle="t('pages.exchangeRate.subtitle')">
      <template #actions>
        <el-button type="primary" @click="openDialog">{{ t('pages.exchangeRate.create') }}</el-button>
      </template>
      <el-table :data="rows" v-loading="loading" border stripe size="small" class="admin-table" table-layout="fixed" :empty-text="t('pages.exchangeRate.tableEmpty')">
        <el-table-column prop="effective_date" :label="t('pages.exchangeRate.effectiveDate')" width="120" />
        <el-table-column prop="idr_per_usd" :label="t('pages.exchangeRate.idrPerUsd')" min-width="140">
          <template #default="{ row }">{{ formatNum(row.idr_per_usd) }}</template>
        </el-table-column>
        <el-table-column prop="created_by" :label="t('pages.exchangeRate.createdBy')" width="100" />
        <el-table-column prop="notes" :label="t('common.remark')" min-width="200" show-overflow-tooltip />
      </el-table>
    </AdminSection>

    <el-dialog v-model="dialog" :title="t('pages.exchangeRate.dialogTitle')" width="600px" destroy-on-close align-center @closed="resetForm">
      <el-form label-position="top">
        <el-form-item :label="t('pages.exchangeRate.idrPerUsdForm')" required>
          <el-input-number v-model="form.idr_per_usd" :min="1" :step="100" class="w-full" controls-position="right" />
        </el-form-item>
        <el-form-item :label="t('pages.exchangeRate.effectiveDate')" required>
          <el-date-picker v-model="form.effective_date" type="date" value-format="YYYY-MM-DD" class="w-full" />
        </el-form-item>
        <el-row :gutter="12">
          <el-col :span="12">
            <el-form-item :label="t('pages.exchangeRate.validFrom')">
              <el-date-picker v-model="form.valid_from" type="date" value-format="YYYY-MM-DD" class="w-full" clearable />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item :label="t('pages.exchangeRate.validTo')">
              <el-date-picker v-model="form.valid_to" type="date" value-format="YYYY-MM-DD" class="w-full" clearable />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item :label="t('common.remark')">
          <el-input v-model="form.notes" type="textarea" rows="2" />
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="exchange-rate-dialog-footer">
          <el-button @click="dialog = false">{{ t('common.cancel') }}</el-button>
          <el-button type="primary" :loading="saving" @click="submit">{{ t('common.save') }}</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import AdminSection from '../../components/AdminSection.vue'
import { createExchangeRate, listExchangeRates } from '../../api/client'

const { t } = useI18n()
const rows = ref([])
const loading = ref(false)
const dialog = ref(false)
const saving = ref(false)
const form = ref({ idr_per_usd: 16000, effective_date: '', valid_from: '', valid_to: '', notes: '' })

function formatNum(v) {
  if (v == null) return ''
  return Number(v).toLocaleString('id-ID')
}

async function load() {
  loading.value = true
  try {
    rows.value = await listExchangeRates()
  } finally {
    loading.value = false
  }
}

function openDialog() {
  const d = new Date()
  form.value = {
    idr_per_usd: 16000,
    effective_date: d.toISOString().slice(0, 10),
    valid_from: '',
    valid_to: '',
    notes: '',
  }
  dialog.value = true
}

function resetForm() {
  form.value = { idr_per_usd: 16000, effective_date: '', valid_from: '', valid_to: '', notes: '' }
}

async function submit() {
  saving.value = true
  try {
    await createExchangeRate({
      idr_per_usd: form.value.idr_per_usd,
      effective_date: form.value.effective_date,
      valid_from: form.value.valid_from || undefined,
      valid_to: form.value.valid_to || undefined,
      notes: form.value.notes || null,
      created_by: 'exim',
    })
    dialog.value = false
    await load()
  } finally {
    saving.value = false
  }
}

onMounted(load)
</script>

<style scoped>
.exchange-rate-dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}
</style>
