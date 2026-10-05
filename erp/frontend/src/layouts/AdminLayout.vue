<template>
  <el-container class="admin-root">
    <el-aside :width="isSidebarCollapsed ? '64px' : '240px'" class="admin-sidebar">
      <div class="border-b border-slate-800 px-5 py-4" :class="{ 'px-2': isSidebarCollapsed }">
        <div class="flex items-center gap-3">
          <img v-show="!isSidebarCollapsed" :src="logoPath" alt="CDS Logo" class="h-8 w-auto object-contain" />
          <div v-show="!isSidebarCollapsed">
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
        :default-active="activeMenuPath"
        :collapse="isSidebarCollapsed"
        :collapse-transition="false"
        class="admin-sidebar-menu"
        background-color="#0f172a"
        text-color="#cbd5e1"
        active-text-color="#ffffff"
        @select="goTo"
      >
        <el-menu-item v-if="can('dashboard', 'view', currentRole)" index="/admin/dashboard">
          <el-icon><DataAnalysis /></el-icon>
          <span>{{ t('menu.dashboard') }}</span>
        </el-menu-item>

        <div v-show="!isSidebarCollapsed" class="px-3 py-2 mt-2 text-xs font-semibold uppercase tracking-wider text-slate-400">
          {{ t('common.nav.erp') }}
        </div>

        <el-sub-menu v-if="filteredErpSalesMenus.length" index="erp-sales">
          <template #title>
            <el-icon><Share /></el-icon>
            <span>{{ t('common.nav.sales') }}</span>
          </template>
          <template v-for="item in filteredErpSalesMenus" :key="item.path">
            <el-sub-menu v-if="item.children?.length" :index="item.path">
              <template #title>
                <span class="admin-subgroup-title">
                  <el-icon><component :is="item.icon" /></el-icon>
                  <span>{{ t(item.labelKey) }}</span>
                </span>
              </template>
              <el-menu-item
                v-for="child in item.children"
                :key="child.path"
                :index="child.path"
              >
                <el-icon><component :is="child.icon" /></el-icon>
                <span>{{ t(child.labelKey) }}</span>
              </el-menu-item>
            </el-sub-menu>
            <el-menu-item v-else :index="item.path">
              <el-icon><component :is="item.icon" /></el-icon>
              <span>{{ t(item.labelKey) }}</span>
            </el-menu-item>
          </template>
        </el-sub-menu>

        <el-sub-menu v-if="filteredErpFulfillmentMenus.length" index="erp-fulfillment">
          <template #title>
            <el-icon><Van /></el-icon>
            <span>{{ t('common.nav.fulfillment') }}</span>
          </template>
          <el-menu-item v-for="item in filteredErpFulfillmentMenus" :key="item.path" :index="item.path">
            <el-icon><component :is="item.icon" /></el-icon>
            <span>{{ t(item.labelKey) }}</span>
          </el-menu-item>
        </el-sub-menu>

        <el-sub-menu v-if="filteredErpBookMenus.length" index="erp-book">
          <template #title>
            <el-icon><Operation /></el-icon>
            <span>{{ t('common.nav.erpBookGroup') }}</span>
          </template>
          <el-menu-item v-for="item in filteredErpBookMenus" :key="item.path" :index="item.path">
            <el-icon><component :is="item.icon" /></el-icon>
            <span>{{ t(item.labelKey) }}</span>
          </el-menu-item>
        </el-sub-menu>

        <el-sub-menu v-if="filteredErpMasterMenus.length" index="erp-master">
          <template #title>
            <el-icon><Files /></el-icon>
            <span>{{ t('common.nav.masterData') }}</span>
          </template>
          <template v-for="group in filteredErpMasterMenus" :key="group.path">
            <el-sub-menu v-if="group.children?.length" :index="group.path">
              <template #title>
                <span class="admin-subgroup-title">
                  <el-icon><component :is="group.icon" /></el-icon>
                  <span>{{ t(group.labelKey) }}</span>
                </span>
              </template>
              <el-menu-item
                v-for="item in group.children"
                :key="item.path"
                :index="item.path"
              >
                <el-icon><component :is="item.icon" /></el-icon>
                <span>{{ t(item.labelKey) }}</span>
              </el-menu-item>
            </el-sub-menu>
            <el-menu-item v-else :index="group.path">
              <el-icon><component :is="group.icon" /></el-icon>
              <span>{{ t(group.labelKey) }}</span>
            </el-menu-item>
          </template>
        </el-sub-menu>

        <el-sub-menu v-if="filteredErpSystemMenus.length" index="erp-system">
          <template #title>
            <el-icon><Setting /></el-icon>
            <span>{{ t('common.nav.system') }}</span>
          </template>
          <el-menu-item v-for="item in filteredErpSystemMenus" :key="item.path" :index="item.path">
            <el-icon><component :is="item.icon" /></el-icon>
            <span>{{ t(item.labelKey) }}</span>
          </el-menu-item>
        </el-sub-menu>

        <!-- Inventory & MRP menus removed; live on mrp/frontend -->
      </el-menu>
    </el-aside>

    <el-container>
      <el-header class="admin-header" :style="{ left: isSidebarCollapsed ? '64px' : '240px' }">
        <el-button text @click="toggleSidebar">
          <el-icon size="20">
            <Expand v-if="isSidebarCollapsed" />
            <Fold v-else />
          </el-icon>
        </el-button>
        
        <div class="flex items-center gap-2 ml-auto">
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
            <el-button circle>
              <el-icon><UserFilled /></el-icon>
            </el-button>
            <template #dropdown>
              <el-dropdown-menu>
                <div class="px-4 py-2 border-b border-gray-100">
                  <div class="font-medium">{{ currentUser?.username || '-' }}</div>
                  <div class="text-xs text-gray-500">{{ currentUser?.role || '-' }}</div>
                </div>
                <el-dropdown-item disabled>
                  <span class="text-gray-400">{{ t('common.profileUser') }}:</span> {{ currentUser?.username || '-' }}
                </el-dropdown-item>
                <el-dropdown-item disabled>
                  <span class="text-gray-400">{{ t('common.profileRole') }}:</span> {{ currentUser?.role || '-' }}
                </el-dropdown-item>
                <el-dropdown-item disabled>
                  <span class="text-gray-400">{{ t('common.profileStatus') }}:</span>
                  {{ currentUser?.is_active ? t('status.active') : t('status.inactive') }}
                </el-dropdown-item>
                <el-dropdown-item divided @click="handleLogout">
                  {{ t('common.logout') }}
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
          
          <el-dropdown trigger="click" @command="onChangeLocale">
            <el-button circle>
              <span class="text-xs font-bold">{{ getCurrentLangCode() }}</span>
            </el-button>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item v-for="lang in languageOptions" :key="lang.value" :command="lang.value">
                  <span class="flex items-center gap-2">
                    <span class="w-8 text-center font-bold">{{ lang.code }}</span>
                    <span>{{ lang.label }}</span>
                    <el-icon v-if="currentLocale === lang.value" class="ml-auto"><Check /></el-icon>
                  </span>
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>

      <el-main class="admin-main" :style="{ marginLeft: isSidebarCollapsed ? '64px' : '240px' }">
        <router-view v-slot="{ Component }">
          <component v-if="Component" :is="Component" :key="route.path" />
        </router-view>
      </el-main>

      <el-footer class="admin-footer" :style="{ left: isSidebarCollapsed ? '64px' : '240px' }">
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
  Bell,
  UserFilled,
  Fold,
  Expand,
  Check,
  DataAnalysis,
  ShoppingCart,
  Van,
  Tickets,
  Document,
  Files,
  Setting,
  Share,
  Box,
  Sell,
  CollectionTag,
  Coin,
  Goods,
  Operation,
  CircleCheck,
  User,
  FolderOpened,
  Monitor,
} from '@element-plus/icons-vue'
import {
  getPermissionMatrix,
  listNotifications,
  markAllNotificationsRead,
  markNotificationRead,
  me,
  unreadNotificationsCount,
} from '../api/client'
import { can, permissionMatrixVersion, setRuntimePermissionMatrix } from '../security/permissions'
import { roleAllowsMenu } from '../security/rbac'

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

