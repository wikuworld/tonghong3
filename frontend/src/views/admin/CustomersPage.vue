<template>
  <AdminSection :title="t('pages.customers.title')" :subtitle="t('pages.customers.subtitle')">
    <template #actions>
      <el-input
        v-model="keyword"
        :placeholder="t('pages.customers.searchPlaceholder')"
        clearable
        class="customer-toolbar-search"
      />
      <span v-if="loading" class="text-xs text-slate-500">{{ t('common.loadingData') }}</span>
      <el-button :icon="Refresh" :loading="loading" @click="load">{{ t('common.refresh') }}</el-button>
      <el-button v-if="canCreate" type="primary" :icon="Plus" @click="openCreate">{{ t('common.create') }}</el-button>
    </template>

    <div class="admin-inner-card">
      <div class="admin-inner-card__head customer-inner-head">
        <div>
          <h3 class="admin-inner-card__title">{{ t('pages.customers.listTitle') }}</h3>
          <p class="admin-inner-card__sub">{{ t('pages.customers.listSubtitle') }}</p>
        </div>
        <el-tooltip placement="top-start" :show-after="200">
          <template #content>{{ t('pages.customers.legacyLayoutHint') }}</template>
          <el-icon class="customer-layout-hint" :size="16" tabindex="0" :aria-label="t('pages.customers.legacyLayoutHint')">
            <InfoFilled />
          </el-icon>
        </el-tooltip>
      </div>

      <div class="admin-stats-grid customer-stats-grid">
        <div class="admin-stat-card admin-stat-card--warn">
          <span class="admin-stat-card__value">{{ exportCount }}</span>
          <span class="admin-stat-card__label">{{ t('pages.customers.statExport') }}</span>
        </div>
        <div class="admin-stat-card admin-stat-card--success">
          <span class="admin-stat-card__value">{{ localCount }}</span>
          <span class="admin-stat-card__label">{{ t('pages.customers.statLocal') }}</span>
        </div>
        <div class="admin-stat-card admin-stat-card--info">
          <span class="admin-stat-card__value">{{ totalRows }}</span>
          <span class="admin-stat-card__label">{{ t('pages.customers.statFilteredTotal') }}</span>
        </div>
      </div>

      <div class="filter-panel customer-filter-panel">
        <p class="filter-panel__title">{{ t('common.filter') }}</p>
        <div class="customer-filter-row">
          <span class="customer-filter-label">{{ t('pages.customers.filterMode') }}</span>
          <el-switch
            v-model="showExportCustomers"
            inline-prompt
            :active-text="t('pages.customers.filterExport')"
            :inactive-text="t('pages.customers.filterLocal')"
          />
        </div>
      </div>

      <el-row :gutter="16" class="customer-master-layout" v-loading="loading">
        <el-col :xs="24" :md="7" :lg="6">
          <div class="customer-aside-panel">
            <div class="customer-aside-panel__head">
              <span class="customer-aside-panel__title">{{ t('pages.customers.asideTitle') }}</span>
              <span class="customer-aside-panel__count">
                {{ t('pages.customers.shownOnPage', { count: filteredRows.length }) }}
              </span>
            </div>
            <el-scrollbar max-height="460">
              <div
                v-for="row in filteredRows"
                :key="row.id"
                class="customer-aside-item"
                :class="{ 'customer-aside-item--active': panelRow?.id === row.id }"
                role="button"
                tabindex="0"
                @click="selectCustomer(row.id)"
                @keydown.enter.prevent="selectCustomer(row.id)"
                @dblclick="openEdit(row)"
              >
                <div class="customer-aside-item__head">
                  <div class="text-xs font-mono text-slate-500">{{ row.code || '—' }}</div>
                  <el-tag size="small" :type="row.is_active ? 'success' : 'info'" effect="light">
                    {{ row.is_active ? t('status.active') : t('status.inactive') }}
                  </el-tag>
                </div>
                <div class="text-sm font-medium text-slate-800 line-clamp-2">{{ row.name || t('common.emptyValue') }}</div>
                <div class="customer-aside-item__meta">
                  <span>{{ row.country || t('common.emptyValue') }}</span>
                  <span>{{ contactSummary(row) }}</span>
                </div>
                <div class="customer-aside-item__actions">
                  <el-switch
                    :model-value="Boolean(row.is_active)"
                    size="small"
                    @click.stop
                    @change="toggleCustomerActive(row, $event)"
                  />
                  <el-button
                    v-if="canDelete"
                    :icon="Delete"
                    link
                    type="danger"
                    @click.stop="confirmDelete(row)"
                  />
                </div>
              </div>
              <el-empty v-if="!filteredRows.length" :description="t('pages.customers.tableEmpty')" />
            </el-scrollbar>
            <div class="customer-list-pagination">
              <el-pagination
                size="small"
                background
                layout="prev, pager, next"
                :total="totalRows"
                :current-page="page"
                :page-size="pageSize"
                @current-change="onPageChange"
              />
            </div>
          </div>
        </el-col>

        <el-col :xs="24" :md="17" :lg="18">
          <div v-if="panelRow" class="customer-detail-panel" v-loading="panelLoading">
            <div class="customer-detail-panel__head">
              <div class="customer-detail-panel__title-wrap">
                <span class="customer-detail-panel__code">{{ panelRow.code || '—' }}</span>
                <h4 class="customer-detail-panel__title">{{ panelRow.name || panelRow.code }}</h4>
              </div>
              <div class="customer-detail-panel__actions">
                <el-button v-if="canUpdate" type="primary" size="small" :icon="EditPen" @click="openEdit(panelRow)">
                  {{ t('common.edit') }}
                </el-button>
                <el-button size="small" :icon="View" @click="openDetail(panelRow)">{{ t('common.detail') }}</el-button>
              </div>
            </div>
            <div class="customer-detail-panel__body">
              <el-descriptions :column="2" border size="small">
                <el-descriptions-item :label="t('common.code')">{{ panelRow.code || '—' }}</el-descriptions-item>
                <el-descriptions-item :label="t('pages.customers.fieldReferenceQuotation')">
                  {{ panelRow.reference_quotation || '—' }}
                </el-descriptions-item>
                <el-descriptions-item :label="t('pages.customers.fieldPaymentTerms')">
                  {{ panelRow.payment_terms || '—' }}
                </el-descriptions-item>
                <el-descriptions-item :label="t('pages.customers.fieldDefaultCurrency')">
                  {{ panelRow.default_currency || '—' }}
                </el-descriptions-item>
                <el-descriptions-item :label="t('pages.customers.fieldTaxMode')">
                  {{ taxModeLabel(panelRow.tax_mode) }}
                </el-descriptions-item>
                <el-descriptions-item :label="t('pages.customers.fieldContactSummary')">
                  {{ contactSummary(panelRow) }}
                </el-descriptions-item>
                <el-descriptions-item :label="t('common.address')" :span="2">{{ panelRow.address || '—' }}</el-descriptions-item>
                <el-descriptions-item :label="t('pages.customers.fieldBillingAddress')" :span="2">
                  {{ panelRow.billing_address || '—' }}
                </el-descriptions-item>
                <el-descriptions-item :label="t('pages.customers.fieldRemark')" :span="2">{{ panelRow.remark || '—' }}</el-descriptions-item>
              </el-descriptions>
            </div>
          </div>
          <div v-else class="customer-detail-panel customer-detail-panel--empty">
            <el-empty :description="t('pages.customers.panelEmpty')" />
          </div>
        </el-col>
      </el-row>
    </div>

    <el-dialog
      v-model="detailVisible"
      :title="t('pages.customers.dialogDetail')"
      width="640px"
      destroy-on-close
      class="customer-dialog"
      align-center
      @closed="detailRow = null"
    >
      <template v-if="detailRow">
        <el-descriptions :column="2" border size="small" class="customer-descriptions">
          <el-descriptions-item :label="t('common.code')" :span="1">
            {{ detailRow.code || t('common.emptyValue') }}
          </el-descriptions-item>
          <el-descriptions-item :label="t('common.name')" :span="1">
            {{ detailRow.name || t('common.emptyValue') }}
          </el-descriptions-item>
          <el-descriptions-item :label="t('pages.customers.fieldContactSummary')" :span="2">
            {{ contactSummary(detailRow) }}
          </el-descriptions-item>
          <el-descriptions-item :label="t('pages.customers.fieldTaxId')" :span="1">
            {{ detailRow.tax_id || t('common.emptyValue') }}
          </el-descriptions-item>
          <el-descriptions-item :label="t('pages.customers.fieldSkepKb')" :span="1">
            {{ detailRow.skep_kb_number || t('common.emptyValue') }}
          </el-descriptions-item>
          <el-descriptions-item :label="t('pages.customers.fieldCustomsOfficeCode')" :span="1">
            {{ detailRow.customs_office_code || t('common.emptyValue') }}
          </el-descriptions-item>
          <el-descriptions-item :label="t('pages.customers.fieldCountry')" :span="1">
            {{ detailRow.country || t('common.emptyValue') }}
          </el-descriptions-item>
          <el-descriptions-item :label="t('pages.customers.wilayahDetail')" :span="2">
            {{ wilayahDetailText || t('common.emptyValue') }}
          </el-descriptions-item>
          <el-descriptions-item :label="t('common.address')" :span="2">
            {{ detailRow.address || t('common.emptyValue') }}
          </el-descriptions-item>
          <el-descriptions-item :label="t('pages.customers.fieldBillingAddress')" :span="2">
            {{ detailRow.billing_address || t('common.emptyValue') }}
          </el-descriptions-item>
          <el-descriptions-item :label="t('pages.customers.fieldRemark')" :span="2">
            {{ detailRow.remark || t('common.emptyValue') }}
          </el-descriptions-item>
          <el-descriptions-item :label="t('pages.customers.fieldExportCustomer')" :span="1">
            {{ detailRow.is_export_customer ? t('common.yes') : t('common.no') }}
          </el-descriptions-item>
          <el-descriptions-item :label="t('pages.customers.fieldReferenceQuotation')" :span="1">
            {{ detailRow.reference_quotation || t('common.emptyValue') }}
          </el-descriptions-item>
          <el-descriptions-item :label="t('pages.customers.fieldPaymentTerms')" :span="1">
            {{ detailRow.payment_terms || t('common.emptyValue') }}
          </el-descriptions-item>
          <el-descriptions-item :label="t('pages.customers.fieldDefaultCurrency')" :span="1">
            {{ detailRow.default_currency || t('common.emptyValue') }}
          </el-descriptions-item>
          <el-descriptions-item :label="t('pages.customers.fieldTaxMode')" :span="1">
            {{ taxModeLabel(detailRow.tax_mode) }}
          </el-descriptions-item>
        </el-descriptions>
      </template>
      <template #footer>
        <el-button type="primary" @click="detailVisible = false">{{ t('pages.customers.closeDetail') }}</el-button>
      </template>
    </el-dialog>

    <el-dialog
      v-model="formVisible"
      :title="formIsEdit ? t('pages.customers.dialogEdit') : t('pages.customers.dialogAdd')"
      width="900px"
      destroy-on-close
      class="customer-dialog"
      align-center
      @closed="resetFormModel"
    >
      <div class="customer-dialog-head">
        <el-tooltip placement="top-start" :show-after="200">
          <template #content>{{ t('pages.customers.formHint') }}</template>
          <el-icon class="customer-layout-hint" :size="16" tabindex="0" :aria-label="t('pages.customers.formHint')">
            <InfoFilled />
          </el-icon>
        </el-tooltip>
        <el-button size="small" type="primary" plain @click="applyQuotationDefaults">{{ t('pages.customers.applyDefaultLocal') }}</el-button>
      </div>
      <el-form
        ref="formRef"
        :model="formModel"
        :rules="formRules"
        label-position="top"
        class="customer-form"
        @submit.prevent
      >
        <el-row :gutter="16" class="customer-form-grid">
          <el-col :xs="24" :sm="12">
            <el-form-item :label="t('common.code')" prop="code">
              <el-input
                v-model="formModel.code"
                :placeholder="t('pages.customers.placeholderCode')"
                maxlength="50"
                show-word-limit
                clearable
              />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :sm="12">
            <el-form-item :label="t('common.name')" prop="name">
              <el-input
                v-model="formModel.name"
                :placeholder="t('pages.customers.placeholderNameLegal')"
                maxlength="255"
                show-word-limit
                clearable
              />
            </el-form-item>
          </el-col>
          <el-col :span="24">
            <el-divider content-position="left">{{ t('pages.customers.quotationSection') }}</el-divider>
          </el-col>
          <el-col :xs="24" :sm="12">
            <el-form-item :label="t('pages.customers.fieldReferenceQuotation')" prop="reference_quotation">
              <el-input v-model="formModel.reference_quotation" maxlength="100" clearable />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :sm="12">
            <el-form-item :label="t('pages.customers.fieldPaymentTerms')" prop="payment_terms">
              <el-select
                v-model="formModel.payment_terms"
                filterable
                allow-create
                default-first-option
                clearable
                class="w-full"
              >
                <el-option
                  v-for="term in PAYMENT_TERMS_OPTIONS"
                  :key="term.value"
                  :label="term.label"
                  :value="term.value"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :xs="24" :sm="8">
            <el-form-item :label="t('pages.customers.fieldDefaultCurrency')" prop="default_currency">
              <el-select v-model="formModel.default_currency" filterable allow-create clearable class="w-full" default-first-option>
                <el-option label="USD" value="USD" />
                <el-option label="IDR" value="IDR" />
                <el-option label="EUR" value="EUR" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :xs="24" :sm="8">
            <el-form-item :label="t('pages.customers.fieldTaxMode')" prop="tax_mode">
              <el-select v-model="formModel.tax_mode" clearable class="w-full" :placeholder="t('pages.customers.fieldTaxMode')">
                <el-option :label="t('pages.customers.taxMode_pkp')" value="pkp" />
                <el-option :label="t('pages.customers.taxMode_non_pkp')" value="non_pkp" />
                <el-option :label="t('pages.customers.taxMode_exempt')" value="exempt" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="24">
            <el-divider content-position="left">{{ t('pages.customers.contactsSection') }}</el-divider>
            <div class="mb-2 flex justify-end">
              <el-button type="primary" plain size="small" :icon="Plus" @click="addContactRow">
                {{ t('pages.customers.addContact') }}
              </el-button>
            </div>
            <div v-for="(contact, idx) in formModel.contacts" :key="`contact-${idx}`" class="customer-contact-card">
              <el-row :gutter="12" class="customer-contact-row">
                <el-col :xs="24" :sm="7" :md="7">
                  <el-form-item :label="t('common.name')">
                    <el-input v-model="contact.name" maxlength="255" clearable />
                  </el-form-item>
                </el-col>
                <el-col :xs="24" :sm="7" :md="6">
                  <el-form-item :label="t('pages.customers.fieldPosition')">
                    <el-select
                      v-model="contact.title"
                      filterable
                      allow-create
                      default-first-option
                      clearable
                      class="w-full"
                    >
                      <el-option v-for="role in POSITION_OPTIONS" :key="role" :label="role" :value="role" />
                    </el-select>
                  </el-form-item>
                </el-col>
                <el-col :xs="24" :sm="5" :md="5">
                  <el-form-item :label="t('common.phone')">
                    <el-input v-model="contact.phone" maxlength="50" clearable />
                  </el-form-item>
                </el-col>
                <el-col :xs="24" :sm="5" :md="5">
                  <el-form-item :label="t('pages.customers.fieldEmail')">
                    <el-input v-model="contact.email" type="email" maxlength="255" clearable />
                  </el-form-item>
                </el-col>
                <el-col :xs="24" :sm="24" :md="1" class="customer-contact-remove">
                  <el-button link type="danger" :icon="Delete" @click="removeContactRow(idx)" />
                </el-col>
              </el-row>
            </div>
          </el-col>
          <el-col :xs="24" :sm="12">
            <el-form-item :label="t('pages.customers.fieldTaxId')" prop="tax_id">
              <el-input v-model="formModel.tax_id" maxlength="32" clearable />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :sm="12">
            <el-form-item :label="t('pages.customers.fieldSkepKb')" prop="skep_kb_number">
              <el-input v-model="formModel.skep_kb_number" maxlength="80" clearable />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :sm="12">
            <el-form-item :label="t('pages.customers.fieldCustomsOfficeCode')" prop="customs_office_code">
              <el-input v-model="formModel.customs_office_code" maxlength="32" clearable />
            </el-form-item>
          </el-col>
          <el-col :span="24">
            <div class="customer-section-head">
              <el-divider content-position="left">{{ t('pages.customers.wilayahSection') }}</el-divider>
              <el-tooltip placement="top" :show-after="200">
                <template #content>{{ t('pages.customers.wilayahHint') }}</template>
                <el-icon class="customer-layout-hint" :size="14" tabindex="0" :aria-label="t('pages.customers.wilayahHint')">
                  <InfoFilled />
                </el-icon>
              </el-tooltip>
            </div>
          </el-col>
          <el-col :xs="24" :sm="12">
            <el-form-item :label="t('pages.customers.wilayahProvince')">
              <el-select
                v-model="formModel.wilayah_province_code"
                filterable
                clearable
                class="w-full"
                :loading="wilayahLoading.province"
                :placeholder="t('pages.customers.wilayahPickProvince')"
                @change="onProvincePicked"
              >
                <el-option v-for="p in provinceOptions" :key="p.code" :label="p.name" :value="p.code" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :xs="24" :sm="12">
            <el-form-item :label="t('pages.customers.wilayahRegency')">
              <el-select
                v-model="formModel.wilayah_regency_code"
                filterable
                clearable
                class="w-full"
                :disabled="!formModel.wilayah_province_code"
                :loading="wilayahLoading.regency"
                :placeholder="t('pages.customers.wilayahPickRegency')"
                @change="onRegencyPicked"
              >
                <el-option v-for="p in regencyOptions" :key="p.code" :label="p.name" :value="p.code" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :xs="24" :sm="12">
            <el-form-item :label="t('pages.customers.wilayahDistrict')">
              <el-select
                v-model="formModel.wilayah_district_code"
                filterable
                clearable
                class="w-full"
                :disabled="!formModel.wilayah_regency_code"
                :loading="wilayahLoading.district"
                :placeholder="t('pages.customers.wilayahPickDistrict')"
                @change="onDistrictPicked"
              >
                <el-option v-for="p in districtOptions" :key="p.code" :label="p.name" :value="p.code" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :xs="24" :sm="12">
            <el-form-item :label="t('pages.customers.wilayahVillage')">
              <el-select
                v-model="formModel.wilayah_village_code"
                filterable
                clearable
                class="w-full"
                :disabled="!formModel.wilayah_district_code"
                :loading="wilayahLoading.village"
                :placeholder="t('pages.customers.wilayahPickVillage')"
                @change="onVillagePicked"
              >
                <el-option v-for="p in villageOptions" :key="p.code" :label="p.name" :value="p.code" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :xs="24" :sm="12">
            <el-form-item :label="t('pages.customers.fieldCountry')" prop="country">
              <el-input v-model="formModel.country" maxlength="100" clearable />
            </el-form-item>
          </el-col>
          <el-col :xs="24">
            <el-form-item :label="t('common.address')" prop="address">
              <el-input
                v-model="formModel.address"
                type="textarea"
                :rows="2"
                :placeholder="t('pages.customers.placeholderAddress')"
                maxlength="2000"
                show-word-limit
              />
            </el-form-item>
          </el-col>
          <el-col :xs="24">
            <el-form-item :label="t('pages.customers.fieldBillingAddress')" prop="billing_address">
              <el-input
                v-model="formModel.billing_address"
                type="textarea"
                :rows="2"
                :placeholder="t('pages.customers.placeholderBillingAddress')"
                maxlength="2000"
                show-word-limit
              />
            </el-form-item>
          </el-col>
          <el-col :xs="24">
            <el-form-item :label="t('pages.customers.fieldRemark')" prop="remark">
              <el-input v-model="formModel.remark" type="textarea" :rows="2" maxlength="2000" show-word-limit />
            </el-form-item>
          </el-col>
          <el-col :xs="24">
            <el-form-item :label="t('status.status')">
              <el-switch
                v-model="formModel.is_active"
                :active-text="t('status.active')"
                :inactive-text="t('status.inactive')"
              />
            </el-form-item>
          </el-col>
          <el-col :xs="24">
            <el-form-item :label="t('pages.customers.fieldExportCustomer')">
              <el-switch v-model="formModel.is_export_customer" />
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <template #footer>
        <div class="customer-dialog-footer">
          <el-button @click="formVisible = false">{{ t('common.cancel') }}</el-button>
          <el-button type="primary" :loading="formSubmitting" @click="submitForm">
            {{ t('common.save') }}
          </el-button>
        </div>
      </template>
    </el-dialog>
  </AdminSection>
