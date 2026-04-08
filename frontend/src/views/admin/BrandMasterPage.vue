<template>
  <AdminSection :title="t('pages.brandMaster.title')" :subtitle="t('pages.brandMaster.subtitle')">
    <template #actions>
      <el-input v-model="keyword" :placeholder="t('pages.brandMaster.searchPlaceholder')" clearable class="brand-master-toolbar-search" />
      <el-select v-model="filterCustomerId" clearable filterable class="brand-master-filter-customer" :placeholder="t('pages.brandMaster.filterCustomer')">
        <el-option :label="t('pages.brandMaster.allCustomer')" :value="null" />
        <el-option v-for="c in customers" :key="c.id" :label="`${c.code || ''} ${c.name || ''}`.trim()" :value="c.id" />
      </el-select>
      <el-switch v-model="groupByCustomer" />
      <span class="text-sm text-slate-600">{{ t('pages.brandMaster.groupByCustomer') }}</span>
      <el-button :loading="seeding" @click="runSeedFromBuyers">{{ t('pages.brandMaster.seedFromBuyer') }}</el-button>
      <el-button type="primary" :icon="Plus" @click="openCreate">{{ t('common.create') }}</el-button>
    </template>

    <el-table
      :data="filteredRows"
      v-loading="loading"
      border
      stripe
      size="small"
      class="admin-table"
      table-layout="auto"
      row-key="id"
      :tree-props="{ children: 'children' }"
      :empty-text="t('pages.brandMaster.tableEmpty')"
      :default-expand-all="groupByCustomer"
    >
      <el-table-column type="index" :label="t('common.noLabel')" width="56" align="center" />
      <el-table-column prop="code" :label="t('common.code')" min-width="120" />
      <el-table-column prop="name" :label="t('common.name')" min-width="180" />
      <el-table-column prop="customer_name" :label="t('common.customer')" min-width="180" />
      <el-table-column :label="t('pages.brandMaster.buyerMap')" min-width="200">
        <template #default="{ row }">
          <el-tag v-if="row.buyer_codes?.length" size="small" type="info" effect="plain">
            {{ row.buyer_codes.join(', ') }}
          </el-tag>
          <span v-else class="text-slate-500">{{ t('common.emptyValue') }}</span>
        </template>
      </el-table-column>
      <el-table-column :label="t('common.actions')" width="168" align="center" fixed="right">
        <template #default="{ row }">
          <template v-if="!row.actions_disabled">
            <el-button link @click="openBuyerMap(row)">{{ t('pages.brandMaster.manageBuyerMap') }}</el-button>
            <el-button :icon="EditPen" link type="primary" @click="openEdit(row)" />
            <el-button :icon="Delete" link type="danger" @click="removeRow(row)" />
          </template>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="formVisible" :title="isEdit ? t('pages.brandMaster.editTitle') : t('pages.brandMaster.createTitle')" width="520px" destroy-on-close align-center>
      <el-form label-position="top">
        <el-form-item :label="t('common.code')" required>
          <el-input v-model="form.code" maxlength="50" />
        </el-form-item>
        <el-form-item :label="t('common.name')">
          <el-input v-model="form.name" maxlength="255" />
        </el-form-item>
        <el-form-item :label="t('common.customer')">
          <el-select v-model="form.customer_id" clearable filterable class="w-full">
            <el-option v-for="c in customers" :key="c.id" :label="`${c.code || ''} ${c.name || ''}`.trim()" :value="c.id" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="brand-master-dialog-footer">
          <el-button @click="formVisible = false">{{ t('common.cancel') }}</el-button>
          <el-button type="primary" :loading="saving" @click="submit">{{ t('common.save') }}</el-button>
        </div>
      </template>
    </el-dialog>

    <el-dialog
      v-model="buyerMapVisible"
      :title="t('pages.brandMaster.manageBuyerMap')"
      width="560px"
      destroy-on-close
      align-center
    >
      <p class="mb-2 text-sm text-slate-600">
        {{ t('pages.brandMaster.buyerMapHint', { brand: buyerMapBrandLabel }) }}
      </p>
      <el-select
        v-model="buyerMapSelected"
        multiple
        filterable
        clearable
        class="w-full"
        :placeholder="t('pages.brandMaster.buyerMapPlaceholder')"
      >
        <el-option v-for="b in buyerCodes" :key="b" :label="b" :value="b" />
      </el-select>
      <template #footer>
        <div class="brand-master-dialog-footer">
          <el-button @click="buyerMapVisible = false">{{ t('common.cancel') }}</el-button>
          <el-button type="primary" :loading="buyerMapSaving" @click="saveBuyerMap">{{ t('common.save') }}</el-button>
        </div>
      </template>
    </el-dialog>
  </AdminSection>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Delete, EditPen, Plus } from '@element-plus/icons-vue'
import AdminSection from '../../components/AdminSection.vue'
import {
  createBrand,
  deleteBrand,
  listBrandBuyers,
  listBrands,
  listBuyerPriceLists,
  listCustomers,
  replaceBrandBuyers,
  seedBrandsFromBuyers,
  updateBrand,
} from '../../api/client'

