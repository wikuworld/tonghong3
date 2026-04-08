<template>
  <AdminSection :title="t('pages.poDetail.title')" :subtitle="t('pages.poDetail.subtitle')">
    <el-form label-position="top">
      <el-row :gutter="12">
        <el-col :xs="24" :md="8">
          <el-form-item :label="t('common.buyer')">
            <el-input v-model="form.buyer" :placeholder="t('common.placeholder.buyer')" />
          </el-form-item>
        </el-col>
        <el-col :xs="24" :md="8">
          <el-form-item :label="t('common.material')">
            <el-input v-model="form.material" :placeholder="t('common.placeholder.material')" />
          </el-form-item>
        </el-col>
        <el-col :xs="24" :md="8">
          <el-form-item :label="t('common.thickness')">
            <el-input v-model="form.thickness" :placeholder="t('common.placeholder.thickness')" />
          </el-form-item>
        </el-col>
        <el-col :xs="24" :md="8">
          <el-form-item :label="t('common.color')">
            <el-select v-model="form.color" class="w-full" :placeholder="t('common.placeholder.color')">
              <el-option label="Black" value="black" />
              <el-option label="Grey" value="grey" />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :xs="24" :md="8">
          <el-form-item :label="t('common.softness')">
            <el-input v-model="form.softness" :placeholder="t('common.placeholder.softness')" />
          </el-form-item>
        </el-col>
        <el-col :xs="24" :md="8">
          <el-form-item :label="t('common.quantity')">
            <el-input v-model="form.quantity" :placeholder="t('common.placeholder.quantity')" />
          </el-form-item>
        </el-col>
        <el-col :xs="24">
          <el-form-item :label="t('common.remark')">
            <el-input v-model="form.remark" type="textarea" :rows="3" :placeholder="t('common.placeholder.remark')" />
          </el-form-item>
        </el-col>
      </el-row>
    </el-form>

    <div class="mt-3 flex justify-end gap-2">
      <el-button>{{ t('common.cancel') }}</el-button>
      <el-button type="primary">{{ t('common.confirm') }}</el-button>
    </div>
  </AdminSection>
</template>

<script setup>
import { reactive } from 'vue'
import { useI18n } from 'vue-i18n'
import AdminSection from '../../components/AdminSection.vue'

const { t } = useI18n()

const form = reactive({
  buyer: '',
  material: '',
  thickness: '1.2 - 1.4',
  color: 'black',
  softness: 'Auto by buyer',
  quantity: '',
  remark: '',
})
</script>
