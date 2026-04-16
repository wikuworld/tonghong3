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
import ExchangeRatePage from '../views/admin/ExchangeRatePage.vue'
import PackingPage from '../views/admin/PackingPage.vue'
import CustomsPage from '../views/admin/CustomsPage.vue'
import BuyerPricePage from '../views/admin/BuyerPricePage.vue'
import BrandMasterPage from '../views/admin/BrandMasterPage.vue'
import SpecialPricesPage from '../views/admin/SpecialPricesPage.vue'
import CustomerPricesPage from '../views/admin/CustomerPricesPage.vue'
import BulkPriceUpdatePage from '../views/admin/BulkPriceUpdatePage.vue'
import MarketingFlowPage from '../views/admin/MarketingFlowPage.vue'
import MasterImportPage from '../views/admin/MasterImportPage.vue'
import MasterItemsPage from '../views/admin/MasterItemsPage.vue'
import UserAccessPage from '../views/admin/UserAccessPage.vue'
import CustomerBrandMappingPage from '../views/admin/CustomerBrandMappingPage.vue'
import SubconInvoicePage from '../views/admin/SubconInvoicePage.vue'
import PpicsDashboardPage from '../views/admin/PpicsDashboardPage.vue'
import OutstandingMaterialsPage from '../views/admin/OutstandingMaterialsPage.vue'
import AccountingMappingsPage from '../views/admin/AccountingMappingsPage.vue'
import JournalEntriesPage from '../views/admin/JournalEntriesPage.vue'
import InventoryPage from '../views/admin/InventoryPage.vue'
import LoginPage from '../views/LoginPage.vue'
import { ROUTE_ROLES } from '../security/rbac'

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
        { path: 'dashboard', component: DashboardPage, meta: { titleKey: 'menu.dashboard', roles: ROUTE_ROLES.dashboard } },
        { path: 'customers', component: CustomersPage, meta: { titleKey: 'menu.customers', roles: ROUTE_ROLES.customers } },
        {
          path: 'exchange-rates',
          component: ExchangeRatePage,
          meta: { titleKey: 'menu.exchangeRate', roles: ROUTE_ROLES.exchangeRates },
        },
        { path: 'po', component: PurchaseOrderPage, meta: { titleKey: 'menu.po', roles: ROUTE_ROLES.po } },
        {
          path: 'marketing-flow',
          component: MarketingFlowPage,
          meta: { titleKey: 'menu.marketingFlow', roles: ROUTE_ROLES.marketingFlow },
        },
        { path: 'po-entry', redirect: '/admin/po' },
        { path: 'po-detail', redirect: '/admin/po' },
        { path: 'production', component: ProductionPage, meta: { titleKey: 'menu.production', roles: ROUTE_ROLES.production } },
        { path: 'qc', component: QualityControlPage, meta: { titleKey: 'menu.qc', roles: ROUTE_ROLES.qc } },
        { path: 'packing', component: PackingPage, meta: { titleKey: 'menu.packing', roles: ROUTE_ROLES.packing } },
        { path: 'delivery', component: DeliveryPage, meta: { titleKey: 'menu.delivery', roles: ROUTE_ROLES.delivery } },
        { path: 'delivery-pull', redirect: '/admin/delivery' },
        { path: 'surat-jalan', redirect: '/admin/delivery' },
        { path: 'print-surat-jalan', redirect: '/admin/delivery' },
        { path: 'invoice', component: InvoicePage, meta: { titleKey: 'menu.invoice', roles: ROUTE_ROLES.invoice } },
        { path: 'reports', component: ReportsPage, meta: { titleKey: 'menu.reports', roles: ROUTE_ROLES.reports } },
        { path: 'buyer-prices', component: BuyerPricePage, meta: { titleKey: 'menu.buyerPrices', roles: ROUTE_ROLES.buyerPrices } },
        { path: 'brands', component: BrandMasterPage, meta: { titleKey: 'menu.brandMaster', roles: ROUTE_ROLES.brandMaster } },
        { path: 'special-prices', component: SpecialPricesPage, meta: { titleKey: 'menu.specialPrices', roles: ROUTE_ROLES.specialPrices } },
        { path: 'customer-prices', component: CustomerPricesPage, meta: { titleKey: 'menu.customerPrices', roles: ROUTE_ROLES.customerPrices } },
        { path: 'bulk-price-update', component: BulkPriceUpdatePage, meta: { titleKey: 'menu.bulkPriceUpdate', roles: ROUTE_ROLES.bulkPriceUpdate } },
        { path: 'customs', component: CustomsPage, meta: { titleKey: 'menu.customs', roles: ROUTE_ROLES.customs } },
        { path: 'master-import', component: MasterImportPage, meta: { titleKey: 'menu.masterImport', roles: ROUTE_ROLES.masterImport } },
        { path: 'master-items', component: MasterItemsPage, meta: { titleKey: 'menu.masterItems', roles: ROUTE_ROLES.masterItems } },
        { path: 'user-access', component: UserAccessPage, meta: { titleKey: 'menu.userAccess', roles: ROUTE_ROLES.userAccess } },
        { path: 'customer-brand-mapping', component: CustomerBrandMappingPage, meta: { titleKey: 'menu.customerBrandMapping', roles: ROUTE_ROLES.customerBrandMapping } },
        { path: 'subcon-invoices', component: SubconInvoicePage, meta: { titleKey: 'menu.subconInvoice', roles: ROUTE_ROLES.subconInvoice } },
        { path: 'ppic-dashboard', component: PpicsDashboardPage, meta: { titleKey: 'menu.ppicDashboard', roles: ROUTE_ROLES.ppicDashboard } },
        { path: 'outstanding-materials', component: OutstandingMaterialsPage, meta: { titleKey: 'menu.outstandingMaterials', roles: ROUTE_ROLES.outstandingMaterials } },
        { path: 'accounting-mappings', component: AccountingMappingsPage, meta: { titleKey: 'menu.accountingMappings', roles: ROUTE_ROLES.accountingMappings } },
        { path: 'journal-entries', component: JournalEntriesPage, meta: { titleKey: 'menu.journalEntries', roles: ROUTE_ROLES.accountingMappings } },
        { path: 'inventory', component: InventoryPage, meta: { titleKey: 'menu.inventory', roles: ROUTE_ROLES.inventory } },
      ],
    },
  ],
})

function readRoleFromToken(token) {
  try {
    const base64Url = token.split('.')[1] || ''
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/')
    const padded = base64 + '='.repeat((4 - (base64.length % 4)) % 4)
    const payload = JSON.parse(atob(padded))
    return payload?.role || 'guest'
  } catch {
    return null
  }
}

router.beforeEach((to) => {
  if (to.path.startsWith('/admin')) {
    const token = typeof localStorage !== 'undefined' ? localStorage.getItem('auth_token') : null
    if (!token) {
      return { path: '/login', query: { next: to.fullPath } }
    }
    const role = readRoleFromToken(token)
    if (!role) {
      localStorage.removeItem('auth_token')
      return { path: '/login', query: { next: to.fullPath } }
    }
    const required = to.meta?.roles
    if (Array.isArray(required) && !required.includes(role) && role !== 'admin') {
      return { path: '/admin/dashboard' }
    }
  }
  return true
})

export default router
