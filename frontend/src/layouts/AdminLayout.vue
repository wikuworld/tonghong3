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
        :default-active="route.path"
        :collapse="isSidebarCollapsed"
        :collapse-transition="false"
        class="admin-sidebar-menu"
        background-color="#0f172a"
        text-color="#cbd5e1"
        active-text-color="#ffffff"
        @select="goTo"
      >
        <div v-show="!isSidebarCollapsed" class="px-3 py-2 text-xs font-semibold uppercase tracking-wider text-slate-400">
          {{ t('common.nav.erp') }}
        </div>
        
        <el-sub-menu v-if="filteredErpFlowMenus.length" index="erp-flow">
          <template #title>
            <el-icon><Share /></el-icon>
            <span>{{ t('common.nav.flow') }}</span>
          </template>
          <template v-for="item in filteredErpFlowMenus" :key="item.path">
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

        <el-sub-menu v-if="filteredErpFinanceMenus.length" index="erp-finance">
          <template #title>
            <el-icon><Coin /></el-icon>
            <span>{{ t('common.nav.finance') }}</span>
          </template>
          <el-menu-item v-for="item in filteredErpFinanceMenus" :key="item.path" :index="item.path">
            <el-icon><component :is="item.icon" /></el-icon>
            <span>{{ t(item.labelKey) }}</span>
          </el-menu-item>
        </el-sub-menu>
        
        <el-sub-menu v-if="filteredErpMasterMenus.length" index="erp-master">
          <template #title>
            <el-icon><Files /></el-icon>
            <span>{{ t('common.nav.masterData') }}</span>
          </template>
          <el-menu-item v-for="item in filteredErpMasterMenus" :key="item.path" :index="item.path">
            <el-icon><component :is="item.icon" /></el-icon>
            <span>{{ t(item.labelKey) }}</span>
          </el-menu-item>
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
        
        <div v-show="!isSidebarCollapsed" class="px-3 py-2 mt-2 text-xs font-semibold uppercase tracking-wider text-slate-400">
          {{ t('common.nav.mrp') }}
        </div>

        <el-sub-menu v-if="filteredMrpFlowMenus.length" index="mrp-flow">
          <template #title>
            <el-icon><Operation /></el-icon>
            <span>{{ t('common.nav.flow') }}</span>
          </template>
          <el-menu-item v-for="item in filteredMrpFlowMenus" :key="item.path" :index="item.path">
            <el-icon><component :is="item.icon" /></el-icon>
            <span>{{ t(item.labelKey) }}</span>
          </el-menu-item>
        </el-sub-menu>

        <el-sub-menu v-if="filteredMrpMaterialMenus.length" index="mrp-material">
          <template #title>
            <el-icon><Goods /></el-icon>
            <span>{{ t('common.nav.materialStock') }}</span>
          </template>
          <el-menu-item v-for="item in filteredMrpMaterialMenus" :key="item.path" :index="item.path">
            <el-icon><component :is="item.icon" /></el-icon>
            <span>{{ t(item.labelKey) }}</span>
          </el-menu-item>
        </el-sub-menu>

        <el-sub-menu v-if="filteredMrpMasterMenus.length" index="mrp-master">
          <template #title>
            <el-icon><Files /></el-icon>
            <span>{{ t('common.nav.masterData') }}</span>
          </template>
          <el-menu-item v-for="item in filteredMrpMasterMenus" :key="item.path" :index="item.path">
            <el-icon><component :is="item.icon" /></el-icon>
            <span>{{ t(item.labelKey) }}</span>
          </el-menu-item>
        </el-sub-menu>

        <el-sub-menu v-if="filteredMrpReportMenus.length" index="mrp-reports">
          <template #title>
            <el-icon><Document /></el-icon>
            <span>{{ t('common.nav.reports') }}</span>
          </template>
          <el-menu-item v-for="item in filteredMrpReportMenus" :key="item.path" :index="item.path">
            <el-icon><component :is="item.icon" /></el-icon>
            <span>{{ t(item.labelKey) }}</span>
          </el-menu-item>
        </el-sub-menu>
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
          <component v-if="Component" :is="Component" :key="route.fullPath" />
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
  Guide,
  Van,
  Tickets,
  Document,
  DocumentCopy,
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

