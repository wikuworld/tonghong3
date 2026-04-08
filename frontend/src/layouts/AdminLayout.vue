<template>
  <el-container class="admin-root min-h-screen">
    <el-aside width="240px" class="admin-sidebar border-r border-slate-200 bg-slate-900 text-white">
      <div class="border-b border-slate-800 px-5 py-4">
        <div class="flex items-center gap-3">
          <img :src="logoPath" alt="CDS Logo" class="h-8 w-auto object-contain" />
          <div>
            <div class="text-lg font-semibold leading-tight text-white">
              {{ t('appName') }}
            </div>
            <div class="mt-1 text-xs tracking-wide text-slate-300">
              {{ t('appSubtitle') }}
            </div>
          </div>
        </div>
      </div>
      <el-menu
        :default-active="route.path"
        class="admin-sidebar-menu el-menu-vertical-demo border-none bg-transparent text-white"
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
      <el-header class="admin-header flex min-h-[56px] flex-wrap items-center justify-between gap-3 border-b border-slate-200 bg-white py-2">
        <div class="min-w-0 flex-1">
          <h1 class="truncate text-base font-semibold text-slate-800">
            {{ t(route.meta.titleKey || 'menu.dashboard') }}
          </h1>
        </div>
        <div class="flex shrink-0 flex-wrap items-center gap-2 sm:gap-3">
          <el-badge :value="unreadCount" :hidden="unreadCount <= 0" class="admin-notification-badge">
            <el-popover placement="bottom-end" :width="340" trigger="click" @show="loadNotifications">
              <template #reference>
                <el-button circle>
                  <el-icon><Bell /></el-icon>
                </el-button>
              </template>
              <template #default>
                <div class="flex items-center justify-between">
                  <strong>{{ t('common.notifications') }}</strong>
                  <el-button text type="primary" @click="handleMarkAllRead">
                    {{ t('common.markAllRead') }}
                  </el-button>
                </div>
                <el-divider class="my-2" />
                <div v-if="notifications.length === 0" class="text-sm text-slate-500">
                  {{ t('common.noNotifications') }}
                </div>
                <div v-else class="admin-notification-list">
                  <div
                    v-for="item in notifications"
                    :key="item.id"
                    class="admin-notification-item"
                    :class="{ 'is-read': item.is_read }"
                    @click="handleReadNotification(item)"
                  >
                    <div class="font-medium">{{ item.title }}</div>
                    <div v-if="item.message" class="text-xs text-slate-500">{{ item.message }}</div>
                  </div>
                </div>
              </template>
            </el-popover>
          </el-badge>
          <el-dropdown trigger="click">
            <el-button>
              <el-icon class="mr-1"><UserFilled /></el-icon>
              {{ currentUser?.username || '-' }}
            </el-button>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item disabled>
                  {{ t('common.profileUser') }}: {{ currentUser?.username || '-' }}
                </el-dropdown-item>
                <el-dropdown-item disabled>
                  {{ t('common.profileRole') }}: {{ currentUser?.role || '-' }}
                </el-dropdown-item>
                <el-dropdown-item disabled>
                  {{ t('common.profileStatus') }}:
                  {{ currentUser?.is_active ? t('status.active') : t('status.inactive') }}
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
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

      <el-main class="admin-main min-w-0 overflow-x-auto bg-slate-50 p-4">
        <router-view />
      </el-main>
      <el-footer class="admin-footer">
        <span>{{ t('common.poweredBy') }} : PT Creative Digital Solutions</span>
      </el-footer>
    </el-container>
  </el-container>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
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
  Bell,
  UserFilled,
} from '@element-plus/icons-vue'
import {
  getPermissionMatrix,
  listNotifications,
  markAllNotificationsRead,
  markNotificationRead,
  me,
  unreadNotificationsCount,
} from '../api/client'
import { roleAllowsMenu } from '../security/rbac'
import { setRuntimePermissionMatrix } from '../security/permissions'