</template>

<script setup>
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, View, EditPen, Delete, Refresh, InfoFilled } from '@element-plus/icons-vue'
import AdminSection from '../../components/AdminSection.vue'
import { can } from '../../security/permissions'
import {
  createCustomer,
  deleteCustomer,
  getCustomer,
  listCustomersPage,
  updateCustomer,
  wilayahDistricts,
  wilayahProvinces,
  wilayahRegencies,
  wilayahVillages,
} from '../../api/client'

const { t } = useI18n()
const POSITION_OPTIONS = [
  'Director',
  'General Manager',
  'Marketing Director',
  'Purchasing Manager',
  'Procurement Manager',
  'Finance Manager',
  'QC Manager',
  'Production Manager',
  'Sales Manager',
  'PPIC Manager',
  'Warehouse Manager',
  'Admin',
  'Staff',
]
const PAYMENT_TERMS_OPTIONS = [
  { value: 'TT in advance', label: 'TT in advance' },
  { value: 'TT 30 days', label: 'TT 30 days' },
  { value: 'TT 60 days', label: 'TT 60 days' },
  { value: 'TT 90 days', label: 'TT 90 days' },
]

const canCreate = can('customers', 'create')
const canUpdate = can('customers', 'update')
const canDelete = can('customers', 'delete')

