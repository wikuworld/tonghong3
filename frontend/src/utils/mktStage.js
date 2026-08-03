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
