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
  it('draft waits for Order Penjualan confirm; confirmed goes to outstanding', () => {
    expect(soListNextStep({ mkt_workflow_stage: 'input_system' })).toBe('wait')
    expect(soListNextStep({ mkt_workflow_stage: 'input_system', status: 'draft' })).toBe('wait')
    expect(soListNextStep({ mkt_workflow_stage: 'input_system', status: 'confirmed' })).toBe('outstanding')
    expect(soListNextStep({ mkt_workflow_stage: 'input_system', status: 'production' })).toBe('outstanding')
  })

  it('skips RKPO/PPIC gates — historical stages go to outstanding', () => {
    expect(soListNextStep({ mkt_workflow_stage: 'rekap_printed' })).toBe('outstanding')
    expect(soListNextStep({ mkt_workflow_stage: 'rekap_printed' }, { hasPpic: true })).toBe('outstanding')
    expect(
      soListNextStep(
        { mkt_workflow_stage: 'with_ppic' },
        { hasPpic: true, ppicStatus: 'pending' },
      ),
    ).toBe('outstanding')
    expect(
      soListNextStep({ mkt_workflow_stage: 'with_ppic' }, { hasPpic: true, ppicStatus: 'completed' }),
    ).toBe('outstanding')
  })

  it('routes outstanding and ship work to the right page', () => {
    expect(soListNextStep({ mkt_workflow_stage: 'in_outstanding' })).toBe('outstanding')
    expect(soListNextStep({ mkt_workflow_stage: 'back_to_mkt' })).toBe('outstanding')
    expect(soListNextStep({ mkt_workflow_stage: 'material_followup' })).toBe('outstanding')
    expect(soListNextStep({ mkt_workflow_stage: 'delivery_arranged' })).toBe('delivery')
    expect(soListNextStep({ mkt_workflow_stage: 'sj_invpl' })).toBe('invoice')
    expect(soListNextStep({ mkt_workflow_stage: 'invoice_billing' })).toBe('done')
  })
})