const keyword = ref('')
const loading = ref(false)
const rows = ref([])
const totalRows = ref(0)
const exportCount = ref(0)
const localCount = ref(0)
const page = ref(1)
const pageSize = ref(20)
const showExportCustomers = ref(false)
const panelRow = ref(null)
const panelLoading = ref(false)

function taxModeLabel(mode) {
  const v = (mode || '').toLowerCase()
  if (v === 'pkp') return t('pages.customers.taxMode_pkp')
  if (v === 'non_pkp') return t('pages.customers.taxMode_non_pkp')
  if (v === 'exempt') return t('pages.customers.taxMode_exempt')
  return mode || '—'
}

function normalizeContacts(row) {
  const list = Array.isArray(row?.contacts) ? row.contacts : []
  return list
    .map((c) => ({
      name: (c?.name || '').trim(),
      title: (c?.title || '').trim(),
      phone: (c?.phone || '').trim(),
      email: (c?.email || '').trim(),
    }))
    .filter((c) => c.name || c.title || c.phone || c.email)
}

function contactSummary(row) {
  const contacts = normalizeContacts(row)
  if (!contacts.length) return t('common.emptyValue')
  return contacts
    .map((c) => [c.name, c.title].filter(Boolean).join(' - '))
    .filter(Boolean)
    .join(', ')
}

