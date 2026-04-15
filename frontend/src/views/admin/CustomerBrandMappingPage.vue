<template>
  <AdminSection :title="t('pages.customerBrandMapping.title')" :subtitle="t('pages.customerBrandMapping.subtitle')">
    <template #actions>
      <el-input v-model="keyword" :placeholder="t('pages.customerBrandMapping.searchPlaceholder')" clearable class="customer-brand-toolbar-search" />
    </template>

    <el-row :gutter="16">
      <el-col :xs="24" :sm="12" :md="8">
        <el-card shadow="never" class="customer-brand-card">
          <template #header>
            <div class="flex items-center justify-between">
              <span class="font-semibold">{{ t('pages.customerBrandMapping.selectCustomer') }}</span>
            </div>
          </template>
          <el-select
            v-model="selectedCustomerId"
            clearable
            filterable
            class="w-full"
            :placeholder="t('pages.customerBrandMapping.selectCustomer')"
            @change="onCustomerChange"
          >
            <el-option
              v-for="c in customers"
              :key="c.id"
              :label="customerOptionLabel(c)"
              :value="c.id"
            />
          </el-select>
        </el-card>

        <el-card v-if="selectedCustomerId" shadow="never" class="customer-brand-card mt-4" :header="t('pages.customerBrandMapping.constraintTitle')">
          <p class="text-xs text-slate-500 mb-3">{{ t('pages.customerBrandMapping.constraintSubtitle') }}</p>
          <el-select
            v-model="constraintBrandIds"
            multiple
            clearable
            filterable
            class="w-full"
            :placeholder="t('pages.customerBrandMapping.allowedBrands')"
          >
            <el-option
              v-for="b in allBrands"
              :key="b.id"
              :label="brandOptionLabel(b)"
              :value="b.id"
            />
          </el-select>
          <el-button type="primary" class="mt-3 w-full" :loading="savingConstraint" @click="saveConstraint">
            {{ t('pages.customerBrandMapping.saveConstraint') }}
          </el-button>
        </el-card>
      </el-col>

      <el-col :xs="24" :sm="12" :md="16">
        <el-card v-if="selectedCustomerId" shadow="never" class="customer-brand-card">
          <template #header>
            <div class="flex items-center justify-between">
              <span class="font-semibold">{{ t('pages.customerBrandMapping.title') }}</span>
              <el-button type="primary" size="small" @click="openAddMappingDialog">
                {{ t('pages.customerBrandMapping.addMapping') }}
              </el-button>
            </div>
          </template>

          <el-table :data="filteredMappings" v-loading="loading" border stripe size="small" class="admin-table" :empty-text="t('pages.customerBrandMapping.tableEmpty')">
            <el-table-column :label="t('common.noLabel')" width="60" align="center">
              <template #default="{ $index }">{{ $index + 1 }}</template>
            </el-table-column>
            <el-table-column prop="brand.code" :label="t('common.code')" min-width="120">
              <template #default="{ row }">{{ row.brand?.code || '-' }}</template>
            </el-table-column>
            <el-table-column prop="brand.name" :label="t('common.name')" min-width="180">
              <template #default="{ row }">{{ row.brand?.name || '-' }}</template>
            </el-table-column>
            <el-table-column :label="t('pages.customerBrandMapping.isDefault')" width="100" align="center">
              <template #default="{ row }">
                <el-tag v-if="row.is_default" size="small" type="success">{{ t('pages.customerBrandMapping.isDefault') }}</el-tag>
                <el-tag v-else size="small" type="info" effect="plain">-</el-tag>
              </template>
            </el-table-column>
            <el-table-column :label="t('common.actions')" width="150" align="center">
              <template #default="{ row }">
                <div class="flex items-center justify-center gap-1">
                  <el-tooltip :content="t('pages.customerBrandMapping.setAsDefault')" placement="top">
                    <el-button
                      link
                      type="primary"
                      :icon="Star"
                      :disabled="row.is_default"
                      @click="setAsDefault(row)"
                    />
                  </el-tooltip>
                  <el-tooltip :content="t('pages.customerBrandMapping.removeMapping')" placement="top">
                    <el-button
                      link
                      type="danger"
                      :icon="Delete"
                      @click="removeMapping(row)"
                    />
                  </el-tooltip>
                </div>
              </template>
            </el-table-column>
          </el-table>
        </el-card>

        <el-empty v-else :description="t('pages.customerBrandMapping.selectCustomer')" />
      </el-col>
    </el-row>

    <el-dialog v-model="addMappingVisible" :title="t('pages.customerBrandMapping.addMapping')" width="480px" destroy-on-close align-center>
      <el-form label-position="top">
        <el-form-item :label="t('pages.customerBrandMapping.selectBrands')" required>
          <el-select
            v-model="addMappingBrandIds"
            multiple
            clearable
            filterable
            class="w-full"
            :placeholder="t('pages.customerBrandMapping.selectBrands')"
          >
            <el-option
              v-for="b in availableBrandsForAdd"
              :key="b.id"
              :label="brandOptionLabel(b)"
              :value="b.id"
            />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="flex justify-end gap-2">
          <el-button @click="addMappingVisible = false">{{ t('common.cancel') }}</el-button>
          <el-button type="primary" :loading="savingMapping" @click="addMapping">
            {{ t('common.save') }}
          </el-button>
        </div>
      </template>
    </el-dialog>
  </AdminSection>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Delete, Star } from '@element-plus/icons-vue'
