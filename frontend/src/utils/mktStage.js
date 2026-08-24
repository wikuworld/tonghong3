/** Urutan tahap MKT — sama dengan backend `MKT_STAGES_ORDER`. */
export const MKT_STAGE_ORDER = [
  'input_system',
  'rekap_printed',
  'with_ppic',
  'in_outstanding',
  'material_followup',
  'delivery_arranged',
  'sj_invpl',
  'invoice_billing',
]

export function normalizeMktStage(stage) {
  const s = String(stage || 'input_system').trim() || 'input_system'
  return s === 'back_to_mkt' ? 'in_outstanding' : s
}

/** Status follow-up bahan mengikuti tahap MKT — tanpa toggle manual. */
export function materialFollowUpAutoStatus(stage) {
  const s = normalizeMktStage(stage)
  const idx = MKT_STAGE_ORDER.indexOf(s)
  if (idx < 0 || idx < MKT_STAGE_ORDER.indexOf('in_outstanding')) return 'idle'
  if (idx >= MKT_STAGE_ORDER.indexOf('delivery_arranged')) return 'done'
  if (s === 'material_followup') return 'in_progress'
  return 'pending'
}

/**
 * Langkah kerja berikutnya di daftar SO — aksi halaman, bukan sekadar «lanjut tahap».
 * @returns {'rekap'|'confirm_so'|'assign_ppic'|'advance'|'outstanding'|'planning'|'delivery'|'invoice'|'wait'|'done'}
 */
export function soListNextStep(row = {}, opts = {}) {
  const stage = normalizeMktStage(row.mkt_workflow_stage)
  const status = String(row.status || '').trim().toLowerCase()
  const hasPpic = Boolean(opts.hasPpic)
  const stuck = String(row.stuck_reason || '')

  if (stage === 'invoice_billing') return 'done'

  if (stage === 'input_system') {
    if (!row.rekap_printed_at) return 'rekap'
    if (status === 'draft') return 'confirm_so'
    return 'advance'
  }

  if (stage === 'rekap_printed') {
    if (!hasPpic) return 'assign_ppic'
    return 'advance'
  }

  if (stage === 'with_ppic') {
    if (stuck) return 'wait'
    return 'advance'
  }

  if (stage === 'in_outstanding') return 'outstanding'
  if (stage === 'material_followup') return 'planning'
  if (stage === 'delivery_arranged') return 'delivery'
  if (stage === 'sj_invpl') return 'invoice'
  return 'wait'
}

export function soListNextStepActionable(kind) {
  return kind !== 'wait' && kind !== 'done'
}

/** Label tahap alur marketing (shared PO list & marketing flow). */

export function createMktStageLabels(t) {
  return {
    input_system: t('mktStage.input_system'),
    rekap_printed: t('mktStage.rekap_printed'),
    with_ppic: t('mktStage.with_ppic'),
    // Alias historis — digabung ke in_outstanding
    back_to_mkt: t('mktStage.in_outstanding'),
    in_outstanding: t('mktStage.in_outstanding'),
    material_followup: t('mktStage.material_followup'),
    delivery_arranged: t('mktStage.delivery_arranged'),
    sj_invpl: t('mktStage.sj_invpl'),
    invoice_billing: t('mktStage.invoice_billing'),
  }
}

export function mktStageLabel(stage, labels, emptyValue = '—') {
  if (!stage) return emptyValue
  return labels[stage] || stage
}
