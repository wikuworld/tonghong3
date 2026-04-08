<template>
  <div class="space-y-4">
    <AdminSection title="Kurs USD → IDR">
      <template #actions>
        <el-button type="primary" @click="openDialog">+ Kurs baru</el-button>
      </template>
      <el-table :data="rows" v-loading="loading" border stripe size="small">
        <el-table-column prop="effective_date" label="Berlaku" width="120" />
        <el-table-column prop="idr_per_usd" label="1 USD = (IDR)" min-width="140">
          <template #default="{ row }">{{ formatNum(row.idr_per_usd) }}</template>
        </el-table-column>
        <el-table-column prop="created_by" label="Oleh" width="100" />
        <el-table-column prop="notes" label="Catatan" min-width="200" show-overflow-tooltip />
      </el-table>
    </AdminSection>

    <el-dialog v-model="dialog" title="Input kurs" width="420px" @closed="resetForm">
      <el-form label-position="top">
        <el-form-item label="IDR per 1 USD" required>
          <el-input-number v-model="form.idr_per_usd" :min="1" :step="100" class="w-full" controls-position="right" />
        </el-form-item>
        <el-form-item label="Tanggal efektif" required>
          <el-date-picker v-model="form.effective_date" type="date" value-format="YYYY-MM-DD" class="w-full" />
        </el-form-item>
        <el-form-item label="Catatan">
          <el-input v-model="form.notes" type="textarea" rows="2" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialog = false">Batal</el-button>
        <el-button type="primary" :loading="saving" @click="submit">Simpan</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import AdminSection from '../../components/AdminSection.vue'
import { createExchangeRate, listExchangeRates } from '../../api/client'

const rows = ref([])
const loading = ref(false)
const dialog = ref(false)
const saving = ref(false)
const form = ref({ idr_per_usd: 16000, effective_date: '', notes: '' })

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
    notes: '',
  }
  dialog.value = true
}

function resetForm() {
  form.value = { idr_per_usd: 16000, effective_date: '', notes: '' }
}

async function submit() {
  saving.value = true
  try {
    await createExchangeRate({
      idr_per_usd: form.value.idr_per_usd,
      effective_date: form.value.effective_date,
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
