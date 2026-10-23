<template>
  <div class="customer-info">
    <section class="customer-group">
      <h5 class="customer-group__title">{{ t('pages.customers.identitySection') }}</h5>
      <el-descriptions :column="2" border size="small">
        <el-descriptions-item :label="t('common.code')">{{ text(row.code) }}</el-descriptions-item>
        <el-descriptions-item :label="t('common.name')">{{ text(row.name) }}</el-descriptions-item>
      </el-descriptions>
    </section>

    <section class="customer-group">
      <h5 class="customer-group__title">{{ t('pages.customers.quotationSection') }}</h5>
      <el-descriptions :column="2" border size="small">
        <el-descriptions-item :label="t('pages.customers.fieldReferenceQuotation')">
          {{ text(row.reference_quotation) }}
        </el-descriptions-item>
        <el-descriptions-item :label="t('pages.customers.fieldPaymentTerms')">
          {{ text(row.payment_terms) }}
        </el-descriptions-item>
        <el-descriptions-item :label="t('pages.customers.fieldDefaultCurrency')">
          {{ text(row.default_currency) }}
        </el-descriptions-item>
        <el-descriptions-item :label="t('pages.customers.fieldTaxMode')">
          {{ taxModeLabel(row.tax_mode) }}
        </el-descriptions-item>
      </el-descriptions>
    </section>

    <section class="customer-group">
      <h5 class="customer-group__title">{{ t('pages.customers.contactsSection') }}</h5>
      <el-table v-if="contacts.length" :data="contacts" size="small" border class="customer-info-table">
        <el-table-column prop="name" :label="t('common.name')" min-width="140" />
        <el-table-column prop="title" :label="t('pages.customers.fieldPosition')" min-width="120" />
        <el-table-column prop="phone" :label="t('common.phone')" min-width="120" />
        <el-table-column prop="email" :label="t('pages.customers.fieldEmail')" min-width="180" />
      </el-table>
      <p v-else class="customer-info-empty">{{ t('common.emptyValue') }}</p>
    </section>

    <section class="customer-group">
      <h5 class="customer-group__title">{{ t('pages.customers.taxSection') }}</h5>
      <el-descriptions :column="2" border size="small">
        <el-descriptions-item :label="t('pages.customers.fieldTaxId')">{{ text(row.tax_id) }}</el-descriptions-item>
        <el-descriptions-item :label="t('pages.customers.fieldSkepKb')">{{ text(row.skep_kb_number) }}</el-descriptions-item>
        <el-descriptions-item :label="t('pages.customers.fieldCustomsOfficeCode')" :span="2">
          {{ text(row.customs_office_code) }}
        </el-descriptions-item>
      </el-descriptions>
    </section>

    <section class="customer-group">
      <h5 class="customer-group__title">{{ t('pages.customers.addressSection') }}</h5>
      <el-descriptions :column="2" border size="small">
        <el-descriptions-item :label="t('pages.customers.fieldCountry')">{{ text(row.country) }}</el-descriptions-item>
        <el-descriptions-item :label="t('pages.customers.wilayahDetail')">
          {{ text(wilayahText) }}
        </el-descriptions-item>
        <el-descriptions-item :label="t('common.address')" :span="2">{{ text(row.address) }}</el-descriptions-item>
        <el-descriptions-item :label="t('pages.customers.fieldBillingAddress')" :span="2">
          {{ text(row.billing_address) }}
        </el-descriptions-item>
        <el-descriptions-item :label="t('pages.customers.fieldRemark')" :span="2">{{ text(row.remark) }}</el-descriptions-item>
      </el-descriptions>
    </section>

    <section class="customer-group">
      <h5 class="customer-group__title">{{ t('pages.customers.statusSection') }}</h5>
      <el-descriptions :column="3" border size="small">
        <el-descriptions-item :label="t('status.status')">
          {{ row.is_active ? t('status.active') : t('status.inactive') }}
        </el-descriptions-item>
        <el-descriptions-item :label="t('pages.customers.fieldExportCustomer')">
          {{ row.is_export_customer ? t('common.yes') : t('common.no') }}
        </el-descriptions-item>
        <el-descriptions-item :label="t('pages.customers.fieldOutsideBanten')">
          {{ row.outside_banten ? t('common.yes') : t('common.no') }}
        </el-descriptions-item>
      </el-descriptions>
    </section>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

const props = defineProps({
  row: { type: Object, required: true },
  wilayahText: { type: String, default: '' },
})

const { t } = useI18n()

const contacts = computed(() => {
  const list = Array.isArray(props.row?.contacts) ? props.row.contacts : []
  return list
    .map((c) => ({
      name: (c?.name || '').trim(),
      title: (c?.title || '').trim(),
      phone: (c?.phone || '').trim(),
      email: (c?.email || '').trim(),
    }))
    .filter((c) => c.name || c.title || c.phone || c.email)
})

function text(value) {
  const v = value == null ? '' : String(value).trim()
  return v || t('common.emptyValue')
}

function taxModeLabel(mode) {
  const v = (mode || '').toLowerCase()
  if (v === 'pkp') return t('pages.customers.taxMode_pkp')
  if (v === 'non_pkp') return t('pages.customers.taxMode_non_pkp')
  if (v === 'exempt') return t('pages.customers.taxMode_exempt')
  return text(mode)
}
</script>

<style scoped>
.customer-info {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.customer-group__title {
  margin: 0 0 8px;
  font-size: 13px;
  font-weight: 600;
  color: #0f172a;
}

.customer-info-empty {
  margin: 0;
  font-size: 13px;
  color: #64748b;
}

.customer-info-table {
  width: 100%;
}
</style>
