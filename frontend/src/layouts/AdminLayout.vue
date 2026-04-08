<template>
  <el-container class="admin-root min-h-screen">
    <el-aside width="240px" class="border-r border-slate-200 bg-slate-900 text-white">
      <div class="border-b border-slate-800 px-5 py-4">
        <div class="text-lg font-semibold leading-tight text-white">
          {{ t('appName') }}
        </div>
        <div class="mt-1 text-xs tracking-wide text-slate-300">
          {{ t('appSubtitle') }}
        </div>
      </div>
      <el-menu
        :default-active="route.path"
        class="el-menu-vertical-demo border-none bg-transparent text-white"
        background-color="#0f172a"
        text-color="#cbd5e1"
        active-text-color="#ffffff"
        @select="goTo"
      >
        <el-menu-item-group :title="t('common.nav.erp')">
          <el-menu-item v-for="item in filteredErpMenus" :key="item.path" :index="item.path">
            <el-icon><component :is="item.icon" /></el-icon>
            <span>{{ t(item.labelKey) }}</span>
          </el-menu-item>
        </el-menu-item-group>
        <el-menu-item-group :title="t('common.nav.mrp')">
          <el-menu-item v-for="item in filteredMrpMenus" :key="item.path" :index="item.path">
            <el-icon><component :is="item.icon" /></el-icon>
            <span>{{ t(item.labelKey) }}</span>
          </el-menu-item>
        </el-menu-item-group>
      </el-menu>
    </el-aside>

    <el-container class="admin-layout-main min-w-0 flex-1">
      <el-header class="flex min-h-[56px] flex-wrap items-center justify-between gap-3 border-b border-slate-200 bg-white py-2">
        <div class="min-w-0 flex-1">
          <h1 class="truncate text-base font-semibold text-slate-800">
            {{ t(route.meta.titleKey || 'menu.dashboard') }}
          </h1>
        </div>
        <div class="flex shrink-0 flex-wrap items-center gap-2 sm:gap-3">
          <span class="hidden text-sm text-slate-500 sm:inline">{{ t('common.language') }}</span>
          <el-select
            v-model="currentLocale"
            class="admin-locale-select"
            @change="onChangeLocale"
          >
            <el-option
              v-for="option in localeOptions"
              :key="option.value"
              :label="option.label"
              :value="option.value"
            />
          </el-select>
        </div>
      </el-header>

      <el-main class="min-w-0 overflow-x-auto bg-slate-50 p-4">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { ElMessage } from 'element-plus'
import {
  DataAnalysis,
  User,
  ShoppingCart,
  Operation,
  CircleCheck,
  Van,
  Tickets,
  Document,
  Coin,
  Box,
  FolderOpened,
  Sell,
  Guide,
} from '@element-plus/icons-vue'
import { getPermissionMatrix, me } from '../api/client'
import { roleAllowsMenu } from '../security/rbac'
import { setRuntimePermissionMatrix } from '../security/permissions'

const route = useRoute()
const router = useRouter()
const { t, locale } = useI18n()

const currentLocale = computed({
  get: () => locale.value,
  set: (value) => {
    locale.value = value
  },
})

const localeOptions = computed(() => [
  { value: 'id', label: t('common.languageOptions.id') },
  { value: 'en', label: t('common.languageOptions.en') },
  { value: 'zh', label: t('common.languageOptions.zh') },
])

const currentUser = ref(null)
const currentRole = computed(() => currentUser.value?.role || 'guest')

const erpMenus = [
  { path: '/admin/dashboard', labelKey: 'menu.dashboard', icon: DataAnalysis },
  { path: '/admin/customers', labelKey: 'menu.customers', icon: User },
  { path: '/admin/exchange-rates', labelKey: 'menu.exchangeRate', icon: Coin },
  { path: '/admin/po', labelKey: 'menu.po', icon: ShoppingCart },
  { path: '/admin/marketing-flow', labelKey: 'menu.marketingFlow', icon: Guide },
  { path: '/admin/delivery', labelKey: 'menu.delivery', icon: Van },
  { path: '/admin/invoice', labelKey: 'menu.invoice', icon: Tickets },
  { path: '/admin/reports', labelKey: 'menu.reports', icon: Document },
  { path: '/admin/buyer-prices', labelKey: 'menu.buyerPrices', icon: Sell },
  { path: '/admin/customs', labelKey: 'menu.customs', icon: FolderOpened },
  { path: '/admin/master-import', labelKey: 'menu.masterImport', icon: FolderOpened },
  { path: '/admin/user-access', labelKey: 'menu.userAccess', icon: User },
]

const mrpMenus = [
  { path: '/admin/production', labelKey: 'menu.production', icon: Operation },
  { path: '/admin/qc', labelKey: 'menu.qc', icon: CircleCheck },
  { path: '/admin/packing', labelKey: 'menu.packing', icon: Box },
]

const filteredErpMenus = computed(() =>
  erpMenus.filter((m) => roleAllowsMenu(currentRole.value, m.labelKey)),
)
const filteredMrpMenus = computed(() =>
  mrpMenus.filter((m) => roleAllowsMenu(currentRole.value, m.labelKey)),
)

const goTo = (path) => {
  router.push(path)
}

const onChangeLocale = (value) => {
  locale.value = value
}

onMounted(async () => {
  try {
    currentUser.value = await me()
    const pm = await getPermissionMatrix().catch(() => null)
    if (pm?.matrix) setRuntimePermissionMatrix(pm.matrix)
  } catch (e) {
    localStorage.removeItem('auth_token')
    ElMessage.error(e.message || t('common.sessionExpired'))
    router.replace({ path: '/login', query: { next: route.fullPath } })
  }
})
</script>

<style scoped>
.admin-root {
  width: 100%;
  max-width: 100vw;
}

.admin-layout-main {
  min-width: 0;
  flex: 1 1 auto;
}

.admin-locale-select {
  width: 140px;
}

@media (min-width: 640px) {
  .admin-locale-select {
    width: 150px;
  }
}

:deep(.el-menu-item:hover) {
  background-color: #1e293b;
}
:deep(.el-menu-item.is-active) {
  background-color: #2563eb;
}
</style>
