import { listMasterItemDimensionValues } from '../api/client'

/** Step 2: dimensi material & ketebalan dari master. */
export function usePoStepLines({
  materialDimensionOptions,
  thicknessDimensionOptions,
  masterDimensionCategoryParam,
}) {
  async function refreshMaterialDimensionOptions() {
    try {
      const r = await listMasterItemDimensionValues('materials', {
        category: masterDimensionCategoryParam(),
      })
      materialDimensionOptions.value = r.values || []
    } catch {
      materialDimensionOptions.value = []
    }
  }

  async function refreshThicknessOptionsFromApi() {
    try {
      const r = await listMasterItemDimensionValues('thickness', {
        category: masterDimensionCategoryParam(),
      })
      thicknessDimensionOptions.value = r.values || []
    } catch {
      thicknessDimensionOptions.value = []
    }
  }

  function upsertMasterItemInCache(masterItems, row) {
    if (!row?.id) return
    const rows = masterItems.value
    const idx = rows.findIndex((x) => x.id === row.id)
    if (idx >= 0) rows[idx] = { ...rows[idx], ...row }
    else rows.push(row)
  }

  return {
    refreshMaterialDimensionOptions,
    refreshThicknessOptionsFromApi,
    upsertMasterItemInCache,
  }
}