const languageOptions = [
  { value: 'id', label: 'Indonesia', code: 'ID' },
  { value: 'en', label: 'English', code: 'EN' },
  { value: 'zh', label: '中文', code: 'ZH' },
]

function getCurrentLangCode() {
  const lang = languageOptions.find(l => l.value === currentLocale.value)
  return lang?.code || 'EN'
}

const currentUser = ref(null)
const currentRole = computed(() => currentUser.value?.role || 'guest')
const notifications = ref([])
const unreadCount = ref(0)
const isSidebarCollapsed = ref(false)
let unreadTimer = null

function applySidebarWidthVar() {
  const width = isSidebarCollapsed.value ? '64px' : '240px'
  document.documentElement.style.setProperty('--admin-sidebar-width', width)
}

function toggleSidebar() {
  isSidebarCollapsed.value = !isSidebarCollapsed.value
}

watch(isSidebarCollapsed, applySidebarWidthVar, { immediate: true })

const erpSalesMenus = [
  { path: '/admin/po', labelKey: 'menu.po', icon: ShoppingCart },
  { path: '/admin/marketing-flow/outstanding', labelKey: 'menu.marketingFlowOutstanding', icon: Document },
]

const erpFulfillmentMenus = [
  { path: '/admin/delivery', labelKey: 'menu.delivery', icon: Van },
  { path: '/admin/invoice', labelKey: 'menu.invoice', icon: Tickets },
  { path: '/admin/reports', labelKey: 'menu.reports', icon: Document },
]

