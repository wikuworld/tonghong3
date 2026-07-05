<template>
  <div>
    <el-tabs v-model="activeTab">
      <el-tab-pane :label="t('pages.inventory.tabs.stock')" name="stock">
        <StockTab />
      </el-tab-pane>
      <el-tab-pane :label="t('pages.inventory.tabs.material')" name="material">
        <MaterialTab />
      </el-tab-pane>
      <el-tab-pane :label="t('pages.inventory.tabs.warehouse')" name="warehouse">
        <WarehouseTab />
      </el-tab-pane>
      <el-tab-pane :label="t('pages.inventory.tabs.receipt')" name="receipt">
        <ReceiptTab />
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import StockTab from './inventory/StockTab.vue'
import MaterialTab from './inventory/MaterialTab.vue'
import WarehouseTab from './inventory/WarehouseTab.vue'
import ReceiptTab from './inventory/ReceiptTab.vue'

const { t } = useI18n()
const activeTab = ref('stock')
</script>