function toggleSidebar() {
  isSidebarCollapsed.value = !isSidebarCollapsed.value
}

const erpFlowMenus = [
  { path: '/admin/dashboard', labelKey: 'menu.dashboard', icon: DataAnalysis },
  { path: '/admin/quotations', labelKey: 'menu.quotations', icon: DocumentCopy },
  { path: '/admin/po', labelKey: 'menu.po', icon: ShoppingCart },
  {
    path: '/admin/marketing-flow',
    labelKey: 'menu.marketingFlow',
    icon: Guide,
    children: [
      { path: '/admin/marketing-flow/po-list', labelKey: 'menu.marketingFlowPoList', icon: Guide },
      { path: '/admin/marketing-flow/outstanding', labelKey: 'menu.marketingFlowOutstanding', icon: Document },
      { path: '/admin/marketing-flow/planning', labelKey: 'menu.marketingFlowPlanning', icon: Files },
    ],
  },
  { path: '/admin/ppic-dashboard', labelKey: 'menu.ppicDashboard', icon: Operation },
  { path: '/admin/outstanding-materials', labelKey: 'menu.outstandingMaterials', icon: Document },
  { path: '/admin/production', labelKey: 'menu.production', icon: Operation },
  { path: '/admin/qc', labelKey: 'menu.qc', icon: CircleCheck },
  { path: '/admin/packing', labelKey: 'menu.packing', icon: Box },
  { path: '/admin/delivery', labelKey: 'menu.delivery', icon: Van },
  { path: '/admin/invoice', labelKey: 'menu.invoice', icon: Tickets },
  { path: '/admin/reports', labelKey: 'menu.reports', icon: Document },
]

const erpFinanceMenus = [
  { path: '/admin/subcon-invoices', labelKey: 'menu.subconInvoice', icon: Tickets },
  { path: '/admin/accounting-mappings', labelKey: 'menu.accountingMappings', icon: Files },
  { path: '/admin/journal-entries', labelKey: 'menu.journalEntries', icon: DocumentCopy },
]

const erpMasterMenus = [
  { path: '/admin/customers', labelKey: 'menu.customers', icon: User },
  { path: '/admin/buyer-prices', labelKey: 'menu.buyerPrices', icon: Sell },
  { path: '/admin/special-prices', labelKey: 'menu.specialPrices', icon: Sell },
  { path: '/admin/customer-prices', labelKey: 'menu.customerPrices', icon: Sell },
  { path: '/admin/bulk-price-update', labelKey: 'menu.bulkPriceUpdate', icon: Coin },
  { path: '/admin/customer-brand-mapping', labelKey: 'menu.customerBrandMapping', icon: CollectionTag },
  { path: '/admin/brands', labelKey: 'menu.brandMaster', icon: CollectionTag },
  { path: '/admin/customs', labelKey: 'menu.customs', icon: FolderOpened },
  { path: '/admin/master-items', labelKey: 'menu.masterItems', icon: Box },
  { path: '/admin/fluorescent-colors', labelKey: 'menu.fluorescentColors', icon: CollectionTag },
  { path: '/admin/color-swatch', labelKey: 'menu.colorSwatch', icon: CollectionTag },
  { path: '/admin/exchange-rates', labelKey: 'menu.exchangeRate', icon: Coin },
  { path: '/admin/master-import', labelKey: 'menu.masterImport', icon: FolderOpened },
  { path: '/admin/inventory', labelKey: 'menu.inventory', icon: Goods },
]

const erpSystemMenus = [
  { path: '/admin/user-access', labelKey: 'menu.userAccess', icon: User },
]

