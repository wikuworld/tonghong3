<template>
  <div class="login-page min-h-screen bg-slate-50 flex items-center justify-center p-4">
    <div class="w-full max-w-sm rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
      <div class="mb-4 flex items-center gap-3">
        <img :src="logoPath" alt="CDS Logo" class="h-9 w-auto object-contain" />
        <div>
          <div class="text-lg font-semibold text-slate-800">{{ t('pages.login.title') }}</div>
          <div class="text-sm text-slate-500">{{ t('pages.login.subtitle') }}</div>
        </div>
      </div>
      <el-form label-position="top">
        <el-form-item :label="t('pages.login.username')">
          <el-input v-model="username" autocomplete="username" />
        </el-form-item>
        <el-form-item :label="t('pages.login.password')">
          <el-input v-model="password" type="password" autocomplete="current-password" show-password />
        </el-form-item>
        <el-button type="primary" class="w-full" :loading="loading" @click="submit">
          {{ t('pages.login.signIn') }}
        </el-button>
      </el-form>
    </div>
    <div class="login-footer">
      <span>{{ t('common.poweredBy') }} : PT Creative Digital Solutions</span>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { login } from '../api/client'

const { t, locale } = useI18n()
const router = useRouter()
const route = useRoute()

const username = ref('')
const password = ref('')
const loading = ref(false)
const logoPath = '/cds_logo.png'

function updateDocumentTitle() {
  document.title = `${t('pages.login.title')} | ${t('appName')}`
}

watch(() => locale.value, () => {
  updateDocumentTitle()
})

onMounted(() => {
  updateDocumentTitle()
})

async function submit() {
  loading.value = true
  try {
    const res = await login(username.value, password.value)
    localStorage.setItem('auth_token', res.access_token)
    const next = route.query.next ? String(route.query.next) : '/admin/dashboard'
    router.replace(next)
  } catch (e) {
    ElMessage.error(e.message || t('pages.login.failed'))
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  position: relative;
  padding-bottom: 56px;
}

.login-footer {
  position: fixed;
  left: 0;
  right: 0;
  bottom: 0;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-top: 1px solid #e2e8f0;
  background: #ffffff;
  color: #64748b;
  font-size: 12px;
}
</style>

