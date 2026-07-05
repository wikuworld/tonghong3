<template>
  <AdminSection :title="t('pages.masterImport.title')" :subtitle="t('pages.masterImport.subtitle')">
    <div class="rounded border border-slate-200 bg-white p-4">
      <p class="mb-3 text-sm text-slate-600">
        Upload <b>ZIP</b> yang berisi CSV master:
        <code class="rounded bg-slate-100 px-1">00_Master_Customer.csv</code>,
        <code class="rounded bg-slate-100 px-1">01_Master_Item.csv</code>,
        <code class="rounded bg-slate-100 px-1">02_Master_Harga.csv</code>.
      </p>

      <el-upload :show-file-list="false" :http-request="doUpload" accept=".zip">
        <el-button v-if="canCreate" type="primary" :loading="uploading">{{ t('pages.masterImport.uploadZip') }}</el-button>
      </el-upload>

      <div v-if="result" class="mt-4 rounded border border-slate-200 bg-slate-50 p-3 text-sm">
        <div class="font-semibold text-slate-700">{{ t('pages.masterImport.result') }}</div>
        <pre class="mt-2 whitespace-pre-wrap break-words">{{ JSON.stringify(result, null, 2) }}</pre>
      </div>
    </div>
  </AdminSection>
</template>

<script setup>
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessage } from 'element-plus'
import AdminSection from '../../components/AdminSection.vue'
import { importMasterZip } from '../../api/client'
import { useModulePermission } from '../../composables/useModulePermission'

const { t } = useI18n()
const { canCreate } = useModulePermission('masterImport')
const uploading = ref(false)
const result = ref(null)

async function doUpload(req) {
  uploading.value = true
  result.value = null
  try {
    const file = req.file
    result.value = await importMasterZip(file)
    ElMessage.success(t('pages.masterImport.done'))
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  } finally {
    uploading.value = false
  }
}
</script>

