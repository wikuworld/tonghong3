<template>
  <AdminSection :title="t('pages.buyerPrices.title')" :subtitle="t('pages.buyerPrices.subtitle')">
    <template #actions>
      <el-input
        v-model="keyword"
        :placeholder="t('pages.buyerPrices.searchPlaceholder')"
        clearable
        class="buyer-price-toolbar-search"
      />
      <span v-if="loading" class="text-xs text-slate-500">{{ t('common.loadingData') }}</span>
      <el-button :icon="Refresh" :loading="loading" @click="load">{{ t('common.refresh') }}</el-button>
      <el-button v-if="canCreate" type="primary" :icon="Plus" @click="openCreateDialog">
        {{ t('common.create') }}
      </el-button>
    </template>

    <div class="admin-inner-card">
      <div class="admin-inner-card__head buyer-inner-head">
        <div>
          <h3 class="admin-inner-card__title">{{ t('pages.buyerPrices.listSectionTitle') }}</h3>
          <p class="admin-inner-card__sub">{{ t('pages.buyerPrices.listSubtitle') }}</p>
        </div>
        <el-tooltip placement="top-start" :show-after="200">
          <template #content>{{ t('pages.buyerPrices.pageHint') }}</template>
          <el-icon class="buyer-page-hint" :size="16" tabindex="0" :aria-label="t('pages.buyerPrices.pageHint')">
            <InfoFilled />
          </el-icon>
        </el-tooltip>
      </div>

      <div class="admin-stats-grid admin-stats-grid--2 buyer-price-stats">
        <div class="admin-stat-card">
          <span class="admin-stat-card__value">{{ listStats.total }}</span>
          <span class="admin-stat-card__label">{{ t('pages.buyerPrices.statTotal') }}</span>
        </div>
        <div class="admin-stat-card admin-stat-card--info">
          <span class="admin-stat-card__value">{{ listStats.shown }}</span>
          <span class="admin-stat-card__label">{{ t('pages.buyerPrices.statShown') }}</span>
        </div>
      </div>

      <p class="admin-scroll-hint">{{ t('pages.buyerPrices.scrollHint') }}</p>

      <div class="admin-table-scroll buyer-price-table-wrap">
        <el-table
          :data="filteredRows"
          v-loading="loading"
          border
          stripe
          size="small"
          class="admin-table buyer-price-table"
          table-layout="fixed"
          :empty-text="t('pages.buyerPrices.tableEmpty')"
        >
          <el-table-column type="index" :label="t('common.noLabel')" width="56" align="center" />
          <el-table-column prop="buyer_code" :label="t('pages.buyerPrices.buyerCode')" width="120" show-overflow-tooltip />
          <el-table-column prop="currency" :label="t('pages.buyerPrices.currency')" width="90" align="center" />
          <el-table-column prop="title" :label="t('pages.buyerPrices.listTitle')" min-width="160" show-overflow-tooltip />
          <el-table-column prop="period_label" :label="t('pages.buyerPrices.period')" min-width="180" show-overflow-tooltip />
          <el-table-column :label="t('pages.buyerPrices.itemList')" min-width="240">
            <template #default="{ row }">
              <div v-if="!(row.item_codes || []).length" class="buyer-cell-empty">—</div>
              <el-tooltip v-else placement="top-start" :show-after="200">
                <template #content>
                  <div class="buyer-item-tooltip">
                    <p class="buyer-item-tooltip__title">
                      {{ t('pages.buyerPrices.itemList') }} ({{ row.item_codes.length }})
                    </p>
                    <ol class="buyer-item-tooltip__list">
                      <li v-for="(item, idx) in row.item_codes" :key="`${idx}-${item}`">{{ item }}</li>
                    </ol>
                  </div>
                </template>
                <div class="buyer-item-cell">
                  <span class="buyer-item-cell__badge">{{ row.item_codes.length }}</span>
                  <span class="buyer-item-cell__text">{{ row.item_codes[0] }}</span>
                  <span v-if="row.item_codes.length > 1" class="buyer-item-cell__more">
                    +{{ row.item_codes.length - 1 }}
                  </span>
                </div>
              </el-tooltip>
            </template>
          </el-table-column>
          <el-table-column :label="t('pages.buyerPrices.priceComponentsFilled')" min-width="200">
            <template #default="{ row }">
              <div v-if="!(row.filled_price_components || []).length" class="buyer-cell-empty">—</div>
              <div v-else class="buyer-component-tags">
                <el-tag
                  v-for="comp in row.filled_price_components"
                  :key="comp"
                  size="small"
                  effect="plain"
                  type="info"
                >
                  {{ comp }}
                </el-tag>
              </div>
            </template>
          </el-table-column>
          <el-table-column :label="t('common.actions')" width="130" align="center" fixed="right">
            <template #default="{ row }">
              <div class="buyer-price-row-actions">
                <el-tooltip :content="t('pages.buyerPrices.viewDetail')" placement="top">
                  <el-button
                    :icon="View"
                    link
                    type="info"
                    :aria-label="t('pages.buyerPrices.viewDetail')"
                    @click="openDetail(row.id)"
                  />
                </el-tooltip>
                <el-tooltip v-if="canUpdate" :content="t('pages.buyerPrices.manageData')" placement="top">
                  <el-button
                    :icon="EditPen"
                    link
                    type="primary"
                    :aria-label="t('pages.buyerPrices.manageData')"
                    @click="openMaster(row.id)"
                  />
                </el-tooltip>
                <el-tooltip v-if="canDelete" :content="t('common.delete')" placement="top">
                  <el-button
                    :icon="Delete"
                    link
                    type="danger"
                    :aria-label="t('common.delete')"
                    @click="confirmDelete(row)"
                  />
                </el-tooltip>
              </div>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </div>

    <!-- Dialog: buat list buyer baru -->
    <el-dialog
      v-model="createVisible"
      width="560px"
      destroy-on-close
      align-center
      class="buyer-price-dialog"
      :show-close="true"
      @closed="resetCreateForm"
    >
      <template #header>
        <div class="buyer-dialog-header">
          <div class="buyer-dialog-header__main">
            <h3 class="buyer-dialog-header__title">{{ t('pages.buyerPrices.dialogAdd') }}</h3>
            <p class="buyer-dialog-header__sub">{{ t('pages.buyerPrices.dialogAddSub') }}</p>
          </div>
          <el-tooltip placement="top-start" :show-after="200">
            <template #content>{{ t('pages.buyerPrices.formHint') }}</template>
            <el-icon class="buyer-page-hint" :size="16" tabindex="0" :aria-label="t('pages.buyerPrices.formHint')">
              <InfoFilled />
            </el-icon>
          </el-tooltip>
        </div>
      </template>

      <div class="buyer-dialog-body">
        <div class="buyer-dialog-panel">
          <div class="buyer-dialog-panel__head">
            <h4 class="buyer-dialog-panel__title">{{ t('pages.buyerPrices.dialogGroupIdentity') }}</h4>
          </div>
          <div class="buyer-dialog-panel__body">
            <el-form ref="createFormRef" :model="createForm" :rules="createRules" label-position="top" @submit.prevent>
              <el-row :gutter="16">
                <el-col :xs="24" :sm="12">
                  <el-form-item :label="t('pages.buyerPrices.buyerCode')" prop="buyer_code">
                    <el-input
                      v-model="createForm.buyer_code"
                      :placeholder="t('pages.buyerPrices.placeholderBuyerCode')"
                      maxlength="32"
                      show-word-limit
                      clearable
                    />
                  </el-form-item>
                </el-col>
                <el-col :xs="24" :sm="12">
                  <el-form-item :label="t('pages.buyerPrices.currency')">
                    <el-select v-model="createForm.currency" class="w-full">
                      <el-option label="USD" value="USD" />
                      <el-option label="IDR" value="IDR" />
                      <el-option label="EUR" value="EUR" />
                    </el-select>
                  </el-form-item>
                </el-col>
                <el-col :span="24">
                  <el-form-item :label="t('pages.buyerPrices.listTitle')" prop="title">
                    <el-input v-model="createForm.title" maxlength="255" clearable />
                  </el-form-item>
                </el-col>
              </el-row>
            </el-form>
          </div>
        </div>
      </div>

      <template #footer>
        <div class="buyer-dialog-footer">
          <el-button :icon="Close" @click="createVisible = false">{{ t('common.cancel') }}</el-button>
          <el-button v-if="canCreate" type="primary" :icon="Check" :loading="createSaving" @click="submitCreate">
            {{ t('common.save') }}
          </el-button>
        </div>
      </template>
    </el-dialog>

    <el-dialog
      v-model="detailVisible"
      width="920px"
      top="4vh"
      destroy-on-close
      align-center
      class="buyer-price-dialog buyer-price-dialog--detail"
      :show-close="true"
    >
      <template #header>
        <div class="buyer-dialog-header">
          <div class="buyer-dialog-header__main">
            <h3 class="buyer-dialog-header__title">{{ t('pages.buyerPrices.detailDialogTitle') }}</h3>
            <p v-if="detailData" class="buyer-dialog-header__sub">
              {{ detailData.buyer_code || '—' }}
              <template v-if="detailData.currency"> · {{ detailData.currency }}</template>
            </p>
          </div>
        </div>
      </template>

      <div v-loading="detailLoading" class="buyer-dialog-body buyer-dialog-body--stack">
        <div v-if="detailData" class="buyer-dialog-panel">
          <div class="buyer-dialog-panel__head">
            <h4 class="buyer-dialog-panel__title">{{ t('pages.buyerPrices.detailGroupSummary') }}</h4>
          </div>
          <div class="buyer-dialog-panel__body">
            <el-descriptions :column="2" border size="small">
              <el-descriptions-item :label="t('pages.buyerPrices.buyerCode')">{{ detailData.buyer_code || '—' }}</el-descriptions-item>
              <el-descriptions-item :label="t('pages.buyerPrices.currency')">{{ detailData.currency || '—' }}</el-descriptions-item>
              <el-descriptions-item :label="t('pages.buyerPrices.listTitle')">{{ detailData.title || '—' }}</el-descriptions-item>
              <el-descriptions-item :label="t('pages.buyerPrices.period')">{{ formatPeriodLabel(detailData.period_label) }}</el-descriptions-item>
            </el-descriptions>

            <div class="buyer-summary-blocks">
              <div class="buyer-summary-block">
                <div class="buyer-summary-block__head">
                  <h5 class="buyer-summary-block__title">{{ t('pages.buyerPrices.itemList') }}</h5>
                  <span class="buyer-summary-block__count">{{ detailUniqueItems.length }}</span>
                </div>
                <ol v-if="detailUniqueItems.length" class="buyer-item-enum-list">
                  <li v-for="(item, idx) in detailUniqueItems" :key="`${idx}-${item}`">{{ item }}</li>
                </ol>
                <p v-else class="buyer-cell-empty">—</p>
              </div>

              <div class="buyer-summary-block">
                <div class="buyer-summary-block__head">
                  <h5 class="buyer-summary-block__title">{{ t('pages.buyerPrices.priceComponentsFilled') }}</h5>
                </div>
                <div v-if="detailFilledComponents.length" class="buyer-component-tags buyer-component-tags--detail">
                  <el-tag
                    v-for="comp in detailFilledComponents"
                    :key="comp"
                    size="small"
                    effect="plain"
                    type="info"
                  >
                    {{ comp }}
                  </el-tag>
                </div>
                <p v-else class="buyer-cell-empty">—</p>
              </div>
            </div>
          </div>
        </div>

        <div v-if="detailData" class="buyer-dialog-panel buyer-dialog-panel--sub">
          <div class="buyer-dialog-panel__head">
            <h4 class="buyer-dialog-panel__title">{{ t('pages.buyerPrices.detailGroupLines') }}</h4>
            <p class="buyer-dialog-panel__sub">
              {{ normalizeRows(detailData.rows).length }} {{ t('pages.buyerPrices.rows') }}
            </p>
          </div>
          <div class="buyer-dialog-panel__body">
            <p class="admin-scroll-hint mb-3">{{ t('pages.buyerPrices.scrollHint') }}</p>
            <div class="admin-table-scroll">
              <el-table
                :data="normalizeRows(detailData.rows)"
                border
                stripe
                size="small"
                class="admin-table"
                max-height="48vh"
                table-layout="auto"
              >
                <el-table-column type="index" :label="t('common.noLabel')" width="56" align="center" />
                <el-table-column prop="ITEM" label="ITEM" min-width="180" show-overflow-tooltip />
                <el-table-column prop="THICKNESS" label="THICKNESS" min-width="110" show-overflow-tooltip />
                <el-table-column prop="COLOR" label="COLOR" min-width="110" show-overflow-tooltip />
                <el-table-column prop="COLOR WHITE" label="COLOR WHITE" min-width="130" />
                <el-table-column prop="COLOR BLACK" label="+ COLOR BLACK" min-width="130" />
                <el-table-column prop="COLOR COLOR" label="+ COLOR" min-width="130" />
                <el-table-column prop="FLOURASENT" label="FLOURASENT" min-width="120" />
                <el-table-column prop="METALIC" label="METALIC" min-width="110" />
                <el-table-column prop="EMBOSS" label="EMBOSS" min-width="110" />
                <el-table-column prop="SPESIAL EMBOSS" label="SPESIAL EMBOSS" min-width="150" />
              </el-table>
            </div>
          </div>
        </div>
      </div>

      <template #footer>
        <div class="buyer-dialog-footer buyer-dialog-footer--single">
          <el-button type="primary" @click="detailVisible = false">{{ t('common.close') }}</el-button>
        </div>
      </template>
    </el-dialog>

    <!-- Drawer: master data (header + grid) -->
    <el-drawer
      v-model="masterDrawer"
      :size="drawerSize"
      destroy-on-close
      class="buyer-price-drawer"
      :show-close="true"
      @closed="onMasterClosed"
    >
      <template #header>
        <div class="buyer-drawer-header">
          <div class="buyer-drawer-header__main">
            <h3 class="buyer-drawer-header__title">{{ masterDrawerTitle }}</h3>
            <p class="buyer-drawer-header__sub">{{ t('pages.buyerPrices.drawerManageSub') }}</p>
          </div>
          <el-tag v-if="masterBuyerCode" type="primary" effect="plain" size="small">{{ masterBuyerCode }}</el-tag>
        </div>
      </template>

      <div v-loading="masterLoading" class="buyer-drawer-body">
        <div class="buyer-dialog-panel mb-4">
          <div class="buyer-dialog-panel__head">
            <h4 class="buyer-dialog-panel__title">{{ t('pages.buyerPrices.sectionHeader') }}</h4>
          </div>
          <div class="buyer-dialog-panel__body">
            <el-form label-position="top">
              <el-row :gutter="16">
                <el-col :xs="24" :sm="12">
                  <el-form-item :label="t('pages.buyerPrices.listTitle')">
                    <el-input v-model="headerForm.title" maxlength="255" clearable />
                  </el-form-item>
                </el-col>
                <el-col :xs="24" :sm="12">
                  <el-form-item :label="t('pages.buyerPrices.currency')">
                    <el-select v-model="headerForm.currency" class="w-full">
                      <el-option label="USD" value="USD" />
                      <el-option label="IDR" value="IDR" />
                      <el-option label="EUR" value="EUR" />
                    </el-select>
                  </el-form-item>
                </el-col>
                <el-col :span="24">
                  <el-form-item :label="t('pages.buyerPrices.periodLabel')">
                    <el-input v-model="headerForm.period_label" maxlength="255" clearable />
                  </el-form-item>
                </el-col>
                <el-col :xs="24" :sm="12">
                  <el-form-item :label="t('pages.buyerPrices.periodStart')">
                    <el-date-picker
                      v-model="headerForm.period_start"
                      type="date"
                      value-format="YYYY-MM-DD"
                      class="w-full"
                      clearable
                    />
                  </el-form-item>
                </el-col>
                <el-col :xs="24" :sm="12">
                  <el-form-item :label="t('pages.buyerPrices.periodEnd')">
                    <el-date-picker
                      v-model="headerForm.period_end"
                      type="date"
                      value-format="YYYY-MM-DD"
                      class="w-full"
                      clearable
                    />
                  </el-form-item>
                </el-col>
              </el-row>
            </el-form>
          </div>
        </div>

        <div class="buyer-dialog-panel buyer-dialog-panel--sub">
          <div class="buyer-dialog-panel__head buyer-dialog-panel__head--row">
            <div>
              <h4 class="buyer-dialog-panel__title">{{ t('pages.buyerPrices.sectionSheet') }}</h4>
              <p class="buyer-dialog-panel__sub">{{ sheetRows.length }} {{ t('pages.buyerPrices.rows') }}</p>
            </div>
            <el-tooltip placement="top" :show-after="200">
              <template #content>{{ t('pages.buyerPrices.pageHint') }}</template>
              <el-icon class="buyer-page-hint" :size="14" tabindex="0" :aria-label="t('pages.buyerPrices.pageHint')">
                <InfoFilled />
              </el-icon>
            </el-tooltip>
          </div>
          <div class="admin-action-bar buyer-sheet-action-bar">
            <p class="admin-action-bar__hint">{{ t('pages.buyerPrices.scrollHint') }}</p>
            <div class="admin-action-bar__buttons">
              <el-button @click="addSheetRow">{{ t('pages.buyerPrices.addRow') }}</el-button>
              <el-button v-if="canUpdate" type="primary" :loading="masterSaving" @click="saveMaster">
                {{ t('pages.buyerPrices.saveSheet') }}
              </el-button>
            </div>
          </div>
          <div class="buyer-dialog-panel__body buyer-dialog-panel__body--flush">
            <div class="admin-table-scroll">
              <el-table :data="sheetRows" border stripe size="small" class="admin-table" max-height="52vh" table-layout="auto">
          <el-table-column type="index" :label="t('common.noLabel')" width="52" align="center" fixed />
          <el-table-column label="ITEM" min-width="200" fixed>
            <template #default="{ row }">
              <el-select
                v-model="row.ITEM"
                filterable
                clearable
                :placeholder="t('pages.buyerPrices.materialPlaceholder')"
                class="w-full"
                size="small"
                @change="onItemChange(row)"
              >
                <el-option
                  v-for="item in masterItems"
                  :key="`${item.item_code}-${item.material_name}`"
                  :label="itemOptionLabel(item)"
                  :value="item.material_name || item.item_code || ''"
                />
              </el-select>
            </template>
          </el-table-column>
          <el-table-column label="THICKNESS" min-width="120">
            <template #default="{ row }">
              <el-input v-model="row.THICKNESS" size="small" disabled />
            </template>
          </el-table-column>
          <el-table-column label="COLOR" min-width="120">
            <template #default="{ row }">
              <el-input v-model="row.COLOR" size="small" disabled />
            </template>
          </el-table-column>
          <el-table-column label="COLOR WHITE (BASE)" min-width="150">
            <template #default="{ row }">
              <el-input-number
                v-model="row['COLOR WHITE']"
                size="small"
                :controls="false"
                :min="0"
                :precision="2"
                :step="0.01"
                class="w-full"
                placeholder="0"
              >
                <template #suffix>
                  <span class="buyer-price-currency-suffix">{{ headerForm.currency || 'USD' }}</span>
                </template>
              </el-input-number>
            </template>
          </el-table-column>
          <el-table-column label="+ COLOR BLACK" min-width="120">
            <template #default="{ row }">
              <el-input-number
                v-model="row['COLOR BLACK']"
                size="small"
                :controls="false"
                :min="0"
                :precision="2"
                :step="0.01"
                class="w-full"
                placeholder="0"
                @change="(val) => onAddonPriceChange(row, 'COLOR BLACK', val)"
              >
                <template #suffix>
                  <span class="buyer-price-currency-suffix">{{ headerForm.currency || 'USD' }}</span>
                </template>
              </el-input-number>
            </template>
          </el-table-column>
          <el-table-column label="+ COLOR" min-width="120">
            <template #default="{ row }">
              <el-input-number
                v-model="row['COLOR COLOR']"
                size="small"
                :controls="false"
                :min="0"
                :precision="2"
                :step="0.01"
                class="w-full"
                placeholder="0"
                @change="(val) => onAddonPriceChange(row, 'COLOR COLOR', val)"
              >
                <template #suffix>
                  <span class="buyer-price-currency-suffix">{{ headerForm.currency || 'USD' }}</span>
                </template>
              </el-input-number>
            </template>
          </el-table-column>
          <el-table-column label="+ FLOURASENT" min-width="120">
            <template #default="{ row }">
              <el-input-number
                v-model="row.FLOURASENT"
                size="small"
                :controls="false"
                :min="0"
                :precision="2"
                :step="0.01"
                class="w-full"
                placeholder="0"
                @change="(val) => onAddonPriceChange(row, 'FLOURASENT', val)"
              >
                <template #suffix>
                  <span class="buyer-price-currency-suffix">{{ headerForm.currency || 'USD' }}</span>
                </template>
              </el-input-number>
            </template>
          </el-table-column>
          <el-table-column label="+ METALIC" min-width="120">
            <template #default="{ row }">
              <el-input-number
                v-model="row.METALIC"
                size="small"
                :controls="false"
                :min="0"
                :precision="2"
                :step="0.01"
                class="w-full"
                placeholder="0"
                @change="(val) => onAddonPriceChange(row, 'METALIC', val)"
              >
                <template #suffix>
                  <span class="buyer-price-currency-suffix">{{ headerForm.currency || 'USD' }}</span>
                </template>
              </el-input-number>
            </template>
          </el-table-column>
          <el-table-column label="+ EMBOSS" min-width="120">
            <template #default="{ row }">
              <el-input-number
                v-model="row.EMBOSS"
                size="small"
                :controls="false"
                :min="0"
                :precision="2"
                :step="0.01"
                class="w-full"
                placeholder="0"
                @change="(val) => onAddonPriceChange(row, 'EMBOSS', val)"
              >
                <template #suffix>
                  <span class="buyer-price-currency-suffix">{{ headerForm.currency || 'USD' }}</span>
                </template>
              </el-input-number>
            </template>
          </el-table-column>
          <el-table-column label="+ SPESIAL EMBOSS" min-width="140">
            <template #default="{ row }">
              <el-input-number
                v-model="row['SPESIAL EMBOSS']"
                size="small"
                :controls="false"
                :min="0"
                :precision="2"
                :step="0.01"
                class="w-full"
                placeholder="0"
                @change="(val) => onAddonPriceChange(row, 'SPESIAL EMBOSS', val)"
              >
                <template #suffix>
                  <span class="buyer-price-currency-suffix">{{ headerForm.currency || 'USD' }}</span>
                </template>
              </el-input-number>
            </template>
          </el-table-column>
          <el-table-column :label="t('common.actions')" width="72" align="center" fixed="right">
            <template #default="{ $index }">
              <el-tooltip :content="t('pages.buyerPrices.removeRow')" placement="top">
                <el-button
                  link
                  type="danger"
                  size="small"
                  :icon="Delete"
                  :aria-label="t('pages.buyerPrices.removeRow')"
                  @click="removeSheetRow($index)"
                />
              </el-tooltip>
            </template>
          </el-table-column>
        </el-table>
            </div>
          </div>
        </div>
      </div>
    </el-drawer>
  </AdminSection>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { Delete, EditPen, Plus, Close, Check, View, Refresh, InfoFilled } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import AdminSection from '../../components/AdminSection.vue'