function searchableText(row) {
  return [
    row.code,
    row.name,
    contactSummary(row),
    row.country,
    row.tax_id,
    row.address,
    row.billing_address,
    row.remark,
    row.payment_terms,
    row.default_currency,
    row.reference_quotation,
    row.tax_mode,
    row.wilayah_province_code,
    row.wilayah_regency_code,
    row.wilayah_district_code,
    row.wilayah_village_code,
    row.is_active ? t('status.active') : t('status.inactive'),
  ]
    .filter(Boolean)
    .join(' ')
    .toLowerCase()
}

async function selectCustomer(id) {
  if (id == null) return
  panelLoading.value = true
  try {
    panelRow.value = await getCustomer(id)
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
    panelRow.value = null
  } finally {
    panelLoading.value = false
  }
}

const filteredRows = computed(() => {
  const q = keyword.value.trim().toLowerCase()
  return rows.value.filter((row) => {
    if (!q) return true
    return searchableText(row).includes(q)
  })
})

async function load() {
  loading.value = true
  try {
    const [result, exportAgg, localAgg] = await Promise.all([
      listCustomersPage({
        q: keyword.value.trim() || undefined,
        is_export_customer: showExportCustomers.value,
        limit: pageSize.value,
        offset: (page.value - 1) * pageSize.value,
      }),
      listCustomersPage({ is_export_customer: true, limit: 1, offset: 0 }),
      listCustomersPage({ is_export_customer: false, limit: 1, offset: 0 }),
    ])
    const offset = (page.value - 1) * pageSize.value
    rows.value = result?.items || []
    totalRows.value = Number(result?.total || 0)
    exportCount.value = Number(exportAgg?.total || 0)
    localCount.value = Number(localAgg?.total || 0)
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  load()
})

