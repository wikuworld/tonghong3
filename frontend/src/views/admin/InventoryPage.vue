<template>
  <div>
    <el-tabs v-model="activeTab">
      <el-tab-pane label="Stok" name="stock">
        <StockTab />
      </el-tab-pane>
      <el-tab-pane label="Material" name="material">
        <MaterialTab />
      </el-tab-pane>
      <el-tab-pane label="Warehouse" name="warehouse">
        <WarehouseTab />
      </el-tab-pane>
      <el-tab-pane label="Penerimaan" name="receipt">
        <ReceiptTab />
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import StockTab from './inventory/StockTab.vue'
import MaterialTab from './inventory/MaterialTab.vue'
import WarehouseTab from './inventory/WarehouseTab.vue'
import ReceiptTab from './inventory/ReceiptTab.vue'

const activeTab = ref('stock')
</script>