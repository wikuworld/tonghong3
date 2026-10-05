<template>
  <AdminSection :title="pageTitle" :subtitle="pageSubtitle">
    <template #actions>
      <el-button :icon="Refresh" :loading="loading" @click="reloadActive">{{ t('common.refresh') }}</el-button>
      <el-button
        v-if="showCreate"
        type="primary"
        :icon="Plus"
        @click="triggerCreate"
      >
        {{ t('common.create') }}
      </el-button>
    </template>

    <el-tabs v-model="activeTab" class="admin-tabs" @tab-change="onTabChange">
      <el-tab-pane :label="t('pages.inventory.tabs.material')" name="material" lazy>
        <MaterialTab ref="materialRef" @loading="onChildLoading" />
      </el-tab-pane>
      <el-tab-pane :label="t('pages.inventory.tabs.stock')" name="stock" lazy>
        <StockTab ref="stockRef" @loading="onChildLoading" />
      </el-tab-pane>
      <el-tab-pane :label="t('pages.inventory.tabs.warehouse')" name="warehouse" lazy>
        <WarehouseTab ref="warehouseRef" @loading="onChildLoading" />
      </el-tab-pane>
    </el-tabs>
  </AdminSection>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { Plus, Refresh } from '@element-plus/icons-vue'
import AdminSection from '../../components/AdminSection.vue'
import { useModulePermission } from '../../composables/useModulePermission'
import MaterialTab from './inventory/MaterialTab.vue'
import StockTab from './inventory/StockTab.vue'
import WarehouseTab from './inventory/WarehouseTab.vue'

const VALID_TABS = new Set(['material', 'stock', 'warehouse'])

const { t } = useI18n()
const route = useRoute()
const router = useRouter()
const { canCreate } = useModulePermission('inventory')

const materialRef = ref(null)
const stockRef = ref(null)
const warehouseRef = ref(null)
const loading = ref(false)

function tabFromRoute() {
  const raw = String(route.query.tab || 'material')
  return VALID_TABS.has(raw) ? raw : 'material'
}

const activeTab = ref(tabFromRoute())

const pageTitle = computed(() => {
  if (activeTab.value === 'stock') return t('pages.inventory.stockTitle')
  if (activeTab.value === 'warehouse') return t('pages.inventory.warehouseTitle')
  return t('pages.inventory.materialTitle')
})

const pageSubtitle = computed(() => {
  if (activeTab.value === 'stock') return t('pages.inventory.stockSubtitle')
  if (activeTab.value === 'warehouse') return t('pages.inventory.warehouseSubtitle')
  return t('pages.inventory.materialSubtitle')
})

const showCreate = computed(
  () => canCreate.value && (activeTab.value === 'material' || activeTab.value === 'warehouse')
)

watch(
  () => route.query.tab,
  () => {
    const next = tabFromRoute()
    activeTab.value = next
    if (route.query.tab && !VALID_TABS.has(String(route.query.tab))) {
      router.replace({ path: '/admin/inventory', query: { tab: 'material' } })
    }
  },
  { immediate: true }
)

function onTabChange(name) {
  const tab = String(name || 'material')
  if (String(route.query.tab || 'material') === tab) return
  router.replace({ path: '/admin/inventory', query: { tab } })
}

function onChildLoading(v) {
  loading.value = !!v
}

function activeChild() {
  if (activeTab.value === 'stock') return stockRef.value
  if (activeTab.value === 'warehouse') return warehouseRef.value
  return materialRef.value
}

function reloadActive() {
  activeChild()?.reload?.()
}

function triggerCreate() {
  activeChild()?.openCreate?.()
}
</script>