const mrpFlowMenus = [
  { path: '/admin/mrp/rencana-produksi', labelKey: 'menu.mrpRencana', icon: Document },
  { path: '/admin/mrp/proses', labelKey: 'menu.mrpProses', icon: Operation },
  { path: '/admin/mrp/lab', labelKey: 'menu.mrpLab', icon: CollectionTag },
  { path: '/admin/mrp/packing', labelKey: 'menu.mrpPacking', icon: Box },
  { path: '/admin/mrp/gudang-fg', labelKey: 'menu.mrpGudangFg', icon: Goods },
  { path: '/admin/mrp/checkpoint', labelKey: 'menu.mrpCheckpoint', icon: CollectionTag },
]

const mrpMaterialMenus = [
  { path: '/admin/mrp/palet', labelKey: 'menu.mrpPalet', icon: Box },
  { path: '/admin/mrp/stok-kimia', labelKey: 'menu.mrpStokKimia', icon: Goods },
  { path: '/admin/mrp/stok-rp', labelKey: 'menu.mrpStokRp', icon: Goods },
  { path: '/admin/mrp/stok-material-lain', labelKey: 'menu.mrpStokMaterialLain', icon: Goods },
  { path: '/admin/mrp/usage', labelKey: 'menu.mrpUsage', icon: Operation },
]

const mrpMasterMenus = [
  { path: '/admin/mrp/masters/erp', labelKey: 'menu.mrpMasterErp', icon: Files },
  { path: '/admin/mrp/masters/kulit', labelKey: 'menu.mrpMasterKulit', icon: Files },
  { path: '/admin/mrp/masters/kimia', labelKey: 'menu.mrpMasterKimia', icon: Files },
  { path: '/admin/mrp/masters/rp', labelKey: 'menu.mrpMasterRp', icon: Files },
  { path: '/admin/mrp/masters/treatment', labelKey: 'menu.mrpMasterTreatment', icon: Files },
  { path: '/admin/mrp/masters/material-lain', labelKey: 'menu.mrpMasterMaterialLain', icon: Files },
]

const mrpReportMenus = [
  { path: '/admin/mrp/reports/packing', labelKey: 'menu.mrpReportPacking', icon: Document },
  { path: '/admin/mrp/reports/persiapan', labelKey: 'menu.mrpReportPersiapan', icon: Document },
]

const filteredErpFlowMenus = computed(() => {
  permissionMatrixVersion.value
  return erpFlowMenus
    .map((m) => {
      if (!m.children?.length) return m
      const children = m.children.filter((c) => roleAllowsMenu(currentRole.value, c.labelKey))
      return children.length ? { ...m, children } : null
    })
    .filter((m) => m && (m.children?.length || roleAllowsMenu(currentRole.value, m.labelKey)))
})
const filteredErpFinanceMenus = computed(() => {
  permissionMatrixVersion.value
  return erpFinanceMenus.filter((m) => roleAllowsMenu(currentRole.value, m.labelKey))
})
const filteredErpMasterMenus = computed(() => {
  permissionMatrixVersion.value
  return erpMasterMenus.filter((m) => roleAllowsMenu(currentRole.value, m.labelKey))
})
const filteredErpSystemMenus = computed(() => {
  permissionMatrixVersion.value
  return erpSystemMenus.filter((m) => roleAllowsMenu(currentRole.value, m.labelKey))
})
function filterMrpMenuList(menus) {
  permissionMatrixVersion.value
  return menus.filter((m) => roleAllowsMenu(currentRole.value, m.labelKey))
}
const filteredMrpFlowMenus = computed(() => filterMrpMenuList(mrpFlowMenus))
const filteredMrpMaterialMenus = computed(() => filterMrpMenuList(mrpMaterialMenus))
const filteredMrpMasterMenus = computed(() => filterMrpMenuList(mrpMasterMenus))
const filteredMrpReportMenus = computed(() => filterMrpMenuList(mrpReportMenus))

const goTo = (path) => {
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
