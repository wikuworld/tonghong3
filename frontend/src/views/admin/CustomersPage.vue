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
      <el-button v-if="canCreate" type="primary" :icon="Plus" @click="openCreate">
        {{ t('common.create') }}
      </el-button>
    </template>

    <el-table
      :data="filteredRows"
      v-loading="loading"
      border
      stripe
      size="small"
      class="admin-table"
      table-layout="auto"
      :empty-text="t('pages.customers.tableEmpty')"
    >
      <el-table-column type="index" :label="t('common.noLabel')" width="56" align="center" />
      <el-table-column prop="code" :label="t('common.code')" min-width="120" show-overflow-tooltip />
      <el-table-column prop="name" :label="t('common.name')" min-width="180" show-overflow-tooltip />
      <el-table-column
        prop="contact_person"
        :label="t('pages.customers.fieldContactPerson')"
        min-width="130"
        show-overflow-tooltip
      />
      <el-table-column prop="email" :label="t('pages.customers.fieldEmail')" min-width="160" show-overflow-tooltip />
      <el-table-column prop="phone" :label="t('common.phone')" min-width="130" show-overflow-tooltip />
      <el-table-column :label="t('pages.customers.fieldCityCountry')" min-width="140" show-overflow-tooltip>
        <template #default="{ row }">{{ cityCountry(row) }}</template>
      </el-table-column>
      <el-table-column prop="tax_id" :label="t('pages.customers.fieldTaxId')" min-width="120" show-overflow-tooltip />
      <el-table-column prop="skep_kb_number" :label="t('pages.customers.fieldSkepKb')" min-width="140" show-overflow-tooltip />
      <el-table-column
        prop="customs_office_code"
        :label="t('pages.customers.fieldCustomsOfficeCode')"
        min-width="140"
        show-overflow-tooltip
      />
      <el-table-column :label="t('common.actions')" width="132" align="center" fixed="right">
        <template #default="{ row }">
          <div class="customer-row-actions">
            <el-tooltip :content="t('common.detail')" placement="top">
              <el-button :icon="View" link type="primary" :aria-label="t('common.detail')" @click="openDetail(row)" />
            </el-tooltip>
            <el-tooltip v-if="canUpdate" :content="t('common.edit')" placement="top">
              <el-button :icon="EditPen" link type="warning" :aria-label="t('common.edit')" @click="openEdit(row)" />
            </el-tooltip>
            <el-tooltip v-if="canDelete" :content="t('common.delete')" placement="top">
              <el-button :icon="Delete" link type="danger" :aria-label="t('common.delete')" @click="confirmDelete(row)" />
            </el-tooltip>
          </div>
        </template>
      </el-table-column>
    </el-table>

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
          <el-descriptions-item :label="t('pages.customers.fieldContactPerson')" :span="1">
            {{ detailRow.contact_person || t('common.emptyValue') }}
          </el-descriptions-item>
          <el-descriptions-item :label="t('pages.customers.fieldEmail')" :span="1">
            {{ detailRow.email || t('common.emptyValue') }}
          </el-descriptions-item>
          <el-descriptions-item :label="t('common.phone')" :span="1">
            {{ detailRow.phone || t('common.emptyValue') }}
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
          <el-descriptions-item :label="t('pages.customers.fieldCity')" :span="1">
            {{ detailRow.city || t('common.emptyValue') }}
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
          <el-descriptions-item :label="t('pages.customers.fieldRemark')" :span="2">
            {{ detailRow.remark || t('common.emptyValue') }}
          </el-descriptions-item>
          <el-descriptions-item :label="t('pages.customers.fieldExportCustomer')" :span="1">
            {{ detailRow.is_export_customer ? t('common.yes') : t('common.no') }}
          </el-descriptions-item>
          <el-descriptions-item :label="t('pages.customers.fieldBillTo')" :span="2">
            {{ detailRow.bill_to || t('common.emptyValue') }}
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
      width="820px"
      destroy-on-close
      class="customer-dialog"
      align-center
      @closed="resetFormModel"
    >
      <p class="mb-3 text-sm text-slate-600">{{ t('pages.customers.formHint') }}</p>
      <el-form
        ref="formRef"
        :model="formModel"
        :rules="formRules"
        label-position="top"
        class="customer-form"
        @submit.prevent
      >
        <el-row :gutter="16">
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
          <el-col :xs="24" :sm="12">
            <el-form-item :label="t('pages.customers.fieldContactPerson')" prop="contact_person">
              <el-input v-model="formModel.contact_person" maxlength="255" clearable />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :sm="12">
            <el-form-item :label="t('pages.customers.fieldEmail')" prop="email">
              <el-input v-model="formModel.email" type="email" maxlength="255" clearable />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :sm="12">
            <el-form-item :label="t('common.phone')" prop="phone">
              <el-input v-model="formModel.phone" :placeholder="t('pages.customers.placeholderPhone')" maxlength="50" clearable />
            </el-form-item>
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
            <el-divider content-position="left">{{ t('pages.customers.wilayahSection') }}</el-divider>
            <p class="mb-3 text-xs text-slate-500">{{ t('pages.customers.wilayahHint') }}</p>
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
            <el-form-item :label="t('pages.customers.fieldCity')" prop="city">
              <el-input v-model="formModel.city" maxlength="120" clearable :placeholder="t('pages.customers.cityFromWilayah')" />
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
            <el-form-item :label="t('pages.customers.fieldRemark')" prop="remark">
              <el-input v-model="formModel.remark" type="textarea" :rows="2" maxlength="2000" show-word-limit />
            </el-form-item>
          </el-col>
          <el-col :xs="24">
            <el-form-item :label="t('pages.customers.fieldExportCustomer')">
              <el-switch v-model="formModel.is_export_customer" />
            </el-form-item>
          </el-col>
          <el-col :xs="24">
            <el-form-item :label="t('pages.customers.fieldBillTo')">
              <el-input
                v-model="formModel.bill_to"
                type="textarea"
                :rows="3"
                maxlength="2000"
                show-word-limit
                :placeholder="t('pages.customers.billToPlaceholder')"
              />
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
import { Plus, View, EditPen, Delete } from '@element-plus/icons-vue'
import AdminSection from '../../components/AdminSection.vue'
import { can } from '../../security/permissions'
import {
  createCustomer,
  deleteCustomer,
  listCustomers,
  updateCustomer,
  wilayahDistricts,
  wilayahProvinces,
  wilayahRegencies,
  wilayahVillages,
} from '../../api/client'

