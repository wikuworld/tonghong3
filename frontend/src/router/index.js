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
import MarketingFlowPage from '../views/admin/MarketingFlowPage.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      redirect: '/admin/dashboard',
    },
    {
      path: '/admin',
      component: AdminLayout,
      children: [
        { path: '', redirect: '/admin/dashboard' },
        { path: 'dashboard', component: DashboardPage, meta: { titleKey: 'menu.dashboard' } },
        { path: 'customers', component: CustomersPage, meta: { titleKey: 'menu.customers' } },
        {
          path: 'exchange-rates',
          component: ExchangeRatePage,
          meta: { titleKey: 'menu.exchangeRate' },
        },
        { path: 'po', component: PurchaseOrderPage, meta: { titleKey: 'menu.po' } },
        {
          path: 'marketing-flow',
          component: MarketingFlowPage,
          meta: { titleKey: 'menu.marketingFlow' },
        },
        { path: 'po-entry', redirect: '/admin/po' },
        { path: 'po-detail', redirect: '/admin/po' },
        { path: 'production', component: ProductionPage, meta: { titleKey: 'menu.production' } },
        { path: 'qc', component: QualityControlPage, meta: { titleKey: 'menu.qc' } },
        { path: 'packing', component: PackingPage, meta: { titleKey: 'menu.packing' } },
        { path: 'delivery', component: DeliveryPage, meta: { titleKey: 'menu.delivery' } },
        { path: 'delivery-pull', redirect: '/admin/delivery' },
        { path: 'surat-jalan', redirect: '/admin/delivery' },
        { path: 'print-surat-jalan', redirect: '/admin/delivery' },
        { path: 'invoice', component: InvoicePage, meta: { titleKey: 'menu.invoice' } },
        { path: 'reports', component: ReportsPage, meta: { titleKey: 'menu.reports' } },
        { path: 'buyer-prices', component: BuyerPricePage, meta: { titleKey: 'menu.buyerPrices' } },
        { path: 'customs', component: CustomsPage, meta: { titleKey: 'menu.customs' } },
      ],
    },
  ],
})

export default router
