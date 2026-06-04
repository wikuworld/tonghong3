import { reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'

import { getPo, listPoDetails, marketingRevisePo, toIsoDate } from '../api/client'
import { parseApiErrorMessage } from '../utils/poApi.js'

/** Dialog revisi marketing (header + baris PO). */
export function usePoMarketingRevise({ t, editingPoId, formModel }) {
  const visible = ref(false)
  const loading = ref(false)
  const saving = ref(false)
  const header = reactive({
    remark: '',
    etd: '',
    delivery_address: '',
    material_followup_remark: '',
    material_followup_done: false,
  })
  const lines = ref([])

  async function open() {
    const poId = editingPoId.value
    if (!poId) return
    loading.value = true
    try {
      const [po, details] = await Promise.all([getPo(poId), listPoDetails(poId)])
      header.remark = formModel.remark || ''
      header.etd = formModel.etd || ''
      header.delivery_address = formModel.delivery_address || ''
      header.material_followup_remark = po.material_followup_remark || ''
      header.material_followup_done = Boolean(po.material_followup_done)
      lines.value = details.map((d) => ({
        detail_id: d.id,
        material_name: d.material_name || '',
        line_etd: d.line_etd ? String(d.line_etd).slice(0, 10) : '',
        detail_remark: d.detail_remark || '',
        marketing_outstanding_remark: d.marketing_outstanding_remark || '',
        rtd_text: d.rtd_text || '',
      }))
      visible.value = true
    } catch (e) {
      ElMessage.error(parseApiErrorMessage(e, t('common.errorGeneric')))
    } finally {
      loading.value = false
    }
  }

  async function submit() {
    const poId = editingPoId.value
    if (!poId) return
    saving.value = true
    try {
      const payloadHeader = {
        remark: header.remark?.trim() || null,
        etd: toIsoDate(header.etd) || null,
        delivery_address: header.delivery_address?.trim() || null,
        material_followup_remark: header.material_followup_remark?.trim() || null,
        material_followup_done: Boolean(header.material_followup_done),
      }
      const payloadLines = lines.value.map((r) => {
        const o = { detail_id: r.detail_id }
        const le = toIsoDate(r.line_etd)
        if (le) o.line_etd = le
        o.detail_remark = r.detail_remark?.trim() || null
        o.marketing_outstanding_remark = r.marketing_outstanding_remark?.trim() || null
        o.rtd_text = r.rtd_text?.trim() || null
        return o
      })
      await marketingRevisePo(poId, { header: payloadHeader, lines: payloadLines })
      formModel.remark = header.remark || ''
      formModel.etd = header.etd || ''
      formModel.delivery_address = header.delivery_address || ''
      ElMessage.success(t('pages.po.marketingReviseSaved'))
      visible.value = false
    } catch (e) {
      ElMessage.error(parseApiErrorMessage(e, t('common.errorGeneric')))
    } finally {
      saving.value = false
    }
  }

  return {
    visible,
    loading,
    saving,
    header,
    lines,
    open,
    submit,
  }
}
