/**
 * Build query params for server-side list pagination + sorting.
 * @param {{ page?: number, pageSize?: number, sortBy?: string|null, sortDir?: 'asc'|'desc'|string|null, extra?: Record<string, any> }} opts
 */
export function buildPageParams({
  page = 1,
  pageSize = 20,
  sortBy = null,
  sortDir = 'desc',
  extra = {},
} = {}) {
  const params = {
    page: Math.max(1, Number(page) || 1),
    page_size: Math.min(200, Math.max(1, Number(pageSize) || 20)),
    ...extra,
  }
  const key = sortBy != null && String(sortBy).trim() ? String(sortBy).trim() : ''
  if (key) {
    params.sort_by = key
    params.sort_dir = String(sortDir || 'desc').toLowerCase() === 'asc' ? 'asc' : 'desc'
  }
  return params
}

/** Normalize list API payload to { items, total, page, page_size }. */
export function normalizePageResult(data, fallback = {}) {
  if (Array.isArray(data)) {
    return {
      items: data,
      total: data.length,
      page: fallback.page || 1,
      page_size: fallback.pageSize || data.length || 20,
    }
  }
  const items = data?.items || data?.rows || data?.data || []
  return {
    items: Array.isArray(items) ? items : [],
    total: Number(data?.total ?? items.length ?? 0),
    page: Number(data?.page ?? fallback.page ?? 1),
    page_size: Number(data?.page_size ?? data?.limit ?? fallback.pageSize ?? 20),
  }
}

/** Map Element Plus sort-change payload → { sortBy, sortDir }. */
export function fromElSortChange({ prop, order } = {}) {
  if (!prop || !order) return { sortBy: null, sortDir: 'desc' }
  return {
    sortBy: prop,
    sortDir: order === 'ascending' ? 'asc' : 'desc',
  }
}