import AdminSection from '../../components/AdminSection.vue'
import {
  createCustomerBrandMapping,
  deleteCustomerBrandMapping,
  getAllowedBrands,
  getBrandConstraint,
  listBrands,
  listCustomerBrandMappings,
  listCustomers,
  updateCustomerBrandMapping,
  upsertBrandConstraint,
} from '../../api/client'

const { t } = useI18n()

const loading = ref(false)
const savingConstraint = ref(false)
const savingMapping = ref(false)
const customers = ref([])
const allBrands = ref([])
const mappings = ref([])
const keyword = ref('')
const selectedCustomerId = ref(null)
const constraintBrandIds = ref([])
const addMappingVisible = ref(false)
const addMappingBrandIds = ref([])

function customerOptionLabel(c) {
  const base = [c.code, c.name].filter(Boolean).join(' — ')
  if (!base) return String(c.id)
  return c.city ? `${base} ${t('common.dotSeparator')} ${c.city}` : base
}

function brandOptionLabel(b) {
  const parts = [b.code, b.name].filter(Boolean)
  return parts.length ? parts.join(' — ') : `#${b.id}`
}

async function load() {
  loading.value = true
  try {
    const [cust, br] = await Promise.all([
      listCustomers(),
      listBrands(),
    ])
    customers.value = cust
    allBrands.value = br
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  } finally {
    loading.value = false
  }
}

async function onCustomerChange(customerId) {
  if (!customerId) {
    mappings.value = []
    constraintBrandIds.value = []
    return
  }
  loading.value = true
  try {
    const [maps, constraint, brands] = await Promise.all([
      loadMappings(customerId),
      getBrandConstraint(customerId).catch(() => null),
      getAllowedBrands(customerId).catch(() => []),
    ])
    mappings.value = maps
    constraintBrandIds.value = constraint?.allowed_brand_ids || []
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  } finally {
    loading.value = false
  }
}

async function loadMappings(customerId) {
  return listCustomerBrandMappings(customerId).catch(() => [])
}

async function saveConstraint() {
  if (!selectedCustomerId.value) return
  savingConstraint.value = true
  try {
    await upsertBrandConstraint(selectedCustomerId.value, {
      allowed_brand_ids: constraintBrandIds.value,
    })
    ElMessage.success(t('pages.customerBrandMapping.constraintSaved'))
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  } finally {
    savingConstraint.value = false
  }
}

function openAddMappingDialog() {
  addMappingBrandIds.value = []
  addMappingVisible.value = true
}

const availableBrandsForAdd = computed(() => {
  const mappedIds = new Set(mappings.value.map(m => m.brand_id))
  return allBrands.value.filter(b => !mappedIds.has(b.id))
})

async function addMapping() {
  if (!selectedCustomerId.value || !addMappingBrandIds.value.length) return
  savingMapping.value = true
  try {
    for (const brandId of addMappingBrandIds.value) {
      await createCustomerBrandMapping(selectedCustomerId.value, { brand_id: brandId })
    }
    ElMessage.success(t('pages.customerBrandMapping.mappingCreated'))
    addMappingVisible.value = false
    mappings.value = await loadMappings(selectedCustomerId.value)
  } catch (e) {
    if (e.message?.includes('409')) {
      ElMessage.warning('Mapping sudah ada')
    } else {
      ElMessage.error(e.message || t('common.errorGeneric'))
    }
  } finally {
    savingMapping.value = false
  }
}

async function setAsDefault(row) {
  try {
    await updateCustomerBrandMapping(selectedCustomerId.value, row.id, { is_default: true })
    ElMessage.success(t('pages.customerBrandMapping.defaultSet'))
    mappings.value = await loadMappings(selectedCustomerId.value)
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  }
}

async function removeMapping(row) {
  try {
    await ElMessageBox.confirm(
      t('pages.customerBrandMapping.removeMapping') + '?',
      t('common.confirm'),
      { type: 'warning' }
    )
    await deleteCustomerBrandMapping(selectedCustomerId.value, row.id)
    ElMessage.success(t('pages.customerBrandMapping.mappingDeleted'))
    mappings.value = await loadMappings(selectedCustomerId.value)
  } catch (e) {
    if (e !== 'cancel') {
      ElMessage.error(e.message || t('common.errorGeneric'))
    }
  }
}

const filteredMappings = computed(() => {
  const q = keyword.value.trim().toLowerCase()
  if (!q) return mappings.value
  return mappings.value.filter(m => {
    const b = m.brand || {}
    return (b.code || '').toLowerCase().includes(q) || (b.name || '').toLowerCase().includes(q)
  })
})

onMounted(load)
</script>

<style scoped>
.customer-brand-card {
  height: 100%;
}

.customer-brand-toolbar-search {
  width: 280px;
}
</style>
