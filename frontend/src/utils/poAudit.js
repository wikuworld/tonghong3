/** Label & diff audit revisi PO. */

const AUDIT_KEY_MAP = {
  quantity_order: 'quantityOrder',
  unit_price: 'unitPrice',
  line_etd: 'lineEtd',
  thi_line_ref: 'thiLineRef',
  color_family: 'colorFamily',
  color_standard: 'colorStandard',
  color_reference: 'colorReference',
  thickness: 'thickness',
  thickness_text: 'thickness',
  softness: 'softness',
  vir_softness_type: 'virSoftnessType',
  backing: 'backing',
  emboss: 'emboss',
  style_article: 'styleArticle',
  model: 'model',
  material_name: 'materialName',
  color: 'color',
  remark: 'remark',
  detail_remark: 'remark',
  status: 'status',
  delivery_schedules: 'deliverySchedules',
  po_number: 'poNumber',
  po_id: 'poId',
  po_header_id: 'poHeaderId',
  master_item_id: 'masterItemId',
  color_swatch_recipe_id: 'colorSwatchRecipeId',
  color_both: 'colorBoth',
}

/** @deprecated gunakan getPoAuditFieldLabels(t) */
export const PO_AUDIT_FIELD_LABELS = {
  quantity_order: 'Qty Order',
  unit_price: 'Harga USD',
  line_etd: 'ETD Baris',
  thi_line_ref: 'THI/Lot',
  color_family: 'Kategori Warna',
  color_standard: 'Color standart',
  thickness: 'Ketebalan',
  softness: 'Kelembutan',
  backing: 'Backing',
  emboss: 'Timbulan',
  style_article: 'Style/Article',
  model: 'Model',
  material_name: 'Material',
  color: 'Warna',
  remark: 'Catatan',
  status: 'Status',
  delivery_schedules: 'Rencana Kirim',
  po_number: 'No. PO',
  po_id: 'PO ID',
  po_header_id: 'PO Header ID',
}

export function getPoAuditFieldLabels(t) {
  const labels = {}
  for (const [field, i18nKey] of Object.entries(AUDIT_KEY_MAP)) {
    labels[field] = t(`pages.po.audit.${i18nKey}`)
  }
  labels.color_both = t('pages.po.audit.colorBoth')
  return labels
}

export function auditFieldLabel(key, labels = PO_AUDIT_FIELD_LABELS) {
  return labels[key] || key
}

function isEmptyAuditValue(value) {
  if (value == null || value === '') return true
  if (Array.isArray(value) && value.length === 0) return true
  return false
}

export function formatAuditValue(value) {
  if (value == null || value === '') return '—'
  if (Array.isArray(value)) {
    if (!value.length) return '—'
    return value
      .map((row) => {
        if (row && typeof row === 'object') {
          const qty = row.qty != null ? row.qty : '—'
          const dt = row.delivery_date || '—'
          return `#${row.sequence_no || '—'} ${qty} / ${dt}`
        }
        return String(row)
      })
      .join('; ')
  }
  if (typeof value === 'object') return JSON.stringify(value)
  return String(value)
}

export function auditChangedFields(a, labels = PO_AUDIT_FIELD_LABELS) {
  const action = String(a.action || '').toLowerCase()
  const before = a.before || {}
  const after = a.after || {}
  const allKeys = new Set([...Object.keys(before), ...Object.keys(after)])
  const changes = []
  const skipKeys = new Set([
    'id',
    'created_at',
    'updated_at',
    'po_header_id',
    'po_id',
    'thickness_min',
    'thickness_max',
  ])

  for (const key of allKeys) {
    if (skipKeys.has(key)) continue
    const b = before[key]
    const af = after[key]
    if (isEmptyAuditValue(b) && isEmptyAuditValue(af)) continue
    if (JSON.stringify(b ?? null) !== JSON.stringify(af ?? null)) {
      let change = null
      if (typeof b === 'number' && typeof af === 'number') {
        const diff = af - b
        change = diff > 0 ? `+${diff}` : `${diff}`
      }
      changes.push({
        key,
        before: formatAuditValue(b),
        after: formatAuditValue(af),
        change,
        rawBefore: b,
        rawAfter: af,
      })
    }
  }

  if (action === 'create') {
    changes.forEach((c) => {
      c.before = '—'
    })
  }
  if (action === 'delete') {
    changes.forEach((c) => {
      c.after = '—'
    })
  }

  const colorIdx = changes.findIndex((c) => c.key === 'color')
  const colorFamilyIdx = changes.findIndex((c) => c.key === 'color_family')
  if (colorIdx !== -1 && colorFamilyIdx !== -1) {
    const colorVal = changes[colorIdx].after
    const colorFamilyVal = changes[colorFamilyIdx].after
    if (colorVal === colorFamilyVal) {
      changes[colorIdx].key = 'color_both'
      changes[colorIdx].displayLabel = labels.color_both || auditFieldLabel('color_both', labels)
      changes.splice(colorFamilyIdx, 1)
    }
  }

  return changes
}