watch(keyword, () => {
  page.value = 1
  load()
})

watch(showExportCustomers, () => {
  page.value = 1
  load()
})

function onPageChange(nextPage) {
  page.value = nextPage
  load()
}

const detailVisible = ref(false)
const detailRow = ref(null)
const wilayahDetailText = ref('')

async function buildWilayahReadable(row) {
  if (!row?.wilayah_province_code) return ''
  const parts = []
  try {
    const pr = await wilayahProvinces()
    const pn = (pr.data || []).find((x) => x.code === row.wilayah_province_code)?.name
    if (pn) parts.push(pn)
    if (row.wilayah_regency_code) {
      const rr = await wilayahRegencies(row.wilayah_province_code)
      const rn = (rr.data || []).find((x) => x.code === row.wilayah_regency_code)?.name
      if (rn) parts.push(rn)
    }
    if (row.wilayah_district_code) {
      const dr = await wilayahDistricts(row.wilayah_regency_code)
      const dn = (dr.data || []).find((x) => x.code === row.wilayah_district_code)?.name
      if (dn) parts.push(dn)
    }
    if (row.wilayah_village_code) {
      const vr = await wilayahVillages(row.wilayah_district_code)
      const vn = (vr.data || []).find((x) => x.code === row.wilayah_village_code)?.name
      if (vn) parts.push(vn)
    }
  } catch {
    return [row.wilayah_province_code, row.wilayah_regency_code, row.wilayah_district_code, row.wilayah_village_code]
      .filter(Boolean)
      .join(` ${t('common.pathSeparator')} `)
  }
  return parts.join(` ${t('common.pathSeparator')} `)
}

