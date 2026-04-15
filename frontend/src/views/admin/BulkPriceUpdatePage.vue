<template>
  <AdminSection :title="t('pages.bulkPriceUpdate.title')" :subtitle="t('pages.bulkPriceUpdate.subtitle')">
    <el-tabs v-model="activeTab">
      <el-tab-pane :label="t('pages.bulkPriceUpdate.singleUpdate')" name="single">
        <el-form :model="singleForm" label-position="top" class="max-w-lg">
          <el-form-item :label="t('pages.bulkPriceUpdate.buyerCode')">
            <el-input v-model="singleForm.buyer_code" />
          </el-form-item>
          <el-form-item :label="t('pages.bulkPriceUpdate.materialPattern')">
            <el-input v-model="singleForm.material_pattern" />
          </el-form-item>
          <el-form-item :label="t('pages.bulkPriceUpdate.newPrice')">
            <el-input-number v-model="singleForm.new_price" :min="0" :precision="4" class="w-full" />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" :loading="saving" @click="submitSingle">
              {{ t('pages.bulkPriceUpdate.update') }}
            </el-button>
          </el-form-item>
        </el-form>
      </el-tab-pane>

      <el-tab-pane :label="t('pages.bulkPriceUpdate.csvUpload')" name="csv">
        <el-upload
          ref="uploadRef"
          :auto-upload="false"
          :limit="1"
          accept=".csv"
          :on-change="handleFileChange"
        >
          <el-button type="primary">{{ t('pages.bulkPriceUpdate.selectFile') }}</el-button>
        </el-upload>
        <div class="mt-4">
          <el-button type="success" :disabled="!csvFile" :loading="uploading" @click="submitCsv">
            {{ t('pages.bulkPriceUpdate.uploadAndUpdate') }}
          </el-button>
        </div>
        <div class="mt-4 text-xs text-slate-500">
          <p>{{ t('pages.bulkPriceUpdate.csvFormat') }}:</p>
          <code>buyer_code,material_pattern,new_price</code>
        </div>
      </el-tab-pane>
    </el-tabs>
  </AdminSection>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessage } from 'element-plus'
import AdminSection from '../../components/AdminSection.vue'
import { bulkUpdatePrices, bulkUpdatePricesCsv } from '../../api/client'

const { t } = useI18n()

const activeTab = ref('single')
const saving = ref(false)
const uploading = ref(false)
const csvFile = ref(null)
const uploadRef = ref(null)

const singleForm = reactive({
  buyer_code: '',
  material_pattern: '',
  new_price: 0,
})

async function submitSingle() {
  if (!singleForm.buyer_code || !singleForm.material_pattern) {
    ElMessage.warning(t('pages.bulkPriceUpdate.fillAllFields'))
    return
  }
  saving.value = true
  try {
    const result = await bulkUpdatePrices({
      updates: [{ ...singleForm }]
    })
    ElMessage.success(t('pages.bulkPriceUpdate.updatedCount', { count: result.updated }))
  } catch (e) {
    ElMessage.error(e.message)
  } finally {
    saving.value = false
  }
}

function handleFileChange(file) {
  csvFile.value = file.raw
}

async function submitCsv() {
  if (!csvFile.value) return
  uploading.value = true
  try {
    const result = await bulkUpdatePricesCsv(csvFile.value)
    ElMessage.success(t('pages.bulkPriceUpdate.updatedCount', { count: result.updated }))
    csvFile.value = null
    uploadRef.value?.clearFiles()
  } catch (e) {
    ElMessage.error(e.message)
  } finally {
    uploading.value = false
  }
}
</script>