const { t } = useI18n()
const loading = ref(false)
const saving = ref(false)
const seeding = ref(false)
const keyword = ref('')
const filterCustomerId = ref(null)
const groupByCustomer = ref(false)
const rows = ref([])
const customers = ref([])
const buyerCodes = ref([])
const buyerMapVisible = ref(false)
const buyerMapSaving = ref(false)
const buyerMapBrandId = ref(null)
const buyerMapBrandLabel = ref('')
const buyerMapSelected = ref([])

const formVisible = ref(false)
const isEdit = ref(false)
const editingId = ref(null)
const form = reactive({
  code: '',
  name: '',
  customer_id: null,
})

async function load() {
  loading.value = true
  try {
    const [brands, cust, bpl] = await Promise.all([listBrands(), listCustomers(), listBuyerPriceLists().catch(() => [])])
    buyerCodes.value = [...new Set((bpl || []).map((x) => x.buyer_code).filter(Boolean))]
    customers.value = cust
    const mapped = await Promise.all(
      brands.map(async (b) => {
        const buyers = await listBrandBuyers(b.id).catch(() => [])
        return {
          ...b,
          buyer_codes: buyers.map((x) => x.buyer_code).filter(Boolean),
        }
      }),
    )
    rows.value = mapped.map((b) => ({
      ...b,
      customer_name: cust.find((c) => c.id === b.customer_id)?.name || t('common.emptyValue'),
    }))
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  } finally {
    loading.value = false
  }
}

function openBuyerMap(row) {
  buyerMapBrandId.value = row.id
  buyerMapBrandLabel.value = row.code || row.name || `#${row.id}`
  buyerMapSelected.value = [...(row.buyer_codes || [])]
  buyerMapVisible.value = true
}

async function saveBuyerMap() {
  if (!buyerMapBrandId.value) return
  buyerMapSaving.value = true
  try {
    await replaceBrandBuyers(buyerMapBrandId.value, buyerMapSelected.value)
    ElMessage.success(t('common.save'))
    buyerMapVisible.value = false
    await load()
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  } finally {
    buyerMapSaving.value = false
  }
}

const filteredRows = computed(() => {
  const q = keyword.value.trim().toLowerCase()
  const base = rows.value.filter((r) => {
    if (filterCustomerId.value && r.customer_id !== filterCustomerId.value) return false
    if (!q) return true
    return JSON.stringify(r).toLowerCase().includes(q)
  })
  if (!groupByCustomer.value) return base
  const groups = new Map()
  for (const row of base) {
    const gid = row.customer_id || 0
    if (!groups.has(gid)) {
      groups.set(gid, {
        id: `g-${gid}`,
        code: '',
        name: row.customer_name || t('common.emptyValue'),
        customer_name: row.customer_name || t('common.emptyValue'),
        buyer_codes: [],
        actions_disabled: true,
        children: [],
      })
    }
    groups.get(gid).children.push(row)
  }
  return Array.from(groups.values())
})

function openCreate() {
  isEdit.value = false
  editingId.value = null
  form.code = ''
  form.name = ''
  form.customer_id = null
  formVisible.value = true
}

function openEdit(row) {
  isEdit.value = true
  editingId.value = row.id
  form.code = row.code || ''
  form.name = row.name || ''
  form.customer_id = row.customer_id ?? null
  formVisible.value = true
}

async function submit() {
  if (!form.code?.trim()) {
    ElMessage.warning(t('pages.brandMaster.codeRequired'))
    return
  }
  saving.value = true
  try {
    const payload = {
      code: form.code.trim(),
      name: form.name?.trim() || undefined,
      customer_id: form.customer_id || undefined,
    }
    if (isEdit.value && editingId.value) {
      await updateBrand(editingId.value, payload)
    } else {
      await createBrand(payload)
    }
    formVisible.value = false
    ElMessage.success(t('common.save'))
    await load()
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  } finally {
    saving.value = false
  }
}

async function removeRow(row) {
  try {
    await ElMessageBox.confirm(
      t('pages.brandMaster.deleteConfirm', { code: row.code || row.id }),
      t('pages.brandMaster.deleteTitle'),
      {
        type: 'warning',
        confirmButtonText: t('common.delete'),
        cancelButtonText: t('common.cancel'),
      },
    )
    await deleteBrand(row.id)
    ElMessage.success(t('common.deleteSuccess'))
    await load()
  } catch (e) {
    if (e !== 'cancel') ElMessage.error(e.message || t('common.errorGeneric'))
  }
}

async function runSeedFromBuyers() {
  seeding.value = true
  try {
    const out = await seedBrandsFromBuyers()
    ElMessage.success(t('pages.brandMaster.seedResult', { n: out.created || 0, m: out.mapped || 0 }))
    await load()
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  } finally {
    seeding.value = false
  }
}

onMounted(load)
</script>

<style scoped>
.brand-master-filter-customer {
  width: 240px;
}

.brand-master-dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}
</style>
