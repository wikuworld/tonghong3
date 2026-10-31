import { createRouter, createWebHistory } from 'vue-router'
import AdminLayout from '../layouts/AdminLayout.vue'
import DashboardPage from '../views/admin/DashboardPage.vue'
import CustomersPage from '../views/admin/CustomersPage.vue'
import PurchaseOrderPage from '../views/admin/PurchaseOrderPage.vue'
import ProductionPage from '../views/admin/ProductionPage.vue'
import QualityControlPage from '../views/admin/QualityControlPage.vue'
import DeliveryPage from '../views/admin/DeliveryPage.vue'
import InvoicePage from '../views/admin/InvoicePage.vue'
import ReportsPage from '../views/admin/ReportsPage.vue'
import PackingPage from '../views/admin/PackingPage.vue'
import BuyerPricePage from '../views/admin/BuyerPricePage.vue'
import BrandMasterPage from '../views/admin/BrandMasterPage.vue'
import MarketingFlowPage from '../views/admin/MarketingFlowPage.vue'
import MasterItemsPage from '../views/admin/MasterItemsPage.vue'
import FluorescentColorMasterPage from '../views/admin/FluorescentColorMasterPage.vue'
import CsiColorMasterPage from '../views/admin/CsiColorMasterPage.vue'
import ColorSwatchMasterPage from '../views/admin/ColorSwatchMasterPage.vue'
import ColorWindowMasterPage from '../views/admin/ColorWindowMasterPage.vue'
import CustomsBc27Page from '../views/admin/CustomsBc27Page.vue'
import UserAccessPage from '../views/admin/UserAccessPage.vue'
// Disembunyikan sementara: halaman Mapping Customer-Brand tidak dipakai.
// import CustomerBrandMappingPage from '../views/admin/CustomerBrandMappingPage.vue'
import DataIntelligentPage from '../views/admin/DataIntelligentPage.vue'
import LoginPage from '../views/LoginPage.vue'
import { can, currentRoleFromToken } from '../security/permissions'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      redirect: '/admin/dashboard',
    },
    {
      path: '/login',
      component: LoginPage,
    },
    {
      path: '/admin',
      component: AdminLayout,
      children: [
        { path: '', redirect: '/admin/dashboard' },
        { path: 'dashboard', component: DashboardPage, meta: { titleKey: 'menu.dashboard', module: 'dashboard' } },
        { path: 'customers', component: CustomersPage, meta: { titleKey: 'menu.customers', module: 'customers' } },
        { path: 'po', component: PurchaseOrderPage, meta: { titleKey: 'menu.po', module: 'po' } },
        {
          path: 'marketing-flow',
          redirect: '/admin/marketing-flow/outstanding',
        },
        {
          path: 'marketing-flow/po-list',
          redirect: '/admin/po',
        },
        {
          path: 'marketing-flow/outstanding',
          component: MarketingFlowPage,
          meta: {
            titleKey: 'menu.marketingFlowOutstanding',
            module: 'marketingFlow',
            marketingSection: 'outstanding',
          },
        },
        {
          path: 'marketing-flow/planning',
          component: MarketingFlowPage,
          meta: {
            titleKey: 'menu.marketingFlowPlanning',
            module: 'marketingFlow',
            marketingSection: 'planning',
          },
        },
        { path: 'po-entry', redirect: '/admin/po' },
        { path: 'po-detail', redirect: '/admin/po' },
        { path: 'production', component: ProductionPage, meta: { titleKey: 'menu.production', module: 'production' } },
        { path: 'qc', component: QualityControlPage, meta: { titleKey: 'menu.qc', module: 'qc' } },
        { path: 'packing', component: PackingPage, meta: { titleKey: 'menu.packing', module: 'packing' } },
        { path: 'delivery', component: DeliveryPage, meta: { titleKey: 'menu.delivery', module: 'delivery' } },
        { path: 'customs-bc27', component: CustomsBc27Page, meta: { titleKey: 'menu.customs', module: 'customsBc27' } },
        { path: 'delivery-pull', redirect: '/admin/delivery' },
        { path: 'surat-jalan', redirect: '/admin/delivery' },
        { path: 'print-surat-jalan', redirect: '/admin/delivery' },
        { path: 'invoice', component: InvoicePage, meta: { titleKey: 'menu.invoice', module: 'invoice' } },
        { path: 'reports', component: ReportsPage, meta: { titleKey: 'menu.reports', module: 'reports' } },
        { path: 'buyer-prices', component: BuyerPricePage, meta: { titleKey: 'menu.buyerPrices', module: 'buyerPrices' } },
        { path: 'brands', component: BrandMasterPage, meta: { titleKey: 'menu.brandMaster', module: 'brandMaster' } },
        { path: 'bulk-price-update', redirect: '/admin/buyer-prices' },
        { path: 'master-items', component: MasterItemsPage, meta: { titleKey: 'menu.masterItems', module: 'masterItems' } },
        { path: 'fluorescent-colors', component: FluorescentColorMasterPage, meta: { titleKey: 'menu.fluorescentColors', module: 'fluorescentColors' } },
        { path: 'csi-colors', component: CsiColorMasterPage, meta: { titleKey: 'menu.csiColors', module: 'csiColors' } },
        { path: 'color-swatch', component: ColorSwatchMasterPage, meta: { titleKey: 'menu.colorSwatch', module: 'colorSwatch' } },
        { path: 'color-window', component: ColorWindowMasterPage, meta: { titleKey: 'menu.colorWindow', module: 'colorWindow' } },
        { path: 'user-access', component: UserAccessPage, meta: { titleKey: 'menu.userAccess', module: 'userAccess' } },
        // Disembunyikan sementara: URL lama jatuh ke redirect dashboard.
        // { path: 'customer-brand-mapping', component: CustomerBrandMappingPage, meta: { titleKey: 'menu.customerBrandMapping', module: 'customerBrandMapping' } },
        { path: 'data-intelligent', component: DataIntelligentPage, meta: { titleKey: 'menu.dataIntelligent', module: 'dataIntelligent' } },
        // Inventory dipindah ke MRP; URL lama jangan blank
        { path: 'inventory', redirect: '/admin/dashboard' },
        { path: 'ppic-dashboard', redirect: '/admin/dashboard' },
        { path: ':pathMatch(.*)*', redirect: '/admin/dashboard' },
      ],
    },
  ],
})

router.beforeEach((to) => {
  if (to.path.startsWith('/admin')) {
    const token = typeof localStorage !== 'undefined' ? localStorage.getItem('auth_token') : null
    if (!token) {
      return { path: '/login', query: { next: to.fullPath } }
    }
    const role = currentRoleFromToken()
    if (!role || role === 'guest') {
      localStorage.removeItem('auth_token')
      return { path: '/login', query: { next: to.fullPath } }
    }
    const moduleKey = to.meta?.module
    if (moduleKey && !can(moduleKey, 'view', role)) {
      return { path: '/admin/dashboard' }
    }
  }
  return true
})

export default router
