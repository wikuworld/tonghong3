import { createRouter, createWebHistory } from 'vue-router'
import AdminLayout from '../layouts/AdminLayout.vue'
import DashboardPage from '../views/admin/DashboardPage.vue'
import InventoryPage from '../views/admin/InventoryPage.vue'
import InventoryUnitMasterPage from '../views/admin/InventoryUnitMasterPage.vue'
import MrpRencanaProduksiPage from '../views/admin/mrp/MrpRencanaProduksiPage.vue'
import MrpPaletPage from '../views/admin/mrp/MrpPaletPage.vue'
import MrpMasterErpPage from '../views/admin/mrp/MrpMasterErpPage.vue'
import MrpMasterSimplePage from '../views/admin/mrp/MrpMasterSimplePage.vue'
import MrpProsesPage from '../views/admin/mrp/MrpProsesPage.vue'
import MrpProsesDetailPage from '../views/admin/mrp/MrpProsesDetailPage.vue'
import MrpLabPage from '../views/admin/mrp/MrpLabPage.vue'
import MrpMasterTreatmentPage from '../views/admin/mrp/MrpMasterTreatmentPage.vue'
import MrpMasterSupplierPage from '../views/admin/mrp/MrpMasterSupplierPage.vue'
import MrpMasterLookupPage from '../views/admin/mrp/MrpMasterLookupPage.vue'
import MrpPackingPage from '../views/admin/mrp/MrpPackingPage.vue'
import MrpPackingDetailPage from '../views/admin/mrp/MrpPackingDetailPage.vue'
import MrpGudangFgPage from '../views/admin/mrp/MrpGudangFgPage.vue'
import MrpGudangSisaPage from '../views/admin/mrp/MrpGudangSisaPage.vue'
import MrpGudangModPage from '../views/admin/mrp/MrpGudangModPage.vue'
import MrpCheckpointPage from '../views/admin/mrp/MrpCheckpointPage.vue'
import MrpStokKimiaPage from '../views/admin/mrp/MrpStokKimiaPage.vue'
import MrpStokRpPage from '../views/admin/mrp/MrpStokRpPage.vue'
import MrpStokMaterialLainPage from '../views/admin/mrp/MrpStokMaterialLainPage.vue'
import MrpUsagePage from '../views/admin/mrp/MrpUsagePage.vue'
import MrpReportPackingPage from '../views/admin/mrp/MrpReportPackingPage.vue'
import MrpReportPersiapanPage from '../views/admin/mrp/MrpReportPersiapanPage.vue'
import MrpReportSelisihWipPage from '../views/admin/mrp/MrpReportSelisihWipPage.vue'
import MrpMonitoringPage from '../views/admin/mrp/MrpMonitoringPage.vue'
import LoginPage from '../views/LoginPage.vue'
import { can, currentRoleFromToken } from '../security/permissions'

