import { ref } from 'vue'

const ALL_ROLES = ['marketing', 'ppic', 'production', 'qc', 'warehouse', 'finance', 'exim', 'sales']

export const ACTION_MATRIX = {
  dashboard: {
    view: ['admin', ...ALL_ROLES],
  },
  customers: {
    view: ['admin', 'marketing', 'sales', 'finance'],
    create: ['admin', 'marketing', 'sales'],
    update: ['admin', 'marketing', 'sales'],
    delete: ['admin'],
  },
  po: {
    view: ['admin', 'marketing', 'ppic', 'sales', 'production', 'finance'],
    create: ['admin', 'marketing', 'sales'],
    update: ['admin', 'marketing', 'sales', 'ppic', 'finance'],
    delete: ['admin'],
    advance: ['admin', 'marketing', 'ppic'],
  },
  quotations: {
    view: ['admin', 'marketing', 'sales', 'finance'],
    create: ['admin', 'marketing', 'sales'],
    update: ['admin', 'marketing', 'sales'],
    delete: ['admin', 'marketing'],
  },
  marketingFlow: {
    view: ['admin', 'marketing', 'ppic'],
    update: ['admin', 'marketing', 'ppic'],
    advance: ['admin', 'marketing', 'ppic'],
  },
  production: {
    view: ['admin', 'production', 'ppic', 'qc'],
    create: ['admin', 'production', 'ppic'],
    update: ['admin', 'production'],
  },
  qc: {
    view: ['admin', 'qc', 'warehouse', 'production'],
    create: ['admin', 'qc'],
    update: ['admin', 'qc'],
  },
  packing: {
    view: ['admin', 'warehouse'],
    create: ['admin', 'warehouse'],
    update: ['admin', 'warehouse'],
    print: ['admin', 'warehouse'],
  },
  delivery: {
    view: ['admin', 'warehouse', 'marketing'],
    create: ['admin', 'warehouse'],
    update: ['admin', 'warehouse'],
    print: ['admin', 'warehouse', 'marketing'],
  },
  invoice: {
    view: ['admin', 'finance'],
    create: ['admin', 'finance'],
    update: ['admin', 'finance'],
  },
  subconInvoice: {
    view: ['admin', 'finance'],
    create: ['admin', 'finance'],
    update: ['admin', 'finance'],
    delete: ['admin'],
  },
  reports: {
    view: ['admin', 'marketing', 'ppic', 'finance', 'exim', 'sales'],
    export: ['admin', 'marketing', 'ppic', 'finance', 'exim', 'sales'],
  },
  buyerPrices: {
    view: ['admin', 'marketing'],
    create: ['admin', 'marketing'],
    update: ['admin', 'marketing'],
    delete: ['admin', 'marketing'],
  },
  brandMaster: {
    view: ['admin', 'marketing', 'sales'],
    create: ['admin', 'marketing'],
    update: ['admin', 'marketing'],
    delete: ['admin'],
  },
  specialPrices: {
    view: ['admin', 'marketing', 'sales'],
    create: ['admin', 'marketing'],
    update: ['admin', 'marketing'],
    delete: ['admin'],
  },
  customerPrices: {
    view: ['admin', 'marketing', 'sales'],
    create: ['admin', 'marketing'],
    update: ['admin', 'marketing'],
    delete: ['admin'],
  },
  bulkPriceUpdate: {
    view: ['admin', 'marketing'],
    update: ['admin', 'marketing'],
  },
  masterItems: {
    view: ['admin'],
    create: ['admin'],
    update: ['admin'],
    delete: ['admin'],
  },
  fluorescentColors: {
    view: ['admin', 'marketing', 'sales'],
    create: ['admin', 'marketing'],
    update: ['admin', 'marketing'],
    delete: ['admin'],
  },
  colorSwatch: {
    view: ['admin', 'marketing', 'sales'],
    create: ['admin', 'marketing'],
    update: ['admin', 'marketing'],
    delete: ['admin'],
  },
  csiColors: {
    view: ['admin', 'marketing', 'sales'],
    create: ['admin', 'marketing'],
    update: ['admin', 'marketing'],
    delete: ['admin'],
  },
  customerBrandMapping: {
    view: ['admin', 'marketing', 'sales'],
    create: ['admin', 'marketing'],
    update: ['admin', 'marketing', 'sales'],
    delete: ['admin', 'marketing'],
  },
  ppicDashboard: {
    view: ['admin', 'ppic'],
    update: ['admin', 'ppic'],
  },
  outstandingMaterials: {
    view: ['admin', 'marketing', 'ppic'],
    update: ['admin', 'marketing', 'ppic'],
  },
  accountingMappings: {
    view: ['admin', 'finance'],
    create: ['admin', 'finance'],
    update: ['admin', 'finance'],
    delete: ['admin', 'finance'],
  },
  journalEntries: {
    view: ['admin', 'finance'],
    create: ['admin', 'finance'],
  },
  inventory: {
    view: ['admin', 'warehouse'],
    create: ['admin', 'warehouse'],
    update: ['admin', 'warehouse'],
  },
  userAccess: {
    view: ['admin'],
    create: ['admin'],
    update: ['admin'],
  },
  mrpShopfloor: {
    view: ['admin', 'production', 'ppic', 'warehouse'],
    create: ['admin', 'production', 'ppic'],
    update: ['admin', 'production', 'ppic'],
  },
}

let runtimeMatrix = null
export const permissionMatrixVersion = ref(0)

export function setRuntimePermissionMatrix(matrix) {
  runtimeMatrix = matrix && typeof matrix === 'object' ? matrix : null
  permissionMatrixVersion.value += 1
}

export function getRuntimePermissionMatrix() {
  return runtimeMatrix || ACTION_MATRIX
}

export function currentRoleFromToken() {
  if (typeof localStorage === 'undefined') return 'guest'
  const token = localStorage.getItem('auth_token')
  if (!token) return 'guest'
  try {
    const base64Url = token.split('.')[1] || ''
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/')
    const padded = base64 + '='.repeat((4 - (base64.length % 4)) % 4)
    const payload = JSON.parse(atob(padded))
    return payload?.role || 'guest'
  } catch {
    return 'guest'
  }
}

export function canWrite(moduleKey, role = currentRoleFromToken()) {
  return can(moduleKey, 'update', role) || can(moduleKey, 'create', role)
}

export function can(moduleKey, action, role = currentRoleFromToken()) {
  if (role === 'admin') return true
  const actions = getRuntimePermissionMatrix()[moduleKey] || {}
  const roles = actions[action] || []
  return roles.includes(role)
}

export function rolesWithView(moduleKey) {
  const actions = getRuntimePermissionMatrix()[moduleKey] || ACTION_MATRIX[moduleKey] || {}
  return actions.view || []
}
