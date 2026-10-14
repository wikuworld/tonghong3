import { can } from './permissions'

export const MODULE_LABEL_KEYS = {
  dashboard: 'menu.dashboard',
  customers: 'menu.customers',
  po: 'menu.po',
  marketingFlow: 'menu.marketingFlow',
  production: 'menu.production',
  qc: 'menu.qc',
  packing: 'menu.packing',
  delivery: 'menu.delivery',
  customsBc27: 'menu.customs',
  invoice: 'menu.invoice',
  reports: 'menu.reports',
  buyerPrices: 'menu.buyerPrices',
  brandMaster: 'menu.brandMaster',
  bulkPriceUpdate: 'menu.bulkPriceUpdate',
  masterItems: 'menu.masterItems',
  fluorescentColors: 'menu.fluorescentColors',
  colorSwatch: 'menu.colorSwatch',
  csiColors: 'menu.csiColors',
  colorWindow: 'menu.colorWindow',
  customerBrandMapping: 'menu.customerBrandMapping',
  dataIntelligent: 'menu.dataIntelligent',
  inventory: 'menu.inventory',
  userAccess: 'menu.userAccess',
  mrpShopfloor: 'menu.mrpRencana',
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
  'menu.po': 'po',
  'menu.marketingFlow': 'marketingFlow',
  'menu.marketingFlowPoList': 'marketingFlow',
  'menu.marketingFlowOutstanding': 'marketingFlow',
  'menu.marketingFlowPlanning': 'marketingFlow',
  'menu.delivery': 'delivery',
  'menu.customs': 'customsBc27',
  'menu.invoice': 'invoice',
  'menu.reports': 'reports',
  'menu.buyerPrices': 'buyerPrices',
  'menu.brandMaster': 'brandMaster',
  'menu.bulkPriceUpdate': 'bulkPriceUpdate',
  'menu.masterItems': 'masterItems',
  'menu.fluorescentColors': 'fluorescentColors',
  'menu.colorSwatch': 'colorSwatch',
  'menu.csiColors': 'csiColors',
  'menu.colorWindow': 'colorWindow',
  'menu.userAccess': 'userAccess',
  'menu.customerBrandMapping': 'customerBrandMapping',
  'menu.dataIntelligent': 'dataIntelligent',
  'menu.production': 'production',
  'menu.qc': 'qc',
  'menu.packing': 'packing',
  'menu.inventory': 'inventory',
  'menu.mrpRencana': 'mrpShopfloor',
  'menu.mrpPalet': 'mrpShopfloor',
  'menu.mrpMasterErp': 'mrpShopfloor',
  'menu.mrpMasterKulit': 'mrpShopfloor',
  'menu.mrpMasterKimia': 'mrpShopfloor',
  'menu.mrpMasterRp': 'mrpShopfloor',
  'menu.mrpMasterTreatment': 'mrpShopfloor',
  'menu.mrpProses': 'mrpShopfloor',
  'menu.mrpLab': 'mrpShopfloor',
  'menu.mrpPacking': 'mrpShopfloor',
  'menu.mrpGudangFg': 'mrpShopfloor',
  'menu.mrpCheckpoint': 'mrpShopfloor',
  'menu.mrpMonitoring': 'mrpShopfloor',
  'menu.mrpStokKimia': 'mrpShopfloor',
  'menu.mrpStokRp': 'mrpShopfloor',
  'menu.mrpStokMaterialLain': 'mrpShopfloor',
  'menu.mrpUsage': 'mrpShopfloor',
  'menu.mrpMasterMaterialLain': 'mrpShopfloor',
  'menu.mrpReportPacking': 'mrpShopfloor',
  'menu.mrpReportPersiapan': 'mrpShopfloor',
}

export function moduleForMenu(labelKey) {
  return MENU_MODULE_MAP[labelKey] || null
}

export function roleAllowsMenu(role, labelKey) {
  const moduleKey = moduleForMenu(labelKey)
  if (!moduleKey) return role === 'admin'
  return can(moduleKey, 'view', role)
}