import {
  createBuyerPriceList,
  deleteBuyerPriceList,
  getBuyerPriceList,
  listBuyerPriceLists,
  listMasterItems,
  saveBuyerPriceSheet,
  toIsoDate,
  updateBuyerPriceList,
} from '../../api/client'
import { useModulePermission } from '../../composables/useModulePermission'

const { t } = useI18n()
const { canCreate, canUpdate, canDelete } = useModulePermission('buyerPrices')

const SHEET_COLUMNS = ['ITEM', 'THICKNESS', 'COLOR', 'COLOR WHITE', 'COLOR BLACK', 'COLOR COLOR', 'FLOURASENT', 'METALIC', 'EMBOSS', 'SPESIAL EMBOSS']

const rows = ref([])
const loading = ref(false)
const keyword = ref('')
const masterItems = ref([])
const detailVisible = ref(false)
const detailLoading = ref(false)
const detailData = ref(null)

const createVisible = ref(false)
const createSaving = ref(false)
const createFormRef = ref(null)
const createForm = reactive({
  buyer_code: '',
  title: '',
  currency: 'USD',
})
const createRules = computed(() => ({
  buyer_code: [{ required: true, message: t('pages.buyerPrices.ruleBuyerCode'), trigger: 'blur' }],
}))

const masterDrawer = ref(false)
const masterLoading = ref(false)
const masterSaving = ref(false)
const activeListId = ref(null)
const masterBuyerCode = ref('')

