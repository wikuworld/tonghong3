import { createRouter, createWebHistory } from 'vue-router'
import AdminLayout from '../layouts/AdminLayout.vue'
import DashboardPage from '../views/admin/DashboardPage.vue'
import CustomersPage from '../views/admin/CustomersPage.vue'
import QuotationPage from '../views/admin/QuotationPage.vue'
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
import FluorescentColorMasterPage from '../views/admin/FluorescentColorMasterPage.vue'
import ColorSwatchMasterPage from '../views/admin/ColorSwatchMasterPage.vue'
import UserAccessPage from '../views/admin/UserAccessPage.vue'
import CustomerBrandMappingPage from '../views/admin/CustomerBrandMappingPage.vue'
import SubconInvoicePage from '../views/admin/SubconInvoicePage.vue'
import PpicsDashboardPage from '../views/admin/PpicsDashboardPage.vue'
import OutstandingMaterialsPage from '../views/admin/OutstandingMaterialsPage.vue'
import AccountingMappingsPage from '../views/admin/AccountingMappingsPage.vue'
import JournalEntriesPage from '../views/admin/JournalEntriesPage.vue'
import InventoryPage from '../views/admin/InventoryPage.vue'
import MrpRencanaProduksiPage from '../views/admin/mrp/MrpRencanaProduksiPage.vue'
import MrpPaletPage from '../views/admin/mrp/MrpPaletPage.vue'
import MrpMasterErpPage from '../views/admin/mrp/MrpMasterErpPage.vue'
import MrpMasterSimplePage from '../views/admin/mrp/MrpMasterSimplePage.vue'
import MrpProsesPage from '../views/admin/mrp/MrpProsesPage.vue'
import MrpProsesDetailPage from '../views/admin/mrp/MrpProsesDetailPage.vue'
import MrpLabPage from '../views/admin/mrp/MrpLabPage.vue'
import MrpMasterTreatmentPage from '../views/admin/mrp/MrpMasterTreatmentPage.vue'
import MrpPackingPage from '../views/admin/mrp/MrpPackingPage.vue'
import MrpPackingDetailPage from '../views/admin/mrp/MrpPackingDetailPage.vue'
import MrpGudangFgPage from '../views/admin/mrp/MrpGudangFgPage.vue'
import MrpStokKimiaPage from '../views/admin/mrp/MrpStokKimiaPage.vue'
import MrpStokRpPage from '../views/admin/mrp/MrpStokRpPage.vue'
import MrpStokMaterialLainPage from '../views/admin/mrp/MrpStokMaterialLainPage.vue'
import MrpUsagePage from '../views/admin/mrp/MrpUsagePage.vue'
import MrpReportPackingPage from '../views/admin/mrp/MrpReportPackingPage.vue'
import MrpReportPersiapanPage from '../views/admin/mrp/MrpReportPersiapanPage.vue'
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
        {
          path: 'quotations',
          component: QuotationPage,
          meta: { titleKey: 'menu.quotations', module: 'quotations' },
        },
        {
          path: 'exchange-rates',
          component: ExchangeRatePage,
          meta: { titleKey: 'menu.exchangeRate', module: 'exchangeRates' },
        },
        { path: 'po', component: PurchaseOrderPage, meta: { titleKey: 'menu.po', module: 'po' } },
        {
          path: 'marketing-flow',
          redirect: '/admin/marketing-flow/po-list',
        },
        {
          path: 'marketing-flow/po-list',
          component: MarketingFlowPage,
          meta: {
            titleKey: 'menu.marketingFlowPoList',
            module: 'marketingFlow',
            marketingSection: 'flow',
          },
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
        { path: 'delivery-pull', redirect: '/admin/delivery' },
        { path: 'surat-jalan', redirect: '/admin/delivery' },
        { path: 'print-surat-jalan', redirect: '/admin/delivery' },
        { path: 'invoice', component: InvoicePage, meta: { titleKey: 'menu.invoice', module: 'invoice' } },
        { path: 'reports', component: ReportsPage, meta: { titleKey: 'menu.reports', module: 'reports' } },
        { path: 'buyer-prices', component: BuyerPricePage, meta: { titleKey: 'menu.buyerPrices', module: 'buyerPrices' } },
        { path: 'brands', component: BrandMasterPage, meta: { titleKey: 'menu.brandMaster', module: 'brandMaster' } },
        { path: 'special-prices', component: SpecialPricesPage, meta: { titleKey: 'menu.specialPrices', module: 'specialPrices' } },
        { path: 'customer-prices', component: CustomerPricesPage, meta: { titleKey: 'menu.customerPrices', module: 'customerPrices' } },
        { path: 'bulk-price-update', component: BulkPriceUpdatePage, meta: { titleKey: 'menu.bulkPriceUpdate', module: 'bulkPriceUpdate' } },
        { path: 'customs', component: CustomsPage, meta: { titleKey: 'menu.customs', module: 'customs' } },
        { path: 'master-import', component: MasterImportPage, meta: { titleKey: 'menu.masterImport', module: 'masterImport' } },
        { path: 'master-items', component: MasterItemsPage, meta: { titleKey: 'menu.masterItems', module: 'masterItems' } },
        { path: 'fluorescent-colors', component: FluorescentColorMasterPage, meta: { titleKey: 'menu.fluorescentColors', module: 'fluorescentColors' } },
        { path: 'color-swatch', component: ColorSwatchMasterPage, meta: { titleKey: 'menu.colorSwatch', module: 'colorSwatch' } },
        { path: 'user-access', component: UserAccessPage, meta: { titleKey: 'menu.userAccess', module: 'userAccess' } },
        { path: 'customer-brand-mapping', component: CustomerBrandMappingPage, meta: { titleKey: 'menu.customerBrandMapping', module: 'customerBrandMapping' } },
        { path: 'subcon-invoices', component: SubconInvoicePage, meta: { titleKey: 'menu.subconInvoice', module: 'subconInvoice' } },
        { path: 'ppic-dashboard', component: PpicsDashboardPage, meta: { titleKey: 'menu.ppicDashboard', module: 'ppicDashboard' } },
        { path: 'outstanding-materials', component: OutstandingMaterialsPage, meta: { titleKey: 'menu.outstandingMaterials', module: 'outstandingMaterials' } },
        { path: 'accounting-mappings', component: AccountingMappingsPage, meta: { titleKey: 'menu.accountingMappings', module: 'accountingMappings' } },
        { path: 'journal-entries', component: JournalEntriesPage, meta: { titleKey: 'menu.journalEntries', module: 'journalEntries' } },
        { path: 'inventory', component: InventoryPage, meta: { titleKey: 'menu.inventory', module: 'inventory' } },
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
          path: 'mrp/gudang-fg',
          component: MrpGudangFgPage,
          meta: { titleKey: 'menu.mrpGudangFg', module: 'mrpShopfloor' },
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
