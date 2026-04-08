const MENU_ROLES = {
  'menu.dashboard': ['admin', 'marketing', 'ppic', 'production', 'qc', 'warehouse', 'finance', 'exim', 'sales'],
  'menu.customers': ['admin', 'marketing', 'sales', 'finance'],
  'menu.exchangeRate': ['admin', 'marketing', 'exim', 'finance'],
  'menu.po': ['admin', 'marketing', 'ppic', 'sales', 'production'],
  'menu.marketingFlow': ['admin', 'marketing', 'ppic'],
  'menu.delivery': ['admin', 'warehouse', 'marketing'],
  'menu.invoice': ['admin', 'finance'],
  'menu.reports': ['admin', 'marketing', 'ppic', 'finance', 'exim', 'sales'],
  'menu.buyerPrices': ['admin', 'marketing'],
  'menu.brandMaster': ['admin', 'marketing', 'sales'],
  'menu.customs': ['admin', 'exim'],
  'menu.masterImport': ['admin'],
  'menu.masterItems': ['admin'],
  'menu.userAccess': ['admin'],
  'menu.production': ['admin', 'production', 'ppic', 'qc'],
  'menu.qc': ['admin', 'qc', 'warehouse'],
  'menu.packing': ['admin', 'warehouse'],
}

export function roleAllowsMenu(role, labelKey) {
  if (role === 'admin') return true
  const roles = MENU_ROLES[labelKey] || []
  return roles.includes(role)
}

export const ROUTE_ROLES = {
  dashboard: MENU_ROLES['menu.dashboard'],
  customers: MENU_ROLES['menu.customers'],
  exchangeRates: MENU_ROLES['menu.exchangeRate'],
  po: MENU_ROLES['menu.po'],
  marketingFlow: MENU_ROLES['menu.marketingFlow'],
  production: MENU_ROLES['menu.production'],
  qc: MENU_ROLES['menu.qc'],
  packing: MENU_ROLES['menu.packing'],
  delivery: MENU_ROLES['menu.delivery'],
  invoice: MENU_ROLES['menu.invoice'],
  reports: MENU_ROLES['menu.reports'],
  buyerPrices: MENU_ROLES['menu.buyerPrices'],
  brandMaster: MENU_ROLES['menu.brandMaster'],
  customs: MENU_ROLES['menu.customs'],
  masterImport: MENU_ROLES['menu.masterImport'],
  masterItems: MENU_ROLES['menu.masterItems'],
  userAccess: MENU_ROLES['menu.userAccess'],
}

