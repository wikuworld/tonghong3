import { inject, provide } from 'vue'

export const PO_FORM_WIZARD_KEY = Symbol('poFormWizard')

export function providePoWizardContext(ctx) {
  provide(PO_FORM_WIZARD_KEY, ctx)
}

export function usePoWizardContext() {
  const ctx = inject(PO_FORM_WIZARD_KEY, null)
  if (!ctx) {
    throw new Error('usePoWizardContext: PoFormWizardDialog harus di dalam PurchaseOrderPage provider')
  }
  return ctx
}
