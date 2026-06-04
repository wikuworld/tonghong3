/** Util daftar & filter PO (pagination, enrich baris, deep link). */

export function createPoOrderDateShortcuts(t) {
  return [
    {
      text: t('pages.marketingFlow.shortcutLast7Days'),
      value: () => {
        const e = new Date()
        const s = new Date()
        s.setDate(s.getDate() - 6)
        return [s, e]
      },
    },
    {
      text: t('pages.marketingFlow.shortcutLast30Days'),
      value: () => {
        const e = new Date()
        const s = new Date()
        s.setDate(s.getDate() - 29)
        return [s, e]
      },
    },
    {
      text: t('pages.marketingFlow.shortcutThisMonth'),
      value: () => {
        const e = new Date()
        return [new Date(e.getFullYear(), e.getMonth(), 1), e]
      },
    },
    {
      text: t('pages.marketingFlow.shortcutThisYear'),
      value: () => {
        const e = new Date()
        return [new Date(e.getFullYear(), 0, 1), e]
      },
    },
  ]
}

export function buildPoPageQuery({
  keyword,
  filterCustomerId,
  filterBuyer,
  filterStatus,
  filterOrderDateRange,
  page,
  pageSize,
}) {
  const query = {
    q: keyword || undefined,
    customer_id: filterCustomerId || undefined,
    buyer: filterBuyer || undefined,
    status: filterStatus || undefined,
    limit: pageSize,
    offset: (page - 1) * pageSize,
  }
  if (
    Array.isArray(filterOrderDateRange) &&
    filterOrderDateRange.length === 2 &&
    filterOrderDateRange[0] &&
    filterOrderDateRange[1]
  ) {
    query.order_date_from = filterOrderDateRange[0]
    query.order_date_to = filterOrderDateRange[1]
  }
  return query
}

export function lookupCustomerDisplayName(customers, id, emptyValue) {
  const c = customers.find((x) => x.id === id)
  return c ? `${c.code || ''} ${c.name || ''}`.trim() : emptyValue
}

export function customerOptionLabel(c, t) {
  const base = [c.code, c.name].filter(Boolean).join(' — ')
  if (!base) return String(c.id)
  return c.city ? `${base} ${t('common.dotSeparator')} ${c.city}` : base
}

export function enrichPoRows(headers, { customers, emptyValue }) {
  return headers.map((h) => ({
    ...h,
    customerName: h.customer_name_snapshot || lookupCustomerDisplayName(customers, h.customer_id, emptyValue),
    material_hint: emptyValue,
    etd: h.etd ? String(h.etd).slice(0, 10) : '',
    order_date_fmt: h.order_date ? String(h.order_date).slice(0, 10) : '',
  }))
}

export function parsePoRoutePoId(route) {
  const poIdRaw = route?.query?.po_id ?? route?.query?.highlight
  const poId = Number(poIdRaw)
  if (Number.isNaN(poId) || poId <= 0) return null
  return poId
}

export async function resolvePoDeepLinkRow({ poId, rows, getPo }) {
  let target = rows.find((r) => Number(r.id) === poId)
  if (!target) {
    try {
      target = await getPo(poId)
    } catch {
      return null
    }
  }
  return target
}

export function mergeExtraBuyerCodes(baseBuyers, priceLists) {
  const extra = [...new Set((priceLists || []).map((x) => x.buyer_code).filter(Boolean))]
  return [...new Set([...(baseBuyers || []), ...extra])]
}