const erpBookMenus = [
  { path: '/admin/production', labelKey: 'menu.production', icon: Operation },
  { path: '/admin/qc', labelKey: 'menu.qc', icon: CircleCheck },
  { path: '/admin/packing', labelKey: 'menu.packing', icon: Box },
]

const erpMasterMenus = [
  {
    path: 'erp-master-customer-brand',
    labelKey: 'common.nav.masterCustomerBrand',
    icon: User,
    children: [
      { path: '/admin/customers', labelKey: 'menu.customers', icon: User },
      { path: '/admin/brands', labelKey: 'menu.brandMaster', icon: CollectionTag },
      // Disembunyikan sementara: halaman Mapping Customer-Brand tidak dipakai.
      // { path: '/admin/customer-brand-mapping', labelKey: 'menu.customerBrandMapping', icon: CollectionTag },
    ],
  },
  {
    path: 'erp-master-pricing',
    labelKey: 'common.nav.masterPricing',
    icon: Sell,
    children: [
      { path: '/admin/buyer-prices', labelKey: 'menu.buyerPrices', icon: Sell },
      { path: '/admin/bulk-price-update', labelKey: 'menu.bulkPriceUpdate', icon: Coin },
    ],
  },
  {
    path: 'erp-master-items-colors',
    labelKey: 'common.nav.masterItemsColors',
    icon: Box,
    children: [
      { path: '/admin/master-items', labelKey: 'menu.masterItems', icon: Box },
      { path: '/admin/color-swatch', labelKey: 'menu.colorSwatch', icon: CollectionTag },
      { path: '/admin/fluorescent-colors', labelKey: 'menu.fluorescentColors', icon: CollectionTag },
      { path: '/admin/csi-colors', labelKey: 'menu.csiColors', icon: CollectionTag },
    ],
  },
  { path: '/admin/data-intelligent', labelKey: 'menu.dataIntelligent', icon: DataAnalysis },
]

const inventoryMenus = []

const erpSystemMenus = [
  { path: '/admin/user-access', labelKey: 'menu.userAccess', icon: User },
]

const mrpFlowMenus = []

const mrpMaterialMenus = []

const mrpMasterMenus = []

const mrpReportMenus = []

function filterMenuTree(menus) {
  permissionMatrixVersion.value
  return menus
    .map((m) => {
      if (!m.children?.length) {
        const key = m.permissionKey || m.labelKey
        return roleAllowsMenu(currentRole.value, key) ? m : null
      }
      const children = m.children.filter((c) =>
        roleAllowsMenu(currentRole.value, c.permissionKey || c.labelKey)
      )
      return children.length ? { ...m, children } : null
    })
    .filter(Boolean)
}

