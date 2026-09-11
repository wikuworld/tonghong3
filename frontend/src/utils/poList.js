/** Util daftar & filter PO (pagination, enrich baris, deep link). */

/** Jenis order header. Legacy `suede` = production (material PU/Suede ada di item). */
export function normalizePoOrderCategory(raw) {
  const cat = String(raw || '').trim().toLowerCase()
  if (!cat || cat === 'suede') return 'production'
  return cat
}

export function poOrderCategoryLabel(cat, t, te) {
  const norm = normalizePoOrderCategory(cat)
  if (norm && typeof te === 'function' && te(`status.${norm}`)) return t(`status.${norm}`)
  if (norm && t) return t(`status.${norm}`)
  return cat || '—'
}

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
  filterPoCategory,
  filterStatus,
  filterOrderDateRange,
  page,
  pageSize,
}) {
  const query = {
    q: keyword || undefined,
    customer_id: Array.isArray(filterCustomerId)
      ? (filterCustomerId.length ? filterCustomerId : undefined)
      : filterCustomerId || undefined,
    buyer: filterBuyer || undefined,
    po_category: filterPoCategory || undefined,
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

export function lookupBrandDisplayName(brands, id, emptyValue) {
  const b = brands.find((x) => x.id === id)
  if (!b) return emptyValue
  return (b.name || b.code || '').trim() || emptyValue
}

export function formatMaterialHint(row, emptyValue, noMaterialLabel) {
  const hint = (row.material_hint || '').trim()
  if (hint) return hint
  const lines = Number(row.detail_line_count ?? 0)
  if (lines > 0 && noMaterialLabel) return noMaterialLabel
  return emptyValue
}

export function formatEtdDisplay(row, emptyValue) {
  const hint = (row.etd_display || '').trim()
  if (hint) return hint
  if (row.etd) return String(row.etd).slice(0, 10)
  return emptyValue
}

export function enrichPoRows(headers, { customers, brands, emptyValue, noMaterialLabel }) {
  return headers.map((h) => ({
    ...h,
    customerName: h.customer_name_snapshot || lookupCustomerDisplayName(customers, h.customer_id, emptyValue),
    brand_name_snapshot:
      (h.brand_name_snapshot || '').trim() || lookupBrandDisplayName(brands, h.brand_id, emptyValue),
    material_hint: formatMaterialHint(h, emptyValue, noMaterialLabel),
    detail_line_count: Number(h.detail_line_count ?? 0),
    etd: formatEtdDisplay(h, emptyValue),
    order_date_fmt: h.order_date ? String(h.order_date).slice(0, 10) : '',
  }))
}

/** Gabungkan material hint dari endpoint batch bila field list belum terisi. */
export function mergePoMaterialHints(items, hintItems) {
  if (!Array.isArray(items) || !Array.isArray(hintItems) || !hintItems.length) return items
  const map = Object.fromEntries(
    hintItems.map((x) => [Number(x.po_id), x]),
  )
  return items.map((h) => {
    const extra = map[Number(h.id)]
    if (!extra) return h
    return {
      ...h,
      detail_line_count: h.detail_line_count ?? extra.detail_line_count ?? 0,
      material_hint: (h.material_hint || '').trim() || extra.material_hint || null,
      etd_display: (h.etd_display || '').trim() || extra.etd_display || null,
    }
  })
}

function csvEscape(value) {
  const s = String(value ?? '')
  if (/[",\n\r]/.test(s)) return `"${s.replace(/"/g, '""')}"`
  return s
}

/** Unduh CSV daftar PO (kolom inti operasional). */
export function downloadPoListCsv(rows, { t, mktStageLabels, emptyValue, filename = 'po-list.csv' }) {
  const header = [
    t('common.poNo'),
    t('common.customer'),
    t('common.buyer'),
    t('common.material'),
    t('common.status'),
    t('common.etd'),
    t('common.orderDate'),
    t('pages.po.brand'),
    t('common.category'),
    t('pages.po.mktFlow'),
  ]
  const lines = [header.map(csvEscape).join(',')]
  for (const row of rows) {
    const stage = row.mkt_workflow_stage
      ? mktStageLabels[row.mkt_workflow_stage] || row.mkt_workflow_stage
      : ''
    lines.push(
      [
        row.po_number || '',
        row.customerName || row.customer_name_snapshot || '',
        row.buyer || '',
        row.material_hint && row.material_hint !== emptyValue ? row.material_hint : '',
        row.status ? t(`status.${row.status}`) : '',
        row.etd || '',
        row.order_date_fmt || (row.order_date ? String(row.order_date).slice(0, 10) : ''),
        row.brand_name_snapshot || '',
        poOrderCategoryLabel(row.po_category, t, (k) => Boolean(t(k))),
        stage,
      ]
        .map(csvEscape)
        .join(','),
    )
  }
  const blob = new Blob([`\ufeff${lines.join('\n')}`], { type: 'text/csv;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  const anchor = document.createElement('a')
  anchor.href = url
  anchor.download = filename
  anchor.click()
  URL.revokeObjectURL(url)
}

export function parsePoRoutePoId(route) {
  const poIdRaw = route?.query?.po_id ?? route?.query?.highlight
  const poId = Number(poIdRaw)
  if (Number.isNaN(poId) || poId <= 0) return null
  return poId
}

/** Deep link hanya buka wizard edit jika query edit/mode diset eksplisit. */
export function shouldOpenPoRouteEdit(route) {
  const raw = route?.query?.edit ?? route?.query?.mode
  const v = String(raw ?? '').trim().toLowerCase()
  return v === '1' || v === 'true' || v === 'edit'
}

export function poRouteQueryWithoutDeepLink(route) {
  const next = { ...(route?.query || {}) }
  delete next.po_id
  delete next.highlight
  delete next.edit
  delete next.mode
  return next
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
