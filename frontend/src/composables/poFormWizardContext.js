import { inject, provide, reactive } from 'vue'

export const PO_FORM_WIZARD_KEY = Symbol('poFormWizard')

export function providePoWizardContext(ctx) {
  // reactive() agar ref di context ter-unwrap di template (v-model el-dialog).
  provide(PO_FORM_WIZARD_KEY, reactive(ctx))
}

export function usePoWizardContext() {
  const ctx = inject(PO_FORM_WIZARD_KEY, null)
  if (!ctx) {
    throw new Error('usePoWizardContext: PoFormWizardDialog harus di dalam PurchaseOrderPage provider')
  }
  return ctx
}