const headerForm = reactive({
  title: '',
  currency: 'USD',
  period_label: '',
  period_start: '',
  period_end: '',
})

const sheetRows = ref([])

const masterDrawerTitle = computed(() => {
  const code = masterBuyerCode.value || ''
  return code ? `${code} · ${t('pages.buyerPrices.masterDrawerTitle')}` : t('pages.buyerPrices.masterDrawerTitle')
})

const filteredRows = computed(() => {
  const k = keyword.value.trim().toLowerCase()
  if (!k) return rows.value
  return rows.value.filter((r) => {
    const hay = [r.buyer_code, r.title, r.period_label, r.currency]
      .filter(Boolean)
      .join(' ')
      .toLowerCase()
    return hay.includes(k)
  })
})

const listStats = computed(() => ({
  total: rows.value.length,
  shown: filteredRows.value.length,
}))

const detailUniqueItems = computed(() => extractUniqueItems(detailData.value?.rows))

const detailFilledComponents = computed(() => extractFilledComponents(detailData.value?.rows))

function formatPeriodLabel(label) {
  const text = String(label || '').trim()
  if (!text) return '—'
  return text.replace(/,+\s*$/g, '').trim() || '—'
}

function normalizeRows(dataRows) {
  return (dataRows || []).map((r) => {
    const o = {}
    for (const k of SHEET_COLUMNS) {
      const v = r && typeof r === 'object' ? r[k] : undefined
      if (v == null || v === '') {
        o[k] = ''
      } else if (isPriceColumn(k)) {
        const num = Number(v)
        o[k] = Number.isFinite(num) ? num : ''
      } else {
        o[k] = String(v)
      }
    }
    return o
  })
}