const { t } = useI18n()
const canCreate = can('customers', 'create')
const canUpdate = can('customers', 'update')
const canDelete = can('customers', 'delete')

const keyword = ref('')
const loading = ref(false)
const rows = ref([])

const filteredRows = computed(() => {
  if (!keyword.value.trim()) return rows.value
  const q = keyword.value.toLowerCase()
  return rows.value.filter((row) =>
    [
      row.code,
      row.name,
      row.contact_person,
      row.email,
      row.phone,
      row.city,
      row.country,
      row.tax_id,
      row.address,
      row.remark,
      row.wilayah_province_code,
      row.wilayah_regency_code,
      row.wilayah_district_code,
      row.wilayah_village_code,
    ]
      .filter(Boolean)
      .join(' ')
      .toLowerCase()
      .includes(q),
  )
})

async function load() {
  loading.value = true
  try {
    rows.value = await listCustomers()
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  } finally {
    loading.value = false
  }
}

onMounted(load)

function cityCountry(row) {
  const p = [row.city, row.country].filter(Boolean)
  return p.length ? p.join(', ') : t('common.emptyValue')
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
  contact_person: '',
  email: '',
  phone: '',
  city: '',
  country: '',
  tax_id: '',
  skep_kb_number: '',
  customs_office_code: '',
  address: '',
  remark: '',
  is_export_customer: false,
  bill_to: '',
  wilayah_province_code: '',
  wilayah_regency_code: '',
  wilayah_district_code: '',
  wilayah_village_code: '',
})

const formRules = computed(() => ({
  code: [{ required: true, message: t('pages.customers.ruleCode'), trigger: 'blur' }],
  name: [{ required: true, message: t('pages.customers.ruleName'), trigger: 'blur' }],
}))

function resetFormModel() {
  formModel.id = null
  formModel.code = ''
  formModel.name = ''
  formModel.contact_person = ''
  formModel.email = ''
  formModel.phone = ''
  formModel.city = ''
  formModel.country = ''
  formModel.tax_id = ''
  formModel.skep_kb_number = ''
  formModel.customs_office_code = ''
  formModel.address = ''
  formModel.remark = ''
  formModel.is_export_customer = false
  formModel.bill_to = ''
  formModel.wilayah_province_code = ''
  formModel.wilayah_regency_code = ''
  formModel.wilayah_district_code = ''
  formModel.wilayah_village_code = ''
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
    formModel.city = sel.name
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
  formModel.contact_person = row.contact_person || ''
  formModel.email = row.email || ''
  formModel.phone = row.phone || ''
  formModel.city = row.city || ''
  formModel.country = row.country || ''
  formModel.tax_id = row.tax_id || ''
  formModel.skep_kb_number = row.skep_kb_number || ''
  formModel.customs_office_code = row.customs_office_code || ''
  formModel.address = row.address || ''
  formModel.remark = row.remark || ''
  formModel.is_export_customer = Boolean(row.is_export_customer)
  formModel.bill_to = row.bill_to || ''
  formModel.wilayah_province_code = row.wilayah_province_code || ''
  formModel.wilayah_regency_code = row.wilayah_regency_code || ''
  formModel.wilayah_district_code = row.wilayah_district_code || ''
  formModel.wilayah_village_code = row.wilayah_village_code || ''
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
      contact_person: formModel.contact_person.trim() || undefined,
      email: formModel.email.trim() || undefined,
      phone: formModel.phone.trim() || undefined,
      city: formModel.city.trim() || undefined,
      country: formModel.country.trim() || undefined,
      tax_id: formModel.tax_id.trim() || undefined,
      skep_kb_number: formModel.skep_kb_number.trim() || undefined,
      customs_office_code: formModel.customs_office_code.trim() || undefined,
      address: formModel.address.trim() || undefined,
      remark: formModel.remark.trim() || undefined,
      is_export_customer: formModel.is_export_customer,
      bill_to: formModel.bill_to.trim() || undefined,
      wilayah_province_code: formModel.wilayah_province_code || undefined,
      wilayah_regency_code: formModel.wilayah_regency_code || undefined,
      wilayah_district_code: formModel.wilayah_district_code || undefined,
      wilayah_village_code: formModel.wilayah_village_code || undefined,
    }
    if (formIsEdit.value && formModel.id != null) {
      await updateCustomer(formModel.id, body)
    } else {
      await createCustomer(body)
    }
    ElMessage.success(t('pages.customers.saved'))
    formVisible.value = false
    await load()
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
.admin-table {
  width: 100%;
}

.customer-row-actions {
  display: inline-flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: center;
  gap: 2px 4px;
}

.customer-form :deep(.el-form-item) {
  margin-bottom: 16px;
}

.customer-form :deep(.el-form-item:last-child) {
  margin-bottom: 0;
}

.customer-dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}
</style>
