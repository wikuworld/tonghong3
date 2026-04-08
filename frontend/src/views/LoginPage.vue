<template>
  <div class="min-h-screen bg-slate-50 flex items-center justify-center p-4">
    <div class="w-full max-w-sm rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
      <div class="mb-4">
        <div class="text-lg font-semibold text-slate-800">{{ t('pages.login.title') }}</div>
        <div class="text-sm text-slate-500">{{ t('pages.login.subtitle') }}</div>
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
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { login } from '../api/client'

const { t } = useI18n()
const router = useRouter()
const route = useRoute()

const username = ref('')
const password = ref('')
const loading = ref(false)

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