function createEmptyRow() {
  const o = {}
  SHEET_COLUMNS.forEach((k) => {
    o[k] = isPriceColumn(k) ? null : ''
  })
  return o
}

const PRICE_COLUMNS = new Set(['COLOR WHITE', 'COLOR BLACK', 'COLOR COLOR', 'FLOURASENT', 'METALIC', 'EMBOSS', 'SPESIAL EMBOSS'])

function isPriceColumn(key) {
  return PRICE_COLUMNS.has(String(key || '').trim().toUpperCase())
}

function parseNumber(val) {
  if (val == null || val === '') return null
  const n = Number(val)
  return Number.isFinite(n) ? n : null
}

function extractUniqueItems(dataRows) {
  const seen = new Set()
  const out = []
  for (const row of dataRows || []) {
    const code = String(row?.ITEM || '').trim()
    if (!code || seen.has(code)) continue
    seen.add(code)
    out.push(code)
  }
  return out
}

function extractFilledComponents(dataRows) {
  const keys = ['COLOR WHITE', 'COLOR BLACK', 'COLOR COLOR', 'FLOURASENT', 'METALIC', 'EMBOSS', 'SPESIAL EMBOSS']
  const out = []
  for (const key of keys) {
    const hasValue = (dataRows || []).some((row) => {
      const v = row?.[key]
      if (v == null || v === '') return false
      const n = Number(v)
      return Number.isFinite(n) && n > 0
    })
    if (hasValue) out.push(key === 'COLOR COLOR' ? '+ COLOR' : key)
  }
  return out
}