async function openDetail(row) {
  detailRow.value = { ...row }
  wilayahDetailText.value = ''
  detailVisible.value = true
  wilayahDetailText.value = await buildWilayahReadable(row)
}

async function toggleCustomerActive(row, nextValue) {
  const old = Boolean(row.is_active)
  row.is_active = Boolean(nextValue)
  try {
    await updateCustomer(row.id, { is_active: row.is_active })
    if (panelRow.value?.id === row.id) {
      panelRow.value.is_active = row.is_active
    }
    ElMessage.success(t('pages.customers.saved'))
  } catch (e) {
    row.is_active = old
    ElMessage.error(e.message || t('common.errorGeneric'))
  }
}

function applyQuotationDefaults() {
  formModel.default_currency = 'IDR'
  formModel.tax_mode = 'non_pkp'
  if (!(formModel.country || '').trim()) {
    formModel.country = t('common.countryIndonesia')
  }
}

function emptyContact() {
  return { name: '', title: '', phone: '', email: '' }
}

function addContactRow() {
  formModel.contacts.push(emptyContact())
}

function removeContactRow(index) {
  formModel.contacts.splice(index, 1)
  if (!formModel.contacts.length) {
    formModel.contacts.push(emptyContact())
  }
}

const formVisible = ref(false)
const formIsEdit = ref(false)
const formRef = ref(null)
const formSubmitting = ref(false)

const provinceOptions = ref([])
const regencyOptions = ref([])
const districtOptions = ref([])
const villageOptions = ref([])
const wilayahLoading = reactive({
  province: false,
  regency: false,
  district: false,
  village: false,
})

const formModel = reactive({
  id: null,
  code: '',
  name: '',
  contacts: [],
  country: '',
  tax_id: '',
  skep_kb_number: '',
  customs_office_code: '',
  address: '',
  remark: '',
  is_export_customer: false,
  is_active: true,
  wilayah_province_code: '',
  wilayah_regency_code: '',
  wilayah_district_code: '',
  wilayah_village_code: '',
  payment_terms: '',
  default_currency: '',
  tax_mode: '',
  reference_quotation: '',
  billing_address: '',
})

const formRules = computed(() => ({
  code: [{ required: true, message: t('pages.customers.ruleCode'), trigger: 'blur' }],
  name: [{ required: true, message: t('pages.customers.ruleName'), trigger: 'blur' }],
}))

function resetFormModel() {
  formModel.id = null
  formModel.code = ''
  formModel.name = ''
  formModel.contacts = [emptyContact()]
  formModel.country = ''
  formModel.tax_id = ''
  formModel.skep_kb_number = ''
  formModel.customs_office_code = ''
  formModel.address = ''
  formModel.remark = ''
  formModel.is_export_customer = false
  formModel.is_active = true
  formModel.wilayah_province_code = ''
  formModel.wilayah_regency_code = ''
  formModel.wilayah_district_code = ''
  formModel.wilayah_village_code = ''
  formModel.payment_terms = ''
  formModel.default_currency = ''
  formModel.tax_mode = ''
  formModel.reference_quotation = ''
  formModel.billing_address = ''
  regencyOptions.value = []
  districtOptions.value = []
  villageOptions.value = []
  formRef.value?.clearValidate?.()
}

async function ensureProvinceOptions() {
  if (provinceOptions.value.length) return
  wilayahLoading.province = true
  try {
    const r = await wilayahProvinces()
    provinceOptions.value = r.data || []
  } catch (e) {
    ElMessage.error(e.message || t('pages.customers.loadProvinceFailed'))
  } finally {
    wilayahLoading.province = false
  }
}

watch(formVisible, (open) => {
  if (open) ensureProvinceOptions()
})

async function onProvincePicked(code) {
  formModel.wilayah_regency_code = ''
  formModel.wilayah_district_code = ''
  formModel.wilayah_village_code = ''
  regencyOptions.value = []
  districtOptions.value = []
  villageOptions.value = []
  if (!code) return
  wilayahLoading.regency = true
  try {
    const r = await wilayahRegencies(code)
    regencyOptions.value = r.data || []
  } catch (e) {
    ElMessage.error(e.message || t('pages.customers.loadRegencyFailed'))
  } finally {
    wilayahLoading.regency = false
  }
}

