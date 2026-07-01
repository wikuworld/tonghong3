/** Pemetaan teks stuck reason dari backend ke kunci i18n. */

export const STUCK_REASON_I18N_KEYS = {
  'Menunggu rekap PO diprint': 'pages.marketingFlow.stuckReasons.waitRekapPrint',
  'PO belum di-confirm': 'pages.marketingFlow.stuckReasons.poNotConfirmed',
  'Belum di-assign ke PPIC': 'pages.marketingFlow.stuckReasons.ppicNotAssigned',
  'Menunggu PPIC menyelesaikan tugas': 'pages.marketingFlow.stuckReasons.ppicNotComplete',
  'Material belum di-follow up': 'pages.marketingFlow.stuckReasons.materialNotFollowedUp',
  'Material belum selesai di-follow up': 'pages.marketingFlow.stuckReasons.materialFollowUpIncomplete',
  'Delivery belum dibuat': 'pages.marketingFlow.stuckReasons.deliveryNotCreated',
  'SJ/INVPL belum dicetak': 'pages.marketingFlow.stuckReasons.sjInvplNotPrinted',
  'Invoice belum dibuat': 'pages.marketingFlow.stuckReasons.invoiceNotCreated',
}

export function stuckReasonLabel(reason, t, emptyValue = '') {
  if (!reason) return emptyValue
  const key = STUCK_REASON_I18N_KEYS[reason]
  return key ? t(key) : reason
}
