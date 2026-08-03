/** Label & diff audit revisi PO. */

const AUDIT_KEY_MAP = {
  quantity_order: 'quantityOrder',
  unit_price: 'unitPrice',
  line_etd: 'lineEtd',
  thi_line_ref: 'thiLineRef',
  color_family: 'colorFamily',
  color_standard: 'colorStandard',
  thickness: 'thickness',
  softness: 'softness',
  backing: 'backing',
  emboss: 'emboss',
  style_article: 'styleArticle',
  model: 'model',
  material_name: 'materialName',
  color: 'color',
  remark: 'remark',
  status: 'status',
  delivery_schedules: 'deliverySchedules',
  po_number: 'poNumber',
  po_id: 'poId',
  po_header_id: 'poHeaderId',
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
  delivery_schedules: 'Jadwal Pengiriman',
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

export function auditChangedFields(a, labels = PO_AUDIT_FIELD_LABELS) {
  const before = a.before || {}
  const after = a.after || {}
  const allKeys = new Set([...Object.keys(before), ...Object.keys(after)])
  const changes = []
  const skipKeys = new Set(['id', 'created_at', 'updated_at', 'po_header_id'])

  for (const key of allKeys) {
    if (skipKeys.has(key)) continue
    const b = before[key]
    const af = after[key]
    if (JSON.stringify(b) !== JSON.stringify(af)) {
      let change = null
      if (typeof b === 'number' && typeof af === 'number') {
        const diff = af - b
        change = diff > 0 ? `+${diff}` : `${diff}`
      }
      changes.push({ key, before: b, after: af, change })
    }
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
