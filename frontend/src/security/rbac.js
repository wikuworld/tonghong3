import { can } from './permissions'

export const MODULE_LABEL_KEYS = {
  dashboard: 'menu.dashboard',
  customers: 'menu.customers',
  exchangeRates: 'menu.exchangeRate',
  po: 'menu.po',
  quotations: 'menu.quotations',
  marketingFlow: 'menu.marketingFlow',
  production: 'menu.production',
  qc: 'menu.qc',
  packing: 'menu.packing',
  delivery: 'menu.delivery',
  invoice: 'menu.invoice',
  subconInvoice: 'menu.subconInvoice',
  reports: 'menu.reports',
  buyerPrices: 'menu.buyerPrices',
  brandMaster: 'menu.brandMaster',
  specialPrices: 'menu.specialPrices',
  customerPrices: 'menu.customerPrices',
  bulkPriceUpdate: 'menu.bulkPriceUpdate',
  customs: 'menu.customs',
  masterImport: 'menu.masterImport',
  masterItems: 'menu.masterItems',
  fluorescentColors: 'menu.fluorescentColors',
  colorSwatch: 'menu.colorSwatch',
  customerBrandMapping: 'menu.customerBrandMapping',
  ppicDashboard: 'menu.ppicDashboard',
  outstandingMaterials: 'menu.outstandingMaterials',
  accountingMappings: 'menu.accountingMappings',
  journalEntries: 'menu.journalEntries',
  inventory: 'menu.inventory',
  userAccess: 'menu.userAccess',
}

export const ACTION_LABEL_KEYS = {
  view: 'permissions.actions.view',
  create: 'permissions.actions.create',
  update: 'permissions.actions.update',
  delete: 'permissions.actions.delete',
  export: 'permissions.actions.export',
  print: 'permissions.actions.print',
  advance: 'permissions.actions.advance',
}

export const MENU_MODULE_MAP = {
  'menu.dashboard': 'dashboard',
  'menu.customers': 'customers',
  'menu.exchangeRate': 'exchangeRates',
  'menu.po': 'po',
  'menu.quotations': 'quotations',
  'menu.marketingFlow': 'marketingFlow',
  'menu.marketingFlowPoList': 'marketingFlow',
  'menu.marketingFlowOutstanding': 'marketingFlow',
  'menu.marketingFlowPlanning': 'marketingFlow',
  'menu.delivery': 'delivery',
  'menu.invoice': 'invoice',
  'menu.subconInvoice': 'subconInvoice',
  'menu.reports': 'reports',
  'menu.buyerPrices': 'buyerPrices',
  'menu.brandMaster': 'brandMaster',
  'menu.specialPrices': 'specialPrices',
  'menu.customerPrices': 'customerPrices',
  'menu.bulkPriceUpdate': 'bulkPriceUpdate',
  'menu.customs': 'customs',
  'menu.masterImport': 'masterImport',
  'menu.masterItems': 'masterItems',
  'menu.fluorescentColors': 'fluorescentColors',
  'menu.colorSwatch': 'colorSwatch',
  'menu.userAccess': 'userAccess',
  'menu.customerBrandMapping': 'customerBrandMapping',
  'menu.production': 'production',
  'menu.qc': 'qc',
  'menu.packing': 'packing',
  'menu.ppicDashboard': 'ppicDashboard',
  'menu.outstandingMaterials': 'outstandingMaterials',
  'menu.accountingMappings': 'accountingMappings',
  'menu.journalEntries': 'journalEntries',
  'menu.inventory': 'inventory',
}

export function moduleForMenu(labelKey) {
  return MENU_MODULE_MAP[labelKey] || null
}

export function roleAllowsMenu(role, labelKey) {
  const moduleKey = moduleForMenu(labelKey)
  if (!moduleKey) return role === 'admin'
  return can(moduleKey, 'view', role)
}