function formatPopupNumber(val) {
  return Number(val).toLocaleString('id-ID', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })
}

function onAddonPriceChange(row, addonKey, addonValue) {
  const addon = parseNumber(addonValue)
  if (addon == null) return
  const base = parseNumber(row['COLOR WHITE'])
  if (base == null) {
    ElMessage.warning(t('pages.buyerPrices.popupNeedBase'))
    return
  }
  const total = base + addon
  ElMessage.info(
    t('pages.buyerPrices.popupAddonTotal', {
      addon: addonKey,
      value: formatPopupNumber(addon),
      total: formatPopupNumber(total),
    }),
  )
}

function onItemChange(row) {
  const selected = masterItems.value.find((i) => (i.material_name || '') === row.ITEM)
  if (selected) {
    row.THICKNESS = selected.thickness_range || ''
    const suggestions = colorSuggestionsFromItem(selected)
    row.COLOR = suggestions[0] || selected.color_standard || selected.color_reference || selected.color || ''
  }
}

function itemOptionLabel(item) {
  return item.material_name || item.item_code || '-'
}

function colorSuggestionsFromItem(item) {
  const src = [item?.color_standard, item?.color_reference]
    .filter(Boolean)
    .join(',')
  const out = []
  for (const raw of src.split(/[,/;|]/)) {
    const v = String(raw || '').trim()
    if (v && !out.includes(v)) out.push(v)
  }
  return out
}

