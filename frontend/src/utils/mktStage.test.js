import { describe, expect, it } from 'vitest'
import { materialFollowUpAutoStatus, normalizeMktStage, soListNextStep } from './mktStage.js'

describe('normalizeMktStage', () => {
  it('maps historical back_to_mkt to in_outstanding', () => {
    expect(normalizeMktStage('back_to_mkt')).toBe('in_outstanding')
    expect(normalizeMktStage('')).toBe('input_system')
  })
})

describe('materialFollowUpAutoStatus', () => {
  it('is idle before outstanding', () => {
    expect(materialFollowUpAutoStatus('input_system')).toBe('idle')
    expect(materialFollowUpAutoStatus('rekap_printed')).toBe('idle')
    expect(materialFollowUpAutoStatus('with_ppic')).toBe('idle')
  })

  it('follows stage after outstanding', () => {
    expect(materialFollowUpAutoStatus('in_outstanding')).toBe('pending')
    expect(materialFollowUpAutoStatus('back_to_mkt')).toBe('pending')
    expect(materialFollowUpAutoStatus('material_followup')).toBe('in_progress')
    expect(materialFollowUpAutoStatus('delivery_arranged')).toBe('done')
    expect(materialFollowUpAutoStatus('invoice_billing')).toBe('done')
  })
})

describe('soListNextStep', () => {
  it('starts with recap then confirm before advancing', () => {
    expect(soListNextStep({ mkt_workflow_stage: 'input_system' })).toBe('rekap')
    expect(soListNextStep({ mkt_workflow_stage: 'input_system', rekap_printed_at: '2026-08-01', status: 'draft' })).toBe(
      'confirm_so',
    )
    expect(
      soListNextStep({ mkt_workflow_stage: 'input_system', rekap_printed_at: '2026-08-01', status: 'confirmed' }),
    ).toBe('advance')
    expect(
      soListNextStep({ mkt_workflow_stage: 'input_system', rekap_printed_at: '2026-08-01', status: 'production' }),
    ).toBe('advance')
  })

  it('assigns PPIC after recap, then waits on PPIC', () => {
    expect(soListNextStep({ mkt_workflow_stage: 'rekap_printed' })).toBe('assign_ppic')
    expect(soListNextStep({ mkt_workflow_stage: 'rekap_printed' }, { hasPpic: true })).toBe('advance')
    expect(soListNextStep({ mkt_workflow_stage: 'with_ppic', stuck_reason: 'Menunggu PPIC' })).toBe('wait')
    expect(soListNextStep({ mkt_workflow_stage: 'with_ppic' })).toBe('advance')
  })

  it('routes outstanding and ship work to the right page', () => {
    expect(soListNextStep({ mkt_workflow_stage: 'in_outstanding' })).toBe('outstanding')
    expect(soListNextStep({ mkt_workflow_stage: 'back_to_mkt' })).toBe('outstanding')
    expect(soListNextStep({ mkt_workflow_stage: 'material_followup' })).toBe('planning')
    expect(soListNextStep({ mkt_workflow_stage: 'delivery_arranged' })).toBe('delivery')
    expect(soListNextStep({ mkt_workflow_stage: 'sj_invpl' })).toBe('invoice')
    expect(soListNextStep({ mkt_workflow_stage: 'invoice_billing' })).toBe('done')
  })
})
