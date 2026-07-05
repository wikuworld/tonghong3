import { computed } from 'vue'
import { can, canWrite, permissionMatrixVersion } from '../security/permissions'

export function useModulePermission(moduleKey) {
  const tick = computed(() => permissionMatrixVersion.value)

  const canView = computed(() => {
    tick.value
    return can(moduleKey, 'view')
  })
  const canCreate = computed(() => {
    tick.value
    return can(moduleKey, 'create')
  })
  const canUpdate = computed(() => {
    tick.value
    return can(moduleKey, 'update')
  })
  const canDelete = computed(() => {
    tick.value
    return can(moduleKey, 'delete')
  })
  const canManage = computed(() => {
    tick.value
    return canWrite(moduleKey)
  })
  const canExport = computed(() => {
    tick.value
    return can(moduleKey, 'export')
  })
  const canPrint = computed(() => {
    tick.value
    return can(moduleKey, 'print')
  })
  const canAdvance = computed(() => {
    tick.value
    return can(moduleKey, 'advance')
  })

  return {
    canView,
    canCreate,
    canUpdate,
    canDelete,
    canManage,
    canExport,
    canPrint,
    canAdvance,
  }
}