function queryColorSuggestions(row, queryString, cb) {
  const selected = masterItems.value.find((i) => (i.material_name || '') === row.ITEM)
  const options = selected ? colorSuggestionsFromItem(selected) : []
  const q = (queryString || '').trim().toLowerCase()
  cb(options.filter((x) => !q || x.toLowerCase().includes(q)).slice(0, 12).map((x) => ({ value: x })))
}

function resetCreateForm() {
  createForm.buyer_code = ''
  createForm.title = ''
  createForm.currency = 'USD'
  headerForm.currency = 'USD'
}

function openCreateDialog() {
  resetCreateForm()
  createVisible.value = true
}

function emptyToNull(s) {
  const v = typeof s === 'string' ? s.trim() : s
  return v === '' || v == null ? null : v
}

async function submitCreate() {
  if (!createFormRef.value) return
  try {
    await createFormRef.value.validate()
  } catch {
    return
  }
  createSaving.value = true
  try {
    const created = await createBuyerPriceList({
      buyer_code: createForm.buyer_code.trim(),
      currency: createForm.currency || 'USD',
      title: emptyToNull(createForm.title),
    })
    ElMessage.success(t('pages.buyerPrices.saved'))
    createVisible.value = false
    await load()
    await openMaster(created.id)
  } catch (e) {
    const msg = e?.message || ''
    if (msg.includes('409') || msg.toLowerCase().includes('already')) {
      ElMessage.error(t('pages.buyerPrices.duplicateBuyer'))
    } else {
      ElMessage.error(msg || t('common.errorGeneric'))
    }
  } finally {
    createSaving.value = false
  }
}