async function onRegencyPicked(code) {
  formModel.wilayah_district_code = ''
  formModel.wilayah_village_code = ''
  districtOptions.value = []
  villageOptions.value = []
  const sel = regencyOptions.value.find((x) => x.code === code)
  if (sel) {
    formModel.country = t('common.countryIndonesia')
  }
  if (!code) return
  wilayahLoading.district = true
  try {
    const r = await wilayahDistricts(code)
    districtOptions.value = r.data || []
  } catch (e) {
    ElMessage.error(e.message || t('pages.customers.loadDistrictFailed'))
  } finally {
    wilayahLoading.district = false
  }
}

async function onDistrictPicked(code) {
  formModel.wilayah_village_code = ''
  villageOptions.value = []
  if (!code) return
  wilayahLoading.village = true
  try {
    const r = await wilayahVillages(code)
    villageOptions.value = r.data || []
  } catch (e) {
    ElMessage.error(e.message || t('pages.customers.loadVillageFailed'))
  } finally {
    wilayahLoading.village = false
  }
}

function onVillagePicked() {
  /* kode & nama tersimpan di formModel.wilayah_village_code + opsional user isi alamat jalan */
}

async function hydrateWilayahFromRow(row) {
  regencyOptions.value = []
  districtOptions.value = []
  villageOptions.value = []
  await ensureProvinceOptions()
  if (!row.wilayah_province_code) return
  try {
    wilayahLoading.regency = true
    const r1 = await wilayahRegencies(row.wilayah_province_code)
    regencyOptions.value = r1.data || []
  } finally {
    wilayahLoading.regency = false
  }
  if (!row.wilayah_regency_code) return
  try {
    wilayahLoading.district = true
    const r2 = await wilayahDistricts(row.wilayah_regency_code)
    districtOptions.value = r2.data || []
  } finally {
    wilayahLoading.district = false
  }
  if (!row.wilayah_district_code) return
  try {
    wilayahLoading.village = true
    const r3 = await wilayahVillages(row.wilayah_district_code)
    villageOptions.value = r3.data || []
  } finally {
    wilayahLoading.village = false
  }
}

function openCreate() {
  formIsEdit.value = false
  resetFormModel()
  formVisible.value = true
}

async function openEdit(row) {
  formIsEdit.value = true
  formModel.id = row.id
  formModel.code = row.code || ''
  formModel.name = row.name || ''
  formModel.contacts = normalizeContacts(row)
  if (!formModel.contacts.length) {
    formModel.contacts = [
      {
        name: row.contact_person || '',
        title: row.position || '',
        phone: row.phone || '',
        email: row.email || '',
      },
    ]
  }
  formModel.country = row.country || ''
  formModel.tax_id = row.tax_id || ''
  formModel.skep_kb_number = row.skep_kb_number || ''
  formModel.customs_office_code = row.customs_office_code || ''
  formModel.address = row.address || ''
  formModel.remark = row.remark || ''
  formModel.is_export_customer = Boolean(row.is_export_customer)
  formModel.is_active = row.is_active !== false
  formModel.wilayah_province_code = row.wilayah_province_code || ''
  formModel.wilayah_regency_code = row.wilayah_regency_code || ''
  formModel.wilayah_district_code = row.wilayah_district_code || ''
  formModel.wilayah_village_code = row.wilayah_village_code || ''
  formModel.payment_terms = row.payment_terms || ''
  formModel.default_currency = row.default_currency || ''
  formModel.tax_mode = row.tax_mode || ''
  formModel.reference_quotation = row.reference_quotation || ''
  formModel.billing_address = row.billing_address || ''
  formVisible.value = true
  await hydrateWilayahFromRow(row)
}

async function submitForm() {
  if (!formRef.value) return
  try {
    await formRef.value.validate()
  } catch {
    return
  }
  formSubmitting.value = true
  try {
    const body = {
      code: formModel.code.trim(),
      name: formModel.name.trim(),
      contacts: normalizeContacts(formModel),
      country: formModel.country.trim() || undefined,
      tax_id: formModel.tax_id.trim() || undefined,
      skep_kb_number: formModel.skep_kb_number.trim() || undefined,
      customs_office_code: formModel.customs_office_code.trim() || undefined,
      address: formModel.address.trim() || undefined,
      remark: formModel.remark.trim() || undefined,
      is_export_customer: formModel.is_export_customer,
      is_active: formModel.is_active,
      wilayah_province_code: formModel.wilayah_province_code || undefined,
      wilayah_regency_code: formModel.wilayah_regency_code || undefined,
      wilayah_district_code: formModel.wilayah_district_code || undefined,
      wilayah_village_code: formModel.wilayah_village_code || undefined,
      payment_terms: formModel.payment_terms.trim() || undefined,
      default_currency: (formModel.default_currency || '').trim().toUpperCase() || undefined,
      tax_mode: formModel.tax_mode || undefined,
      reference_quotation: formModel.reference_quotation.trim() || undefined,
      billing_address: formModel.billing_address.trim() || undefined,
    }
    let refreshId = formModel.id
    if (formIsEdit.value && formModel.id != null) {
      await updateCustomer(formModel.id, body)
      refreshId = formModel.id
    } else {
      const created = await createCustomer(body)
      refreshId = created?.id ?? null
    }
    ElMessage.success(t('pages.customers.saved'))
    formVisible.value = false
    await load()
    if (refreshId != null && panelRow.value?.id === refreshId) {
      await selectCustomer(refreshId)
    }
  } catch (e) {
    const msg = e.message || ''
    if (msg.includes('duplicate') || msg.includes('409')) {
      ElMessage.error(t('pages.customers.codeDuplicate'))
    } else {
      ElMessage.error(msg || t('common.errorGeneric'))
    }
  } finally {
    formSubmitting.value = false
  }
}

