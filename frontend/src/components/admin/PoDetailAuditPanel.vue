<template>
  <div v-if="entries.length" class="mt-4">
    <div class="mb-3 text-sm font-semibold text-slate-700">{{ t('pages.po.lineRevisionHistory') }}</div>
    <div class="space-y-3">
      <div
        v-for="a in visibleEntries"
        :key="a.id"
        class="rounded-lg border border-slate-200 bg-white p-4 shadow-sm"
      >
        <div class="mb-3 flex flex-wrap items-center justify-between gap-2 border-b border-slate-100 pb-2">
          <div class="flex items-center gap-2">
            <span
              class="rounded-full px-2 py-0.5 text-xs font-medium"
              :class="actionClass(a.action)"
            >
              {{ a.action?.toUpperCase() }}
            </span>
            <span v-if="a.entity_type === 'sales_order_line'" class="text-xs text-slate-500">
              {{ t('pages.poDetail.auditLine') }} #{{ a.entity_id }}
            </span>
          </div>
          <div class="flex items-center gap-2 text-xs text-slate-500">
            <span v-if="a.actor">{{ a.actor }}</span>
            <span v-else class="italic">{{ t('common.system') }}</span>
            <span>{{ t('common.dashSeparator') }}</span>
            <span>{{ formatAuditTime(a.created_at) }}</span>
          </div>
        </div>
        <div class="space-y-2">
          <template v-if="changesFor(a).length">
            <div
              v-for="field in changesFor(a)"
              :key="field.key"
              class="grid grid-cols-12 gap-2 rounded bg-slate-50 p-2 text-xs"
            >
              <div class="col-span-12 font-medium text-slate-700 lg:col-span-2">
                {{ field.displayLabel || auditFieldLabel(field.key) }}
              </div>
              <div class="col-span-12 lg:col-span-5">
                <span class="text-slate-400">{{ t('pages.po.audit.before') }}: </span>
                <span class="text-red-600 line-through">{{ field.before ?? '—' }}</span>
              </div>
              <div class="col-span-12 hidden items-center gap-1 lg:col-span-5 lg:flex">
                <span class="text-slate-400">{{ t('pages.po.audit.after') }}: </span>
                <span class="text-green-600">{{ field.after ?? '—' }}</span>
                <span v-if="field.change" class="ml-auto rounded bg-green-100 px-1.5 py-0.5 text-green-700">
                  {{ field.change }}
                </span>
              </div>
            </div>
          </template>
          <div v-else class="text-xs italic text-slate-400">
            {{ t('pages.po.audit.noChanges') }}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

import {
  auditChangedFields as resolveAuditChangedFields,
  auditFieldLabel as resolveAuditFieldLabel,
  getPoAuditFieldLabels,
} from '../../utils/poAudit.js'

const props = defineProps({
  entries: { type: Array, default: () => [] },
})

const { t } = useI18n()

const auditLabels = computed(() => getPoAuditFieldLabels(t))

const visibleEntries = computed(() =>
  (props.entries || []).filter((a) => a.before || a.after),
)

function auditFieldLabel(key) {
  return resolveAuditFieldLabel(key, auditLabels.value)
}

function changesFor(entry) {
  return resolveAuditChangedFields(entry, auditLabels.value)
}

function actionClass(action) {
  if (action === 'create') return 'bg-green-100 text-green-700'
  if (action === 'update') return 'bg-blue-100 text-blue-700'
  if (action === 'delete') return 'bg-red-100 text-red-700'
  return 'bg-slate-100 text-slate-600'
}

function formatAuditTime(value) {
  return value ? String(value).replace('T', ' ').slice(0, 16) : ''
}
</script>