const MRP_HOME = '/admin/dashboard'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      redirect: MRP_HOME,
    },
    {
      path: '/login',
      component: LoginPage,
    },
    {
      path: '/admin',
      component: AdminLayout,
      children: [
        { path: '', redirect: MRP_HOME },
        { path: 'dashboard', component: DashboardPage, meta: { titleKey: 'menu.dashboard', module: 'dashboard' } },
        { path: 'inventory', component: InventoryPage, meta: { titleKey: 'menu.inventory', module: 'inventory' } },
        {
          path: 'inventory/units',
          component: InventoryUnitMasterPage,
          meta: { titleKey: 'menu.inventoryUnitMaster', module: 'inventory' },
        },
        {
          path: 'mrp/rencana-produksi',
          component: MrpRencanaProduksiPage,
          meta: { titleKey: 'menu.mrpRencana', module: 'mrpShopfloor' },
        },
        {
          path: 'mrp/palet',
          component: MrpPaletPage,
          meta: { titleKey: 'menu.mrpPalet', module: 'mrpShopfloor' },
        },
        {
          path: 'mrp/masters/erp',
          component: MrpMasterErpPage,
          meta: { titleKey: 'menu.mrpMasterErp', module: 'mrpShopfloor' },
        },
        {
          path: 'mrp/masters/kulit',
          component: MrpMasterSimplePage,
          meta: { titleKey: 'menu.mrpMasterKulit', module: 'mrpShopfloor', mrpMaster: 'kulit' },
        },
        {
          path: 'mrp/masters/kimia',
          component: MrpMasterSimplePage,
          meta: { titleKey: 'menu.mrpMasterKimia', module: 'mrpShopfloor', mrpMaster: 'kimia' },
        },
        {
          path: 'mrp/masters/rp',
          component: MrpMasterSimplePage,
          meta: { titleKey: 'menu.mrpMasterRp', module: 'mrpShopfloor', mrpMaster: 'rp' },
        },
        {
          path: 'mrp/masters/treatment',
          component: MrpMasterTreatmentPage,
          meta: { titleKey: 'menu.mrpMasterTreatment', module: 'mrpShopfloor' },
        },
        {
          path: 'mrp/masters/supplier',
          component: MrpMasterSupplierPage,
          meta: { titleKey: 'menu.mrpMasterSupplier', module: 'mrpShopfloor' },
        },
        {
          path: 'mrp/masters/bentuk-kulit',
          component: MrpMasterLookupPage,
          meta: {
            titleKey: 'menu.mrpMasterBentukKulit',
            module: 'mrpShopfloor',
            mrpLookup: 'bentuk-kulit',
          },
        },
        {
          path: 'mrp/masters/skala',
          component: MrpMasterLookupPage,
          meta: { titleKey: 'menu.mrpMasterSkala', module: 'mrpShopfloor', mrpLookup: 'skala' },
        },
        {
          path: 'mrp/proses',
          component: MrpProsesPage,
          meta: { titleKey: 'menu.mrpProses', module: 'mrpShopfloor' },
        },
        {
          path: 'mrp/proses/:id',
          component: MrpProsesDetailPage,
          meta: { titleKey: 'menu.mrpProses', module: 'mrpShopfloor' },
        },
        {
          path: 'mrp/lab',
          component: MrpLabPage,
          meta: { titleKey: 'menu.mrpLab', module: 'mrpShopfloor' },
        },
        {
          path: 'mrp/packing',
          component: MrpPackingPage,
          meta: { titleKey: 'menu.mrpPacking', module: 'mrpShopfloor' },
        },
        {
          path: 'mrp/packing/:id',
          component: MrpPackingDetailPage,
          meta: { titleKey: 'menu.mrpPacking', module: 'mrpShopfloor' },
        },
        {
          path: 'mrp/gudang-f',
          redirect: '/admin/mrp/gudang-fg',
        },
        {
          path: 'mrp/gudang-fg',
          component: MrpGudangFgPage,
          meta: { titleKey: 'menu.mrpGudangFg', module: 'mrpShopfloor' },
        },
        {
          path: 'mrp/gudang-sisa',
          component: MrpGudangSisaPage,
          meta: { titleKey: 'menu.mrpGudangSisa', module: 'mrpShopfloor' },
        },
        {
          path: 'mrp/gudang-mod',
          component: MrpGudangModPage,
          meta: { titleKey: 'menu.mrpGudangMod', module: 'mrpShopfloor' },
        },
        {
          path: 'mrp/checkpoint',
          component: MrpCheckpointPage,
          meta: { titleKey: 'menu.mrpCheckpoint', module: 'mrpShopfloor' },
        },
        {
          path: 'mrp/monitoring',
          component: MrpMonitoringPage,
          meta: { titleKey: 'menu.mrpMonitoring', module: 'mrpShopfloor' },
        },
        {
          path: 'mrp/stok-kimia',
          component: MrpStokKimiaPage,
          meta: { titleKey: 'menu.mrpStokKimia', module: 'mrpShopfloor' },
        },
        {
          path: 'mrp/stok-rp',
          component: MrpStokRpPage,
          meta: { titleKey: 'menu.mrpStokRp', module: 'mrpShopfloor' },
        },
        {
          path: 'mrp/stok-material-lain',
          component: MrpStokMaterialLainPage,
          meta: { titleKey: 'menu.mrpStokMaterialLain', module: 'mrpShopfloor' },
        },
        {
          path: 'mrp/usage',
          component: MrpUsagePage,
          meta: { titleKey: 'menu.mrpUsage', module: 'mrpShopfloor' },
        },
        {
          path: 'mrp/masters/material-lain',
          component: MrpMasterSimplePage,
          meta: {
            titleKey: 'menu.mrpMasterMaterialLain',
            module: 'mrpShopfloor',
            mrpMaster: 'material',
          },
        },
        {
          path: 'mrp/reports/packing',
          component: MrpReportPackingPage,
          meta: { titleKey: 'menu.mrpReportPacking', module: 'mrpShopfloor' },
        },
        {
          path: 'mrp/reports/persiapan',
          component: MrpReportPersiapanPage,
          meta: { titleKey: 'menu.mrpReportPersiapan', module: 'mrpShopfloor' },
        },
        {
          path: 'mrp/reports/selisih-wip',
          component: MrpReportSelisihWipPage,
          meta: { titleKey: 'menu.mrpReportSelisihWip', module: 'mrpShopfloor' },
        },
      ],
    },
  ],
})

router.beforeEach((to) => {
  if (to.path.startsWith('/admin')) {
    const token = typeof localStorage !== 'undefined' ? localStorage.getItem('mrp_auth_token') : null
    if (!token) {
      return { path: '/login', query: { next: to.fullPath } }
    }
    const role = currentRoleFromToken()
    if (!role || role === 'guest') {
      localStorage.removeItem('mrp_auth_token')
      return { path: '/login', query: { next: to.fullPath } }
    }
    const moduleKey = to.meta?.module
    if (moduleKey && !can(moduleKey, 'view', role)) {
      return { path: MRP_HOME }
    }
  }
  return true
})

export default router