function onMasterClosed() {
  activeListId.value = null
  masterBuyerCode.value = ''
  sheetRows.value = []
}

const drawerSize = computed(() => {
  const w = window.innerWidth
  if (w < 768) return '100%'
  if (w < 1200) return '80%'
  return '90%'
})

async function openMaster(id) {
  activeListId.value = id
  masterDrawer.value = true
  masterLoading.value = true
  try {
    const d = await getBuyerPriceList(id)
    masterBuyerCode.value = d.buyer_code || ''
    headerForm.title = d.title || ''
    headerForm.currency = d.currency || 'USD'
    headerForm.period_label = d.period_label || ''
    headerForm.period_start = d.period_start || ''
    headerForm.period_end = d.period_end || ''
    sheetRows.value = normalizeRows(d.rows)
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
    masterDrawer.value = false
    masterLoading.value = false
    return
  }
  try {
    const items = await listMasterItems()
    masterItems.value = items || []
  } catch (e) {
    console.warn('Failed to load master items:', e)
    masterItems.value = []
  } finally {
    masterLoading.value = false
  }
}

async function openDetail(id) {
  detailVisible.value = true
  detailLoading.value = true
  try {
    detailData.value = await getBuyerPriceList(id)
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
    detailVisible.value = false
  } finally {
    detailLoading.value = false
  }
}

function addSheetRow() {
  sheetRows.value.push(createEmptyRow())
}

function removeSheetRow(index) {
  sheetRows.value.splice(index, 1)
}

async function saveMaster() {
  if (activeListId.value == null) return
  masterSaving.value = true
  try {
    await updateBuyerPriceList(activeListId.value, {
      title: emptyToNull(headerForm.title),
      currency: emptyToNull(headerForm.currency) || 'USD',
      period_label: emptyToNull(headerForm.period_label),
      period_start: toIsoDate(headerForm.period_start),
      period_end: toIsoDate(headerForm.period_end),
    })
    const rowsPayload = sheetRows.value.map((r) => {
      const o = {}
      SHEET_COLUMNS.forEach((k) => {
        o[k] = r[k] ?? ''
      })
      return o
    })
    await saveBuyerPriceSheet(activeListId.value, {
      column_keys: SHEET_COLUMNS,
      rows: rowsPayload,
    })
    ElMessage.success(t('pages.buyerPrices.sheetSaved'))
    await load()
    await openMaster(activeListId.value)
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  } finally {
    masterSaving.value = false
  }
}

async function load() {
  loading.value = true
  try {
    rows.value = await listBuyerPriceLists()
  } finally {
    loading.value = false
  }
}

async function confirmDelete(row) {
  try {
    await ElMessageBox.confirm(t('pages.buyerPrices.confirmDelete'), t('common.confirm'), {
      type: 'warning',
    })
    await deleteBuyerPriceList(row.id)
    ElMessage.success(t('common.deleteSuccess'))
    await load()
    if (activeListId.value === row.id) {
      masterDrawer.value = false
    }
  } catch (e) {
    if (e !== 'cancel') ElMessage.error(e.message || t('common.errorGeneric'))
  }
}

onMounted(load)
</script>

<style scoped>
.buyer-inner-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
}

.buyer-page-hint {
  color: #94a3b8;
  cursor: help;
  flex-shrink: 0;
  outline: none;
}

.buyer-page-hint:hover,
.buyer-page-hint:focus-visible {
  color: var(--el-color-primary);
}

.buyer-price-stats {
  border-bottom: 1px solid #e2e8f0;
}

.buyer-price-table-wrap {
  padding: 0 16px 16px;
}

.buyer-price-row-actions {
  display: inline-flex;
  flex-wrap: nowrap;
  align-items: center;
  justify-content: center;
  gap: 2px;
}

.buyer-cell-empty {
  color: #94a3b8;
  font-size: 13px;
}

.buyer-item-cell {
  display: flex;
  align-items: center;
  gap: 6px;
  min-width: 0;
  cursor: help;
}

.buyer-item-cell__badge {
  flex-shrink: 0;
  min-width: 1.5rem;
  padding: 0 6px;
  border-radius: 999px;
  background: #e0f2fe;
  color: #0369a1;
  font-size: 11px;
  font-weight: 600;
  line-height: 1.6;
  text-align: center;
}

