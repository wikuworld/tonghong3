<template>
  <div>
    <el-tabs v-model="activeTab" @tab-change="onTabChange">
      <el-tab-pane :label="t('pages.inventory.tabs.stock')" name="stock">
        <StockTab />
      </el-tab-pane>
      <el-tab-pane :label="t('pages.inventory.tabs.material')" name="material">
        <MaterialTab />
      </el-tab-pane>
      <el-tab-pane :label="t('pages.inventory.tabs.warehouse')" name="warehouse">
        <WarehouseTab />
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import StockTab from './inventory/StockTab.vue'
import MaterialTab from './inventory/MaterialTab.vue'
import WarehouseTab from './inventory/WarehouseTab.vue'

const VALID_TABS = new Set(['stock', 'material', 'warehouse'])

const { t } = useI18n()
const route = useRoute()
const router = useRouter()

function tabFromRoute() {
  const raw = String(route.query.tab || 'stock')
  return VALID_TABS.has(raw) ? raw : 'stock'
}

const activeTab = ref(tabFromRoute())

watch(
  () => route.query.tab,
  () => {
    const next = tabFromRoute()
    activeTab.value = next
    if (route.query.tab && !VALID_TABS.has(String(route.query.tab))) {
      router.replace({ path: '/admin/inventory', query: { tab: 'stock' } })
    }
  },
  { immediate: true }
)

function onTabChange(name) {
  const tab = String(name || 'stock')
  if (String(route.query.tab || 'stock') === tab) return
  router.replace({ path: '/admin/inventory', query: { tab } })
}
</script>
