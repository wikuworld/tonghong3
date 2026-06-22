<template>
  <AdminSection :title="t('pages.journalEntries.title')" :subtitle="t('pages.journalEntries.subtitle')">
    <template #actions>
      <el-button type="primary" :icon="Plus" @click="openGenerate">{{ t('pages.journalEntries.generateFromTransaction') }}</el-button>
      <el-button :icon="Refresh" @click="showTrialBalance = true">{{ t('pages.journalEntries.showTrialBalance') }}</el-button>
    </template>

    <div class="flex flex-wrap gap-2 mb-4 items-center">
      <el-date-picker
        v-model="filterDateRange"
        type="daterange"
        :range-separator="t('common.dashSeparator')"
        :start-placeholder="t('common.startDate')"
        :end-placeholder="t('common.endDate')"
        format="YYYY-MM-DD"
        value-format="YYYY-MM-DD"
        class="w-72"
        :shortcuts="dateShortcuts"
        unlink-panels
      />
      <el-select v-model="filterType" :placeholder="t('pages.journalEntries.filterTransactionType')" clearable class="w-40">
        <el-option :label="t('pages.journalEntries.allTransactionTypes')" value="" />
        <el-option :label="t('pages.journalEntries.po_created')" value="po_created" />
        <el-option :label="t('pages.journalEntries.invoice')" value="invoice" />
        <el-option :label="t('pages.journalEntries.payment')" value="payment" />
      </el-select>
      <el-button type="primary" :icon="Search" @click="loadEntries">{{ t('common.search') }}</el-button>
    </div>

    <el-table :data="entries" v-loading="loading" border stripe size="small" class="admin-table" table-layout="fixed" :empty-text="t('pages.journalEntries.tableEmpty')">
      <el-table-column type="index" :label="t('common.noLabel')" width="56" align="center" />
      <el-table-column prop="entry_date" :label="t('pages.journalEntries.entryDate')" width="120">
        <template #default="{ row }">{{ row.entry_date }}</template>
      </el-table-column>
      <el-table-column prop="transaction_type" :label="t('pages.journalEntries.transactionType')" width="140">
        <template #default="{ row }">
          {{ t(`pages.journalEntries.${row.transaction_type}`) }}
        </template>
      </el-table-column>
      <el-table-column prop="transaction_id" :label="t('pages.journalEntries.transactionId')" width="100" align="right" />
      <el-table-column prop="coa_code" :label="t('pages.journalEntries.coaCode')" width="100" />
      <el-table-column prop="coa_name" :label="t('pages.journalEntries.coaName')" min-width="180" />
      <el-table-column prop="debit" :label="t('pages.journalEntries.debit')" width="140" align="right">
        <template #default="{ row }">{{ formatCurrency(row.debit) }}</template>
      </el-table-column>
      <el-table-column prop="credit" :label="t('pages.journalEntries.credit')" width="140" align="right">
        <template #default="{ row }">{{ formatCurrency(row.credit) }}</template>
      </el-table-column>
      <el-table-column prop="description" :label="t('pages.journalEntries.description')" min-width="160" show-overflow-tooltip />
    </el-table>

    <el-dialog v-model="generateVisible" :title="t('pages.journalEntries.generateFromTransaction')" width="600px" destroy-on-close align-center>
      <el-form :model="generateForm" label-position="top">
        <el-form-item :label="t('pages.journalEntries.transactionType')" required>
          <el-select v-model="generateForm.transaction_type" class="w-full">
            <el-option :label="t('pages.journalEntries.po_created')" value="po_created" />
            <el-option :label="t('pages.journalEntries.invoice')" value="invoice" />
            <el-option :label="t('pages.journalEntries.payment')" value="payment" />
          </el-select>
        </el-form-item>
        <el-form-item :label="t('pages.journalEntries.transactionId')" required>
          <el-input-number v-model="generateForm.transaction_id" :min="1" class="w-full" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button :icon="Close" @click="generateVisible = false">{{ t('common.cancel') }}</el-button>
        <el-button type="primary" :loading="generating" @click="submitGenerate">{{ t('pages.journalEntries.generate') }}</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="showTrialBalance" :title="t('pages.journalEntries.trialBalanceTitle')" width="800px" destroy-on-close align-center>
      <div class="flex flex-wrap gap-2 mb-4 items-center">
        <el-date-picker
          v-model="tbDateRange"
          type="daterange"
          :range-separator="t('common.dashSeparator')"
          :start-placeholder="t('common.startDate')"
          :end-placeholder="t('common.endDate')"
          format="YYYY-MM-DD"
          value-format="YYYY-MM-DD"
          class="w-72"
          :shortcuts="dateShortcuts"
          unlink-panels
        />
        <el-button type="primary" :icon="Search" @click="loadTrialBalance">{{ t('common.search') }}</el-button>
      </div>

      <el-table :data="trialBalance.rows" border stripe size="small" class="admin-table" table-layout="fixed" :empty-text="t('common.tableEmpty')" show-summary>
        <el-table-column prop="coa_code" :label="t('pages.journalEntries.coaCode')" width="120" />
        <el-table-column prop="coa_name" :label="t('pages.journalEntries.coaName')" min-width="200" />
        <el-table-column prop="total_debit" :label="t('pages.journalEntries.debit')" width="160" align="right">
          <template #default="{ row }">{{ formatCurrency(row.total_debit) }}</template>
        </el-table-column>
        <el-table-column prop="total_credit" :label="t('pages.journalEntries.credit')" width="160" align="right">
          <template #default="{ row }">{{ formatCurrency(row.total_credit) }}</template>
        </el-table-column>
      </el-table>

      <div class="mt-4 flex justify-end gap-4">
        <div class="text-right">
          <div class="text-sm text-gray-500">{{ t('pages.journalEntries.totalDebit') }}</div>
          <div class="text-lg font-bold">{{ formatCurrency(trialBalance.total_debit) }}</div>
        </div>
        <div class="text-right">
          <div class="text-sm text-gray-500">{{ t('pages.journalEntries.totalCredit') }}</div>
          <div class="text-lg font-bold">{{ formatCurrency(trialBalance.total_credit) }}</div>
        </div>
        <div class="text-right">
          <div class="text-sm text-gray-500">{{ t('pages.journalEntries.trialBalance') }}</div>
          <el-tag :type="trialBalance.is_balanced ? 'success' : 'danger'">
            {{ trialBalance.is_balanced ? t('pages.journalEntries.balanced') : t('pages.journalEntries.notBalanced') }}
          </el-tag>
        </div>
      </div>
    </el-dialog>
  </AdminSection>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessage } from 'element-plus'