const route = useRoute()
const router = useRouter()
const { t, locale } = useI18n()
const logoPath = '/cds_logo.png'

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
const notifications = ref([])
const unreadCount = ref(0)
let unreadTimer = null

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

function updateDocumentTitle() {
  const sectionTitle = t(route.meta.titleKey || 'menu.dashboard')
  document.title = `${sectionTitle} | ${t('appName')}`
}

watch([() => route.fullPath, () => locale.value], () => {
  updateDocumentTitle()
})

onMounted(async () => {
  updateDocumentTitle()
  try {
    currentUser.value = await me()
    unreadCount.value = Number((await unreadNotificationsCount()).unread_count || 0)
    const pm = await getPermissionMatrix().catch(() => null)
    if (pm?.matrix) setRuntimePermissionMatrix(pm.matrix)
  } catch (e) {
    localStorage.removeItem('auth_token')
    ElMessage.error(e.message || t('common.sessionExpired'))
    router.replace({ path: '/login', query: { next: route.fullPath } })
  }
  unreadTimer = setInterval(async () => {
    try {
      unreadCount.value = Number((await unreadNotificationsCount()).unread_count || 0)
    } catch {
      // ignore periodic polling error
    }
  }, 30000)
})

onBeforeUnmount(() => {
  if (unreadTimer) clearInterval(unreadTimer)
})

async function loadNotifications() {
  try {
    notifications.value = await listNotifications({ limit: 10 })
    unreadCount.value = Number((await unreadNotificationsCount()).unread_count || 0)
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  }
}

async function handleReadNotification(item) {
  try {
    if (!item.is_read) {
      await markNotificationRead(item.id)
      item.is_read = true
      unreadCount.value = Math.max(0, unreadCount.value - 1)
    }
    const targetPath = String(item.route_path || '').trim()
    const targetQuery =
      item.route_query && typeof item.route_query === 'object' ? item.route_query : {}
    if (targetPath && targetPath.startsWith('/admin')) {
      const target = router.resolve({ path: targetPath, query: targetQuery })
      const requiredRoles = target.meta?.roles
      const isAllowed =
        !Array.isArray(requiredRoles) ||
        currentRole.value === 'admin' ||
        requiredRoles.includes(currentRole.value)

      if (target.matched.length === 0) {
        ElMessage.warning(t('common.notificationTargetMissing'))
      } else if (!isAllowed) {
        ElMessage.warning(t('common.notificationNoAccess'))
        if (route.path !== '/admin/dashboard') router.push('/admin/dashboard')
      } else if (route.fullPath !== target.fullPath) {
        router.push(target)
      }
    }
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  }
}

async function handleMarkAllRead() {
  try {
    await markAllNotificationsRead()
    notifications.value = notifications.value.map((item) => ({ ...item, is_read: true }))
    unreadCount.value = 0
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  }
}
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

.admin-sidebar {
  position: fixed;
  top: 0;
  left: 0;
  bottom: 0;
  z-index: 30;
  overflow: hidden;
}

.admin-sidebar-menu {
  height: calc(100vh - 82px);
  overflow-y: auto;
}

.admin-locale-select {
  width: 140px;
}

.admin-notification-badge :deep(.el-badge__content) {
  z-index: 1;
}

.admin-notification-list {
  max-height: 320px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.admin-notification-item {
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 8px 10px;
  cursor: pointer;
  background: #ffffff;
}

.admin-notification-item.is-read {
  opacity: 0.7;
}

.admin-header {
  position: fixed;
  top: 0;
  left: 240px;
  right: 0;
  z-index: 20;
}

.admin-main {
  margin-left: 240px;
  margin-top: 56px;
  margin-bottom: 40px;
  min-height: calc(100vh - 96px);
}

.admin-footer {
  position: fixed;
  left: 240px;
  right: 0;
  bottom: 0;
  z-index: 20;
  min-height: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-top: 1px solid #e2e8f0;
  background: #ffffff;
  color: #64748b;
  font-size: 12px;
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
