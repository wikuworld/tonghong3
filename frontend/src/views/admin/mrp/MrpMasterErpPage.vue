<template>
  <AdminSection :title="t('pages.mrpMasterErp.title')" :subtitle="t('pages.mrpMasterErp.subtitle')">
    <template #actions>
      <el-input v-model="keyword" clearable :placeholder="t('common.search')" class="w-56" @keyup.enter="onSearch" />
      <el-select v-model="filterCategory" clearable :placeholder="t('pages.mrpMasterErp.filterCategory')" class="w-36" @change="onSearch">
        <el-option :label="t('pages.mrpMasterErp.allCategory')" value="" />
        <el-option label="PU" value="PU" />
        <el-option label="Suide" value="Suide" />
        <el-option label="SubKon" value="SubKon" />
      </el-select>
      <el-button :icon="Refresh" :loading="loading" @click="reload">{{ t('common.refresh') }}</el-button>
      <el-button type="primary" @click="goManage">{{ t('pages.mrpMasterErp.manageItems') }}</el-button>
    </template>

    <p v-if="stats.total" class="text-sm text-gray-500 mb-2">
      {{ t('pages.mrpMasterErp.statsHint', { shown: rows.length, total }) }}
      · {{ t('pages.mrpMasterErp.sourceHint') }}
    </p>

    <div class="admin-inner-card">
      <el-table :data="rows" v-loading="loading" border stripe size="small" class="admin-table" max-height="60vh">
        <el-table-column type="index" width="56" :label="t('common.noLabel')" align="center">
          <template #default="{ $index }">{{ (page - 1) * pageSize + $index + 1 }}</template>
        </el-table-column>
        <el-table-column prop="category" :label="t('common.category')" width="90" align="center" />
        <el-table-column prop="item_code" :label="t('common.code')" min-width="100" show-overflow-tooltip />
        <el-table-column prop="material_name" :label="t('common.material')" min-width="160" show-overflow-tooltip />
        <el-table-column prop="thickness_range" :label="t('common.thickness')" width="100" align="center" />
        <el-table-column prop="color" :label="t('common.color')" min-width="120" show-overflow-tooltip />
        <el-table-column prop="emboss" :label="t('common.emboss')" min-width="120" show-overflow-tooltip />
        <el-table-column prop="backing" label="Backer" width="120" show-overflow-tooltip />
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
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Refresh } from '@element-plus/icons-vue'
import AdminSection from '../../../components/AdminSection.vue'
import { listMasterItemsPage } from '../../../api/client'

const { t } = useI18n()
const router = useRouter()
const loading = ref(false)
const rows = ref([])
const keyword = ref('')
const filterCategory = ref('')
const page = ref(1)
const pageSize = ref(50)
const total = ref(0)
const stats = reactive({ total: 0, pu: 0, suide: 0, subkon: 0 })

function onSearch() {
  page.value = 1
  reload()
}

function onSizeChange() {
  page.value = 1
  reload()
}

function goManage() {
  router.push('/admin/master-items')
}

async function reload() {
  loading.value = true
  try {
    const data = await listMasterItemsPage({
      limit: pageSize.value,
      offset: (page.value - 1) * pageSize.value,
      keyword: keyword.value.trim() || undefined,
      category: filterCategory.value || undefined,
    })
    rows.value = data.items || []
    total.value = data.total || 0
    Object.assign(stats, data.stats || { total: 0, pu: 0, suide: 0, subkon: 0 })
  } catch (e) {
    ElMessage.error(e.message || String(e))
  } finally {
    loading.value = false
  }
}

onMounted(reload)
</script>