function confirmDelete(row) {
  ElMessageBox.confirm(t('pages.customers.deleteConfirm', { name: row.name }), t('pages.customers.deleteTitle'), {
    confirmButtonText: t('common.delete'),
    cancelButtonText: t('common.cancel'),
    type: 'warning',
    distinguishCancelAndClose: true,
  })
    .then(async () => {
      try {
        await deleteCustomer(row.id)
        if (panelRow.value?.id === row.id) {
          panelRow.value = null
        }
        ElMessage.success(t('pages.customers.deleted'))
        await load()
      } catch (e) {
        ElMessage.error(e.message || t('common.errorGeneric'))
      }
    })
    .catch(() => {})
}
</script>

<style scoped>
.customer-inner-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
}

.customer-layout-hint {
  color: #94a3b8;
  cursor: help;
  flex-shrink: 0;
  outline: none;
}

.customer-layout-hint:hover,
.customer-layout-hint:focus-visible {
  color: var(--el-color-primary);
}

.customer-stats-grid {
  grid-template-columns: repeat(3, minmax(0, 1fr));
  border-bottom: 1px solid #e2e8f0;
}

.customer-filter-panel {
  margin: 0;
  border-bottom: 1px solid #e2e8f0;
  border-radius: 0;
}

.customer-filter-row {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 12px;
}

.customer-filter-label {
  font-size: 13px;
  font-weight: 500;
  color: #475569;
}

.customer-master-layout {
  padding: 16px;
}

.customer-aside-panel {
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  background: #f8fafc;
  padding: 12px;
  min-height: 320px;
}

.customer-aside-panel__head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  margin-bottom: 10px;
}

.customer-aside-panel__title {
  font-size: 13px;
  font-weight: 600;
  color: #0f172a;
}

.customer-aside-panel__count {
  font-size: 11px;
  color: #64748b;
}

.customer-detail-panel {
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  background: #fff;
  min-height: 320px;
  overflow: hidden;
}

.customer-detail-panel--empty {
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f8fafc;
}

.customer-detail-panel__head {
  display: flex;
  flex-wrap: wrap;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
  padding: 14px 16px;
  border-bottom: 1px solid #e2e8f0;
  background: linear-gradient(180deg, #f8fafc 0%, #fff 100%);
}

.customer-detail-panel__code {
  display: block;
  font-size: 11px;
  font-family: ui-monospace, monospace;
  color: #64748b;
}

.customer-detail-panel__title {
  margin: 2px 0 0;
  font-size: 1rem;
  font-weight: 600;
  color: #0f172a;
  line-height: 1.35;
}

.customer-detail-panel__actions {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.customer-detail-panel__body {
  padding: 16px;
}

.customer-dialog-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 12px;
}

.customer-section-head {
  display: flex;
  align-items: center;
  gap: 8px;
}

.customer-section-head :deep(.el-divider) {
  flex: 1;
  margin: 16px 0;
}

.customer-row-actions {
  display: inline-flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: center;
  gap: 2px 4px;
}

.customer-list-filter {
  margin-bottom: 10px;
}

.customer-list-pagination {
  margin-top: 10px;
  display: flex;
  justify-content: center;
}

.customer-form :deep(.el-form-item) {
  margin-bottom: 14px;
}

.customer-form :deep(.el-form-item:last-child) {
  margin-bottom: 0;
}

.customer-dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}

.customer-dialog :deep(.el-dialog) {
  max-height: 90vh;
  margin: 0;
  display: flex;
  flex-direction: column;
}

.customer-dialog :deep(.el-dialog__header),
.customer-dialog :deep(.el-dialog__footer) {
  padding: 16px 20px;
}

.customer-dialog :deep(.el-dialog__body) {
  padding: 14px 20px 10px;
  overflow-y: auto;
}

.customer-form-grid {
  row-gap: 4px;
}

.customer-aside-item {
  padding: 10px 10px;
  margin-bottom: 8px;
  border-radius: 6px;
  cursor: pointer;
  border: 1px solid var(--el-border-color-lighter);
}

.customer-aside-item:hover {
  background: var(--el-fill-color-light);
}

.customer-aside-item--active {
  border-color: var(--el-color-primary-light-5);
  background: var(--el-color-primary-light-9);
}

.customer-aside-item__head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.customer-aside-item__meta {
  margin-top: 4px;
  display: grid;
  gap: 2px;
  font-size: 12px;
  color: var(--el-text-color-secondary);
}

.customer-aside-item__actions {
  margin-top: 8px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.customer-contact-card {
  margin-bottom: 12px;
  padding: 12px 12px 2px;
  border: 1px solid var(--el-border-color-light);
  border-radius: 6px;
  background: var(--el-fill-color-blank);
}

.customer-contact-remove {
  display: flex;
  align-items: flex-end;
  justify-content: flex-end;
  padding-bottom: 16px;
}

@media (max-width: 639px) {
  .customer-stats-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 767px) {
  .customer-contact-remove {
    justify-content: flex-start;
    padding-bottom: 10px;
  }
}
</style>
