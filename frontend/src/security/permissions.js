export const ACTION_MATRIX = {
  customers: {
    view: ['admin', 'marketing', 'sales', 'finance'],
    create: ['admin', 'marketing', 'sales'],
    update: ['admin', 'marketing', 'sales'],
    delete: ['admin'],
  },
  po: {
    view: ['admin', 'marketing', 'ppic', 'sales', 'production', 'finance'],
    create: ['admin', 'marketing', 'ppic', 'sales'],
    update: ['admin', 'marketing', 'ppic', 'finance'],
    delete: ['admin'],
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
  reports: {
    view: ['admin', 'marketing', 'ppic', 'finance', 'exim', 'sales'],
    export: ['admin', 'marketing', 'ppic', 'finance', 'exim', 'sales'],
  },
  masterImport: {
    view: ['admin'],
    create: ['admin'],
  },
  userAccess: {
    view: ['admin'],
    create: ['admin'],
    update: ['admin'],
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
}

let runtimeMatrix = null

export function setRuntimePermissionMatrix(matrix) {
  runtimeMatrix = matrix && typeof matrix === 'object' ? matrix : null
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