const filteredErpSalesMenus = computed(() => filterMenuTree(erpSalesMenus))
const filteredErpFulfillmentMenus = computed(() => filterMenuTree(erpFulfillmentMenus))
const filteredErpBookMenus = computed(() => filterMenuTree(erpBookMenus))
const filteredErpMasterMenus = computed(() => filterMenuTree(erpMasterMenus))
const filteredErpSystemMenus = computed(() => filterMenuTree(erpSystemMenus))
const filteredInventoryMenus = computed(() => filterMenuTree(inventoryMenus))
const filteredMrpFlowMenus = computed(() => filterMenuTree(mrpFlowMenus))
const filteredMrpMaterialMenus = computed(() => filterMenuTree(mrpMaterialMenus))
const filteredMrpMasterMenus = computed(() => filterMenuTree(mrpMasterMenus))
const filteredMrpReportMenus = computed(() => filterMenuTree(mrpReportMenus))

const activeMenuPath = computed(() => route.path)

const MENU_GROUP_INDEXES = new Set([
  'erp-sales',
  'erp-fulfillment',
  'erp-book',
  'erp-master',
  'erp-master-customer-brand',
  'erp-master-pricing',
  'erp-master-items-colors',
  'erp-system',
  'inventory-master',
  'mrp-flow',
  'mrp-material',
  'mrp-master',
  'mrp-reports',
])

const goTo = (path) => {
  if (!path || MENU_GROUP_INDEXES.has(path)) {
    return
  }
  if (path.includes('?')) {
    const [pathname, qs] = path.split('?')
    const query = Object.fromEntries(new URLSearchParams(qs))
    if (route.path !== pathname || JSON.stringify(route.query) !== JSON.stringify(query)) {
      router.push({ path: pathname, query })
    }
    return
  }
  if (path !== route.path) router.push(path)
}

const onChangeLocale = (value) => {
  locale.value = value
  if (typeof localStorage !== 'undefined') {
    localStorage.setItem('tonghong_locale', value)
  }
}

function handleLogout() {
  localStorage.removeItem('auth_token')
  router.replace({ path: '/login' })
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
  document.documentElement.style.removeProperty('--admin-sidebar-width')
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
      const moduleKey = target.meta?.module
      const isAllowed = !moduleKey || can(moduleKey, 'view', currentRole.value)

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
  min-height: 100vh;
}

.admin-sidebar {
  position: fixed;
  top: 0;
  left: 0;
  bottom: 0;
  background-color: #0f172a;
  transition: width 0.3s, left 0.3s;
  z-index: 100;
}

.admin-sidebar-menu {
  border: none;
  height: calc(100vh - 82px);
  overflow-y: auto;
}

.admin-sidebar-menu:not(.el-menu--collapse) {
  width: 240px;
}

.admin-menu-hint {
  margin-left: 4px;
  font-size: 10px;
  font-weight: 500;
  letter-spacing: 0.02em;
  text-transform: uppercase;
  color: #94a3b8;
  opacity: 0.9;
}

.admin-header {
  position: fixed;
  top: 0;
  left: 240px;
  right: 0;
  height: 56px;
  background-color: #ffffff;
  border-bottom: 1px solid #e2e8f0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 16px;
  z-index: 99;
  transition: left 0.3s;
}

.admin-main {
  background-color: #f8fafc;
  padding: 16px;
  margin-top: 56px;
  margin-bottom: 40px;
  min-height: calc(100vh - 96px);
}

.admin-footer {
  position: fixed;
  bottom: 0;
  left: 240px;
  right: 0;
  height: 40px;
  background-color: #ffffff;
  border-top: 1px solid #e2e8f0;
  color: #64748b;
  font-size: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 99;
  transition: left 0.3s;
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

:deep(.el-menu-item:hover) {
  background-color: #1e293b;
}
:deep(.el-menu-item.is-active) {
  background-color: #2563eb;
}
</style>