.buyer-item-cell__text {
  flex: 1;
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-size: 12px;
  color: #334155;
}

.buyer-item-cell__more {
  flex-shrink: 0;
  font-size: 11px;
  color: #64748b;
}

.buyer-item-tooltip__title {
  margin: 0 0 6px;
  font-size: 12px;
  font-weight: 600;
}

.buyer-item-tooltip__list {
  margin: 0;
  padding-left: 1.1rem;
  max-height: 240px;
  overflow-y: auto;
  font-size: 12px;
  line-height: 1.45;
}

.buyer-item-tooltip__list li + li {
  margin-top: 4px;
}

.buyer-component-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.buyer-component-tags--detail {
  gap: 6px;
}

.buyer-summary-blocks {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-top: 16px;
}

.buyer-summary-block {
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  background: #f8fafc;
  overflow: hidden;
}

.buyer-summary-block__head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  padding: 10px 12px;
  border-bottom: 1px solid #e2e8f0;
  background: #fff;
}

.buyer-summary-block__title {
  margin: 0;
  font-size: 12px;
  font-weight: 600;
  color: #0f172a;
}

.buyer-summary-block__count {
  flex-shrink: 0;
  min-width: 1.5rem;
  padding: 0 8px;
  border-radius: 999px;
  background: #e0f2fe;
  color: #0369a1;
  font-size: 11px;
  font-weight: 600;
  line-height: 1.7;
  text-align: center;
}

.buyer-item-enum-list {
  margin: 0;
  padding: 10px 12px 10px 2rem;
  max-height: 200px;
  overflow-y: auto;
  font-size: 12px;
  line-height: 1.5;
  color: #334155;
}

.buyer-item-enum-list li {
  word-break: break-word;
  overflow-wrap: anywhere;
}

.buyer-item-enum-list li + li {
  margin-top: 6px;
}

.buyer-item-enum-list li::marker {
  color: #64748b;
  font-weight: 600;
}

:deep(.buyer-price-dialog.el-dialog) {
  border-radius: 14px;
  overflow: hidden;
  max-height: 92vh;
  display: flex;
  flex-direction: column;
}

:deep(.buyer-price-dialog .el-dialog__header) {
  padding: 16px 20px 12px;
  margin: 0;
  border-bottom: 1px solid #e2e8f0;
}

:deep(.buyer-price-dialog .el-dialog__body) {
  padding: 0;
  background: #f8fafc;
  overflow-y: auto;
}

:deep(.buyer-price-dialog .el-dialog__footer) {
  padding: 12px 20px 16px;
  border-top: 1px solid #e2e8f0;
}

.buyer-dialog-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
  padding-right: 28px;
}

.buyer-dialog-header__title {
  margin: 0;
  font-size: 1.05rem;
  font-weight: 600;
  color: #0f172a;
  line-height: 1.3;
}

.buyer-dialog-header__sub {
  margin: 4px 0 0;
  font-size: 12px;
  color: #64748b;
  line-height: 1.45;
}

.buyer-dialog-body {
  padding: 16px;
}

.buyer-dialog-body--stack {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.buyer-dialog-panel {
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  background: #fff;
  overflow: hidden;
}

.buyer-dialog-panel--sub {
  background: #f8fafc;
}

.buyer-dialog-panel__head {
  padding: 12px 16px;
  border-bottom: 1px solid #e2e8f0;
  background: #f8fafc;
}

.buyer-dialog-panel__head--row {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
}

.buyer-dialog-panel__title {
  margin: 0;
  font-size: 0.9rem;
  font-weight: 600;
  color: #0f172a;
}

.buyer-dialog-panel__sub {
  margin: 4px 0 0;
  font-size: 12px;
  color: #64748b;
}

.buyer-dialog-panel__body {
  padding: 16px;
}

.buyer-dialog-panel__body--flush {
  padding: 0 0 16px;
}

.buyer-dialog-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  width: 100%;
}

.buyer-dialog-footer--single {
  justify-content: flex-end;
}

.buyer-drawer-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
  padding-right: 24px;
}

.buyer-drawer-header__title {
  margin: 0;
  font-size: 1rem;
  font-weight: 600;
  color: #0f172a;
}

.buyer-drawer-header__sub {
  margin: 4px 0 0;
  font-size: 12px;
  color: #64748b;
}

.buyer-drawer-body {
  padding: 0 4px 16px;
}

:deep(.buyer-price-drawer .el-drawer__header) {
  margin-bottom: 12px;
  padding-bottom: 12px;
  border-bottom: 1px solid #e2e8f0;
}

:deep(.buyer-price-drawer .el-drawer__body) {
  padding-top: 0;
}

.buyer-sheet-action-bar {
  margin: 0;
  border-radius: 0;
  border-bottom: 1px solid #e2e8f0;
}

.buyer-price-currency-suffix {
  display: inline-block;
  min-width: 2.5rem;
  text-align: right;
  font-size: 12px;
  color: #64748b;
}

@media (max-width: 768px) {
  :deep(.buyer-price-drawer.el-drawer) {
    width: 100% !important;
  }
}
</style>
