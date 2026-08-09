<template>
  <AdminSection :title="t('pages.mrpMasterErp.title')" :subtitle="t('pages.mrpMasterErp.subtitle')">
    <template #actions>
      <el-input v-model="keyword" clearable :placeholder="t('common.search')" class="w-56" />
      <el-button :icon="Refresh" :loading="loading" @click="reload">{{ t('common.refresh') }}</el-button>
    </template>
    <div class="admin-inner-card">
      <el-table :data="filtered" v-loading="loading" border stripe size="small" class="admin-table" max-height="60vh">
        <el-table-column type="index" width="56" :label="t('common.noLabel')" align="center" />
        <el-table-column prop="thickness" label="Thickness" width="100" />
        <el-table-column prop="material_name" label="Material" min-width="140" />
        <el-table-column prop="color" label="Color" width="120" />
        <el-table-column prop="emboss" label="Emboss" width="120" />
        <el-table-column prop="color_swatch" label="Swatch" width="120" />
        <el-table-column prop="backer" label="Backer" width="120" />
        <el-table-column prop="customer" :label="t('common.customer')" min-width="120" />
      </el-table>
    </div>
  </AdminSection>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessage } from 'element-plus'
import { Refresh } from '@element-plus/icons-vue'
import AdminSection from '../../../components/AdminSection.vue'
import { mrpListMasterErp } from '../../../api/client'

const { t } = useI18n()
const loading = ref(false)
const rows = ref([])
const keyword = ref('')
const filtered = computed(() => {
  const q = keyword.value.trim().toLowerCase()
  if (!q) return rows.value
  return rows.value.filter((r) =>
    [r.thickness, r.material_name, r.color, r.emboss, r.color_swatch, r.customer, r.backer]
      .filter(Boolean)
      .some((v) => String(v).toLowerCase().includes(q)),
  )
})

async function reload() {
  loading.value = true
  try {
    rows.value = await mrpListMasterErp()
  } catch (e) {
    ElMessage.error(e.message || String(e))
  } finally {
    loading.value = false
  }
}

onMounted(reload)
</script>
