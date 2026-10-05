import { describe, expect, it } from 'vitest'
import { auditChangedFields, formatAuditValue } from './poAudit.js'

describe('auditChangedFields', () => {
  it('shows item fields on create (after only)', () => {
    const changes = auditChangedFields({
      action: 'create',
      before: null,
      after: {
        po_id: 18,
        material_name: 'AROMA-P',
        color: 'LT SMOKE GREY (0AL)',
        thickness_text: '1.2 - 1.4',
        quantity_order: 99,
        unit_price: 12,
        color_reference: null,
        delivery_schedules: [],
      },
    })
    const keys = changes.map((c) => c.key)
    expect(keys).toContain('material_name')
    expect(keys).toContain('color')
    expect(keys).toContain('thickness_text')
    expect(keys).toContain('quantity_order')
    expect(keys).not.toContain('po_id')
    expect(keys).not.toContain('color_reference')
    expect(keys).not.toContain('delivery_schedules')
    const material = changes.find((c) => c.key === 'material_name')
    expect(material.before).toBe('—')
    expect(material.after).toBe('AROMA-P')
  })

  it('shows deleted item fields from before', () => {
    const changes = auditChangedFields({
      action: 'delete',
      before: { material_name: 'SMOKE AUDIT MAT', color: 'BLACK', quantity_order: 12.5 },
      after: null,
    })
    const material = changes.find((c) => c.key === 'material_name')
    expect(material.before).toBe('SMOKE AUDIT MAT')
    expect(material.after).toBe('—')
  })
})

describe('formatAuditValue', () => {
  it('formats delivery schedules', () => {
    expect(formatAuditValue([{ sequence_no: 1, qty: 20, delivery_date: '2026-08-21' }])).toBe(
      '#1 20 / 2026-08-21',
    )
  })
})
