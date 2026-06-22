import { computed, ref, watch } from 'vue'

import {
  buildPoPageQuery,
  createPoOrderDateShortcuts,
  enrichPoRows,
} from '../utils/poList.js'

/** State filter + pagination daftar PO. */
export function usePoList({ t }) {
  const keyword = ref('')
  const filterCustomerId = ref(null)
  const filterStatus = ref('')
  const filterBuyer = ref('')
  const filterOrderDateRange = ref(null)
  const rows = ref([])
  const totalRows = ref(0)
  const page = ref(1)
  const pageSize = ref(20)
  const loading = ref(false)

  const poOrderDateShortcuts = computed(() => createPoOrderDateShortcuts(t))

  function buildPageQuery() {
    return buildPoPageQuery({
      keyword: keyword.value,
      filterCustomerId: filterCustomerId.value,
      filterBuyer: filterBuyer.value,
      filterStatus: filterStatus.value,
      filterOrderDateRange: filterOrderDateRange.value,
      page: page.value,
      pageSize: pageSize.value,
    })
  }

  function enrichHeaders(items, customers, brands) {
    return enrichPoRows(items, {
      customers,
      brands,
      emptyValue: t('common.emptyValue'),
      noMaterialLabel: t('pages.po.noMaterialOnLines'),
    })
  }

  function resetFilters(loadFn) {
    filterCustomerId.value = null
    filterStatus.value = ''
    filterBuyer.value = ''
    keyword.value = ''
    filterOrderDateRange.value = null
    page.value = 1
    if (loadFn) loadFn()
  }

  function registerFilterWatch(loadFn) {
    let filterLoadTimer = null
    watch([keyword, filterCustomerId, filterBuyer, filterStatus, filterOrderDateRange], () => {
      page.value = 1
      if (filterLoadTimer) clearTimeout(filterLoadTimer)
      filterLoadTimer = setTimeout(() => {
        loadFn()
      }, 300)
    })
    watch([page, pageSize], () => {
      loadFn()
    })
  }

  return {
    keyword,
    filterCustomerId,
    filterStatus,
    filterBuyer,
    filterOrderDateRange,
    rows,
    totalRows,
    page,
    pageSize,
    loading,
    poOrderDateShortcuts,
    buildPageQuery,
    enrichHeaders,
    resetFilters,
    registerFilterWatch,
  }
}
