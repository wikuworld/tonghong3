<template>
  <AdminSection :title="t('pages.mrpMasterErp.title')" :subtitle="t('pages.mrpMasterErp.subtitle')">
    <template #actions>
      <el-input v-model="keyword" clearable :placeholder="t('common.search')" class="w-56" @keyup.enter="onSearch" />
      <el-select v-model="filterCategory" clearable :placeholder="t('pages.mrpMasterErp.filterCategory')" class="w-36" @change="onSearch">
        <el-option :label="t('pages.mrpMasterErp.allCategory')" value="" />
        <el-option label="PU" value="PU" />
        <el-option label="Suede" value="Suede" />
        <el-option label="SubKon" value="SubKon" />
      </el-select>
      <el-button :icon="Refresh" :loading="loading" @click="reload">{{ t('common.refresh') }}</el-button>
      <el-button type="primary" @click="goManage">{{ t('pages.mrpMasterErp.manageItems') }}</el-button>
    </template>

    <p v-if="stats.total" class="text-sm text-gray-500 mb-2">
      <el-tag size="small" type="info" effect="plain" class="mr-1 align-middle">{{ t('common.nav.viewOnly') }}</el-tag>
      {{ t('pages.mrpMasterErp.statsHint', { shown: rows.length, total }) }}
      · {{ t('pages.mrpMasterErp.sourceHint') }}
    </p>
    <p v-else class="text-sm text-gray-500 mb-2">
      <el-tag size="small" type="info" effect="plain" class="mr-1 align-middle">{{ t('common.nav.viewOnly') }}</el-tag>
      {{ t('pages.mrpMasterErp.sourceHint') }}
    </p>

    <div class="admin-inner-card">
      <el-table
        :data="rows"
        v-loading="loading"
        border
        stripe
        size="small"
        class="admin-table"
        max-height="60vh"
        :empty-text="t('common.tableEmpty')"
        @sort-change="onSortChange"
      >
        <el-table-column type="index" width="56" :label="t('common.noLabel')" align="center">
          <template #default="{ $index }">{{ (page - 1) * pageSize + $index + 1 }}</template>
        </el-table-column>
        <el-table-column prop="category" :label="t('common.category')" width="90" align="center" sortable="custom" />
        <el-table-column prop="item_code" :label="t('common.code')" min-width="100" show-overflow-tooltip sortable="custom" />
        <el-table-column prop="material_name" :label="t('common.material')" min-width="160" show-overflow-tooltip sortable="custom" />
        <el-table-column prop="thickness" :label="t('common.thickness')" width="100" align="center" sortable="custom" />
        <el-table-column prop="color" :label="t('common.color')" min-width="120" show-overflow-tooltip sortable="custom" />
        <el-table-column prop="emboss" :label="t('common.emboss')" min-width="120" show-overflow-tooltip sortable="custom" />
        <el-table-column prop="color_swatch" :label="t('common.colorReference')" min-width="120" show-overflow-tooltip />
        <el-table-column prop="backer" :label="t('pages.mrpMasterErp.backer')" width="120" show-overflow-tooltip />
      </el-table>
    </div>

    <div class="mt-3 flex justify-end">
      <el-pagination
        v-model:current-page="page"
        v-model:page-size="pageSize"
        :total="total"
        :page-sizes="[50, 100, 200]"
        layout="total, sizes, prev, pager, next"
        background
        small
        @current-change="reload"
        @size-change="onSizeChange"
      />
    </div>
  </AdminSection>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessage } from 'element-plus'
import { Refresh } from '@element-plus/icons-vue'
import AdminSection from '../../../components/AdminSection.vue'
import { mrpListMasterErpPage } from '../../../api/client'
import { buildPageParams, fromElSortChange, normalizePageResult } from '../../../utils/tableQuery'

const { t } = useI18n()
const loading = ref(false)
const rows = ref([])
const keyword = ref('')
const filterCategory = ref('')
const page = ref(1)
const pageSize = ref(50)
const total = ref(0)
const sortBy = ref('item_code')
const sortDir = ref('asc')
const stats = reactive({ total: 0, pu: 0, suide: 0, subkon: 0 })

function onSearch() {
  page.value = 1
  reload()
}

function onSizeChange() {
  page.value = 1
  reload()
}

function onSortChange(payload) {
  const mapped = fromElSortChange(payload)
  sortBy.value = mapped.sortBy || 'item_code'
  sortDir.value = mapped.sortDir || 'asc'
  page.value = 1
  reload()
}

function goManage() {
  const erpOrigin =
    (import.meta.env.VITE_ERP_ORIGIN || '').trim() ||
    `${window.location.protocol}//${window.location.hostname}:8081`
  window.open(`${erpOrigin}/admin/master-items`, '_blank', 'noopener,noreferrer')
}

async function reload() {
  loading.value = true
  try {
    const params = buildPageParams({
      page: page.value,
      pageSize: pageSize.value,
      sortBy: sortBy.value,
      sortDir: sortDir.value,
      extra: {
        keyword: keyword.value.trim() || undefined,
        category: filterCategory.value || undefined,
      },
    })
    const data = await mrpListMasterErpPage(params)
    const pageData = normalizePageResult(data, { page: page.value, pageSize: pageSize.value })
    rows.value = pageData.items
    total.value = pageData.total
    Object.assign(stats, data.stats || { total: 0, pu: 0, suide: 0, subkon: 0 })
  } catch (e) {
    ElMessage.error(e.message || String(e))
  } finally {
    loading.value = false
  }
}

onMounted(reload)
</script>