import { Plus, Search, Close, Refresh } from '@element-plus/icons-vue'
import AdminSection from '../../components/AdminSection.vue'
import { generateJournalFromTransaction, getTrialBalance, listJournalEntries } from '../../api/client'

const { t } = useI18n()

const loading = ref(false)
const entries = ref([])
const filterDateRange = ref([])
const filterType = ref('')

const dateShortcuts = computed(() => [
  {
    text: t('pages.marketingFlow.shortcutToday'),
    value: () => {
      const end = new Date()
      const start = new Date()
      return [start, end]
    },
  },
  {
    text: t('pages.marketingFlow.shortcutLast7Days'),
    value: () => {
      const end = new Date()
      const start = new Date()
      start.setTime(start.getTime() - 3600 * 1000 * 24 * 7)
      return [start, end]
    },
  },
  {
    text: t('pages.marketingFlow.shortcutLast30Days'),
    value: () => {
      const end = new Date()
      const start = new Date()
      start.setTime(start.getTime() - 3600 * 1000 * 24 * 30)
      return [start, end]
    },
  },
  {
    text: t('pages.marketingFlow.shortcutThisMonth'),
    value: () => {
      const end = new Date()
      const start = new Date(end.getFullYear(), end.getMonth(), 1)
      return [start, end]
    },
  },
])

const generateVisible = ref(false)
const generating = ref(false)
const generateForm = reactive({
  transaction_type: 'po_created',
  transaction_id: null,
})

const showTrialBalance = ref(false)
const tbDateRange = ref([])
const trialBalance = reactive({
  rows: [],
  total_debit: 0,
  total_credit: 0,
  is_balanced: false,
})

function formatCurrency(val) {
  if (val == null) return '0.00'
  return Number(val).toLocaleString('id-ID', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

async function loadEntries() {
  loading.value = true
  try {
    entries.value = await listJournalEntries({
      date_from: filterDateRange.value?.[0] || undefined,
      date_to: filterDateRange.value?.[1] || undefined,
      transaction_type: filterType.value || undefined,
    })
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  } finally {
    loading.value = false
  }
}

function openGenerate() {
  generateForm.transaction_type = 'po_created'
  generateForm.transaction_id = null
  generateVisible.value = true
}

async function submitGenerate() {
  if (!generateForm.transaction_id) {
    ElMessage.warning(t('pages.journalEntries.transactionId') + ' is required')
    return
  }
  generating.value = true
  try {
    const result = await generateJournalFromTransaction(generateForm.transaction_type, generateForm.transaction_id)
    ElMessage.success(t('common.save'))
    generateVisible.value = false
    await loadEntries()
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  } finally {
    generating.value = false
  }
}

async function loadTrialBalance() {
  try {
    const result = await getTrialBalance({
      date_from: tbDateRange.value?.[0] || undefined,
      date_to: tbDateRange.value?.[1] || undefined,
    })
    trialBalance.rows = result.rows
    trialBalance.total_debit = result.total_debit
    trialBalance.total_credit = result.total_credit
    trialBalance.is_balanced = result.is_balanced
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  }
}

onMounted(() => {
  loadEntries()
})
</script>
