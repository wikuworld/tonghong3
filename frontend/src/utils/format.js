export function formatCurrency(value, currency = 'IDR') {
  if (value == null || value === '') return '-'
  const num = Number(value)
  if (isNaN(num)) return '-'
  if (currency === 'USD') {
    return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(num)
  }
  return new Intl.NumberFormat('id-ID', { style: 'currency', currency: 'IDR', minimumFractionDigits: 0 }).format(num)
}

export function formatNumber(value, decimals = 2) {
  if (value == null || value === '') return '-'
  const num = Number(value)
  if (isNaN(num)) return '-'
  return new Intl.NumberFormat('id-ID', { minimumFractionDigits: decimals, maximumFractionDigits: decimals }).format(num)
}

export function formatDate(value) {
  if (!value) return '-'
  const d = new Date(value)
  if (isNaN(d.getTime())) return '-'
  return d.toLocaleDateString('id-ID', { day: '2-digit', month: 'short', year: 'numeric' })
}

export function formatDateFull(value) {
  if (!value) return '-'
  const d = new Date(value)
  if (isNaN(d.getTime())) return '-'
  return d.toLocaleDateString('id-ID', { day: '2-digit', month: 'long', year: 'numeric' })
}

export function statusType(status) {
  const map = {
    draft: 'info',
    pending: 'warning',
    confirmed: 'success',
    in_progress: 'warning',
    completed: 'success',
    cancelled: 'danger',
    paid: 'success',
    sent: 'primary',
    delivered: 'success',
    production: 'warning',
    sample: 'info',
    claim: 'danger',
    return: 'warning',
    subkon: 'info',
    retur: 'warning',
  }
  return map[status?.toLowerCase()] || 'info'
}

export function statusLabel(status, labels = {}) {
  if (labels[status]) return labels[status]
  return status ? status.charAt(0).toUpperCase() + status.slice(1).replace(/_/g, ' ') : '-'
}
