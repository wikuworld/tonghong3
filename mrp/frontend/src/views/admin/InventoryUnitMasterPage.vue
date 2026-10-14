<template>
  <AdminSection :title="t('pages.inventory.unitMasterTitle')" :subtitle="t('pages.inventory.unitMasterSubtitle')">
    <template #actions>
      <el-button :icon="Refresh" :loading="loading" @click="reload">{{ t('common.refresh') }}</el-button>
      <el-button v-if="canCreate" type="primary" :icon="Plus" @click="openCreate">{{ t('common.create') }}</el-button>
    </template>
    <UnitMasterTab ref="tabRef" @loading="onLoading" />
  </AdminSection>
</template>

<script setup>
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { Plus, Refresh } from '@element-plus/icons-vue'
import AdminSection from '../../components/AdminSection.vue'
import UnitMasterTab from './inventory/UnitMasterTab.vue'
import { useModulePermission } from '../../composables/useModulePermission'

const { t } = useI18n()
const { canCreate } = useModulePermission('inventory')

const tabRef = ref(null)
const loading = ref(false)

function onLoading(v) {
  loading.value = !!v
}

function reload() {
  tabRef.value?.reload?.()
}

function openCreate() {
  tabRef.value?.openCreate?.()
}
</script>
