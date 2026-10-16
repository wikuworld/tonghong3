<template>
  <AdminSection :title="t('pages.mrpProses.title')" :subtitle="t('pages.mrpProses.subtitle')">
    <template #actions>
      <el-button :icon="Refresh" :loading="activeTab === 'return' ? returnLoading : loading" @click="refreshActiveTab">{{ t('common.refresh') }}</el-button>
      <el-button v-if="canCreate" type="danger" @click="openReject">{{ t('pages.mrpProses.rejectBtn') }}</el-button>
      <el-button v-if="canCreate" type="warning" @click="openReturn">{{ t('pages.mrpProses.returnBtn') }}</el-button>
      <el-button v-if="canCreate" type="primary" :icon="Plus" @click="openCreate">{{ t('common.create') }}</el-button>
    </template>

    <el-tabs v-model="activeTab" class="mrp-proses-tabs" @tab-change="onTabChange">
      <el-tab-pane :label="t('pages.mrpProses.tabProses')" name="proses" />
      <el-tab-pane :label="t('pages.mrpProses.tabReturn')" name="return" />
    </el-tabs>

    <div v-show="activeTab === 'proses'" class="admin-inner-card">
      <el-table
        :data="rows"
        v-loading="loading"
        border
        stripe
        size="small"
        class="admin-table"
        :empty-text="t('common.tableEmpty')"
        @sort-change="onSortChange"
      >
        <el-table-column type="index" width="56" :label="t('common.noLabel')" align="center">
          <template #default="{ $index }">{{ (page - 1) * pageSize + $index + 1 }}</template>
        </el-table-column>
        <el-table-column prop="kode_proses" :label="t('pages.mrpProses.kodeProses')" min-width="130" show-overflow-tooltip sortable="custom" />
        <el-table-column prop="kode_rencana" :label="t('pages.mrpProses.kodeRpi')" min-width="120" show-overflow-tooltip />
        <el-table-column prop="kode_wip" label="WIP" min-width="120" show-overflow-tooltip />
        <el-table-column prop="no_po" :label="t('pages.mrpRencana.poCustomerRef')" width="110" show-overflow-tooltip />
        <el-table-column prop="no_so" :label="t('pages.mrpRencana.soRef')" min-width="120" show-overflow-tooltip />
        <el-table-column :label="t('common.color')" width="110" show-overflow-tooltip>
          <template #default="{ row }">{{ dash(row.warna) }}</template>
        </el-table-column>
        <el-table-column :label="t('pages.mrpProses.thickness')" width="90">
          <template #default="{ row }">{{ dash(row.tebal) }}</template>
        </el-table-column>
        <el-table-column :label="t('pages.mrpProses.treatmentJenis')" width="90">
          <template #default="{ row }">{{ dash(row.treatment_jenis) }}</template>
        </el-table-column>
        <el-table-column prop="status" :label="t('common.status')" width="110" align="center" sortable="custom">
          <template #default="{ row }">
            <el-tag :type="statusType(row.status)" size="small" effect="plain">
              {{ statusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column :label="t('pages.mrpProses.checkpointStatus')" min-width="150" show-overflow-tooltip>
          <template #default="{ row }">
            <el-tag v-if="row.checkpoint_status" size="small" effect="plain">
              {{ row.checkpoint_status }}
            </el-tag>
            <span v-else class="text-gray-400">—</span>
          </template>
        </el-table-column>
        <el-table-column :label="t('pages.mrpProses.totalSize')" width="100" align="right">
          <template #default="{ row }">{{ formatQty(row.total_size) }}</template>
        </el-table-column>
        <el-table-column :label="t('common.actions')" width="88" align="center" fixed="right">
          <template #default="{ row }">
            <AdminTableActions :show-view="true" @view="goDetail(row.id)" />
          </template>
        </el-table-column>
      </el-table>
      <div class="mt-3 flex justify-end">
        <el-pagination
          v-model:current-page="page"
          v-model:page-size="pageSize"
          :total="total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next"
          background
          small
          @current-change="reload"
          @size-change="() => { page = 1; reload() }"
        />
      </div>
    </div>

    <div v-show="activeTab === 'return'" class="admin-inner-card">
      <el-table
        :data="returnRows"
        v-loading="returnLoading"
        border
        stripe
        size="small"
        class="admin-table"
        :empty-text="t('common.tableEmpty')"
        @sort-change="onReturnSortChange"
      >
        <el-table-column type="index" width="56" :label="t('common.noLabel')" align="center">
          <template #default="{ $index }">{{ (returnPage - 1) * returnPageSize + $index + 1 }}</template>
        </el-table-column>
        <el-table-column prop="kode_wip" label="WIP" min-width="130" show-overflow-tooltip sortable="custom" />
        <el-table-column prop="kode_palet" :label="t('pages.mrpProses.returnKyLama')" min-width="110" show-overflow-tooltip />
        <el-table-column prop="kode_yl_lama" :label="t('pages.mrpProses.returnYlLama')" min-width="120" show-overflow-tooltip />
        <el-table-column prop="kode_yl_baru" :label="t('pages.mrpProses.returnYlBaru')" min-width="120" show-overflow-tooltip />
        <el-table-column :label="t('pages.mrpProses.returnQty')" width="100" align="right">
          <template #default="{ row }">{{ formatQty(row.return_qty) }}</template>
        </el-table-column>
        <el-table-column :label="t('pages.mrpProses.treatmentList')" min-width="160" show-overflow-tooltip>
          <template #default="{ row }">{{ dash(row.treatment_list) }}</template>
        </el-table-column>
        <el-table-column prop="created_at" :label="t('common.date')" min-width="140" show-overflow-tooltip />
        <el-table-column :label="t('common.actions')" width="120" align="center" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="openReturnLabel(row.id)">
              {{ t('pages.mrpProses.returnLabelPrint') }}
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      <div class="mt-3 flex justify-end">
        <el-pagination
          v-model:current-page="returnPage"
          v-model:page-size="returnPageSize"
          :total="returnTotal"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next"
          background
          small
          @current-change="reloadReturn"
          @size-change="() => { returnPage = 1; reloadReturn() }"
        />
      </div>
    </div>

    <el-dialog
      v-model="rejectOpen"
      :title="t('pages.mrpProses.rejectTitle')"
      width="900px"
      destroy-on-close
      append-to-body
    >
      <p class="text-sm text-slate-500 mb-3">{{ t('pages.mrpProses.rejectHint') }}</p>
      <el-form label-position="top" @submit.prevent="lookupRejectWip">
        <el-form-item :label="t('pages.mrpProses.rejectWipInput')" required>
          <div class="flex gap-2 w-full">
            <el-input
              v-model="rejectForm.kode_wip"
              :placeholder="t('pages.mrpProses.rejectWipPlaceholder')"
              class="flex-1"
              @keyup.enter="lookupRejectWip"
            />
            <el-button :loading="rejectLookupLoading" @click="lookupRejectWip">
              {{ t('pages.mrpProses.rejectLookup') }}
            </el-button>
          </div>
        </el-form-item>
      </el-form>
      <div v-if="rejectLookupInfo" class="mrp-proses-scan-card mb-3">
        <span class="mrp-proses-scan-card__label">{{ t('common.detail') }}</span>
        <span class="mrp-proses-scan-card__value">
          {{ rejectLookupInfo.kode_proses }} · WIP {{ rejectLookupInfo.kode_wip }} ·
          {{ dash(rejectLookupInfo.kode_rencana) }}
        </span>
      </div>
      <div v-if="rejectLines.length" class="mrp-proses-section-title">{{ t('pages.mrpProses.rejectYlList') }}</div>
      <el-table
        v-if="rejectLines.length"
        :data="rejectLines"
        border
        stripe
        size="small"
        class="admin-table mb-3"
        :empty-text="t('common.tableEmpty')"
      >
        <el-table-column prop="kode_palet" :label="t('pages.mrpProses.returnKyLama')" min-width="110" />
        <el-table-column prop="kode_yl" :label="t('pages.mrpProses.ylCode')" min-width="110" />
        <el-table-column :label="t('pages.mrpProses.rejectSf')" width="100" align="right">
          <template #default="{ row }">{{ formatQty(row.reject_sf) }}</template>
        </el-table-column>
        <el-table-column :label="t('pages.mrpProses.rejectLembar')" width="100" align="right">
          <template #default="{ row }">{{ formatQty(row.lembar_qty) }}</template>
        </el-table-column>
      </el-table>
      <template #footer>
        <el-button @click="rejectOpen = false">{{ t('common.cancel') }}</el-button>
        <el-button
          type="primary"
          :loading="rejectSaving"
          :disabled="!rejectLines.length"
          @click="submitReject"
        >{{ t('common.save') }}</el-button>
      </template>
    </el-dialog>

    <el-dialog
      v-model="returnOpen"
      :title="t('pages.mrpProses.returnTitle')"
      width="900px"
      destroy-on-close
      append-to-body
    >
      <p class="text-sm text-slate-500 mb-3">{{ t('pages.mrpProses.returnHint') }}</p>
      <el-form label-position="top" @submit.prevent="lookupReturnWip">
        <el-form-item :label="t('pages.mrpProses.returnWipInput')" required>
          <div class="flex gap-2 w-full">
            <el-input
              v-model="returnForm.kode_wip"
              :placeholder="t('pages.mrpProses.returnWipPlaceholder')"
              class="flex-1"
              @keyup.enter="lookupReturnWip"
            />
            <el-button :loading="returnLookupLoading" @click="lookupReturnWip">
              {{ t('pages.mrpProses.returnLookup') }}
            </el-button>
          </div>
        </el-form-item>
      </el-form>
      <div v-if="returnLookupInfo" class="mrp-proses-scan-card mb-3">
        <span class="mrp-proses-scan-card__label">{{ t('common.detail') }}</span>
        <span class="mrp-proses-scan-card__value">
          {{ returnLookupInfo.kode_proses }} · WIP {{ returnLookupInfo.kode_wip }} ·
          {{ dash(returnLookupInfo.kode_rencana) }}
        </span>
      </div>
      <div v-if="returnLines.length" class="mrp-proses-section-title">{{ t('pages.mrpProses.returnYlList') }}</div>
      <el-table
        v-if="returnLines.length"
        :data="returnLines"
        border
        stripe
        size="small"
        class="admin-table mb-3"
        :empty-text="t('common.tableEmpty')"
      >
        <el-table-column prop="kode_palet" :label="t('pages.mrpProses.returnKyLama')" min-width="110" />
        <el-table-column prop="kode_yl" :label="t('pages.mrpProses.ylCode')" min-width="110" />
        <el-table-column :label="t('pages.mrpProses.returnMeasuredQty')" width="110" align="right">
          <template #default="{ row }">{{ formatQty(row.measured_qty) }}</template>
        </el-table-column>
        <el-table-column :label="t('pages.mrpProses.returnQty')" width="140" align="right">
          <template #default="{ row }">
            <el-input-number
              v-model="row.return_qty"
              :min="0.01"
              :max="row.max_return_qty"
              :step="1"
              :precision="2"
              controls-position="right"
              size="small"
              class="w-full"
            />
          </template>
        </el-table-column>
        <el-table-column prop="kode_yl_baru" :label="t('pages.mrpProses.returnYlBaru')" min-width="120" />
      </el-table>
      <template #footer>
        <el-button @click="returnOpen = false">{{ t('common.cancel') }}</el-button>
        <el-button
          type="primary"
          :loading="returnSaving"
          :disabled="!returnLines.length"
          @click="submitReturn"
        >{{ t('common.save') }}</el-button>
      </template>
    </el-dialog>

    <el-dialog
      v-model="returnLabelOpen"
      :title="t('pages.mrpProses.returnLabelTitle')"
      width="480px"
      destroy-on-close
      append-to-body
      class="mrp-proses-label-dialog"
    >
      <div v-loading="returnLabelLoading" class="mrp-proses-label-dialog__body">
        <div v-if="returnLabelPayload" class="mrp-proses-label-preview">
          <div class="mrp-proses-label-preview__card">
            <div class="mrp-proses-label-sheet">
              <div class="mrp-proses-label-sheet__head">
                <h3>{{ returnLabelPayload.title }}</h3>
                <img
                  v-if="returnLabelPayload.qrDataUrl"
                  :src="returnLabelPayload.qrDataUrl"
                  class="mrp-proses-label-sheet__qr"
                  :alt="dash(returnLabelPayload.r.kode_yl_baru)"
                />
              </div>
              <table class="mrp-proses-label-sheet__table">
                <tr><td>{{ t('pages.mrpProses.returnKyLama') }}</td><td><strong>{{ dash(returnLabelPayload.r.kode_palet) }}</strong></td></tr>
                <tr><td>{{ t('pages.mrpProses.returnYlLama') }}</td><td><strong>{{ dash(returnLabelPayload.r.kode_yl_lama) }}</strong></td></tr>
                <tr><td>{{ t('pages.mrpProses.returnYlBaru') }}</td><td><strong>{{ dash(returnLabelPayload.r.kode_yl_baru) }}</strong></td></tr>
                <tr><td>WIP</td><td><strong>{{ dash(returnLabelPayload.r.kode_wip) }}</strong></td></tr>
                <tr>
                  <td colspan="2" class="mrp-proses-label-sheet__tx">
                    <div class="mrp-proses-label-sheet__tx-title">{{ t('pages.mrpProses.treatmentList') }}</div>
                    <ul v-if="treatmentItems(returnLabelPayload.r.treatment_list).length" class="mrp-proses-label-sheet__tx-list">
                      <li v-for="(name, ti) in treatmentItems(returnLabelPayload.r.treatment_list)" :key="ti">
                        <span>{{ name }}</span>
                        <span class="mrp-proses-label-sheet__box" aria-hidden="true" />
                      </li>
                    </ul>
                    <div v-else class="mrp-proses-label-sheet__tx-empty">—</div>
                  </td>
                </tr>
                <tr><td>{{ t('pages.mrpProses.returnQty') }}</td><td><strong>{{ formatQty(returnLabelPayload.r.return_qty) }}</strong></td></tr>
                <tr><td>{{ t('common.date') }}</td><td>{{ dash(returnLabelPayload.tanggal) }}</td></tr>
              </table>
            </div>
          </div>
        </div>
      </div>
      <template #footer>
        <el-button @click="returnLabelOpen = false">{{ t('common.cancel') }}</el-button>
        <el-button type="primary" :loading="returnLabelPrinting" :disabled="!returnLabelPayload" @click="confirmPrintReturnLabel">
          {{ t('pages.mrpProses.returnLabelPrintAction') }}
        </el-button>
      </template>
    </el-dialog>

    <el-dialog
      v-model="createOpen"
      :title="t('pages.mrpProses.createTitle')"
      width="1280px"
      destroy-on-close
      append-to-body
      class="mrp-proses-create-dialog"
    >
      <div class="mrp-proses-create-layout">
        <div class="mrp-proses-create-layout__main">
          <p class="text-sm text-slate-500 mb-3">{{ t('pages.mrpProses.createHint') }}</p>
          <el-form label-position="top">
        <el-form-item :label="t('pages.mrpProses.treatmentJenis')" required>
          <el-radio-group v-model="form.treatment_jenis" @change="onTreatmentJenisChange">
            <el-radio-button value="PU">PU</el-radio-button>
            <el-radio-button value="Suede">SUEDE</el-radio-button>
          </el-radio-group>
        </el-form-item>
          <div class="mrp-proses-wip-card mb-3">
            <span class="mrp-proses-wip-card__label">{{ t('pages.mrpProses.kodeWip') }}</span>
            <span class="mrp-proses-wip-card__value">{{ previewKodeWip || '—' }}</span>
            <span class="mrp-proses-wip-card__hint">{{ t('pages.mrpProses.kodeWipHint') }}</span>
          </div>
        <el-form-item :label="t('pages.mrpProses.scanRpi')">
          <div class="flex gap-2 w-full">
            <el-autocomplete
              v-model="form.kode_scan"
              :fetch-suggestions="fetchRpiSuggestions"
              :placeholder="t('pages.mrpProses.scanPlaceholder')"
              :trigger-on-focus="true"
              :debounce="250"
              clearable
              class="flex-1"
              value-key="kode_rencana_item"
              @select="onRpiPicked"
              @keyup.enter="doScan"
            >
              <template #default="{ item }">
                <span>{{ rpiListLabel(item) }}</span>
              </template>
            </el-autocomplete>
            <el-button @click="doScan">{{ t('pages.mrpProses.scan') }}</el-button>
          </div>
        </el-form-item>

        <template v-if="processRows.length">
          <div class="mrp-proses-section-title">{{ t('pages.mrpProses.processList') }}</div>
          <el-table
            :data="processRows"
            border
            stripe
            size="small"
            class="admin-table mb-3"
            :empty-text="t('common.tableEmpty')"
          >
            <el-table-column :label="t('pages.mrpProses.kodeRpi')" min-width="130" show-overflow-tooltip>
              <template #default="{ row }">{{ dash(row.kode_rencana_item) }}</template>
            </el-table-column>
            <el-table-column :label="t('common.material')" min-width="120" show-overflow-tooltip>
              <template #default="{ row }">{{ dash(row.material_name) }}</template>
            </el-table-column>
            <el-table-column :label="t('pages.mrpProses.thickness')" width="90">
              <template #default="{ row }">{{ dash(row.thickness) }}</template>
            </el-table-column>
            <el-table-column :label="t('common.color')" width="100" show-overflow-tooltip>
              <template #default="{ row }">{{ dash(row.color) }}</template>
            </el-table-column>
            <el-table-column label="Emboss" width="90" show-overflow-tooltip>
              <template #default="{ row }">{{ dash(row.emboss) }}</template>
            </el-table-column>
            <el-table-column :label="t('common.colorStandard')" min-width="110" show-overflow-tooltip>
              <template #default="{ row }">{{ dash(row.color_swatch) }}</template>
            </el-table-column>
            <el-table-column label="qty" width="80" align="right">
              <template #default="{ row }">{{ formatQty(row.qty) }}</template>
            </el-table-column>
            <el-table-column :label="t('pages.mrpProses.qtyProcess')" width="90" align="right">
              <template #default="{ row }">{{ formatQty(row.qty_proses) }}</template>
            </el-table-column>
            <el-table-column prop="no_po" :label="t('pages.mrpRencana.poCustomerRef')" width="110" show-overflow-tooltip />
            <el-table-column :label="t('common.actions')" width="88" align="center" fixed="right">
              <template #default="{ row }">
                <AdminTableActions :show-delete="true" @delete="removeProcessRow(row)" />
              </template>
            </el-table-column>
          </el-table>
        </template>

        <el-divider />

        <el-form-item :label="t('pages.mrpProses.kySourceLabel')" required>
          <el-radio-group v-model="kySource" @change="onKySourceChange">
            <el-radio-button value="crust">{{ t('pages.mrpProses.kySourceCrust') }}</el-radio-button>
            <el-radio-button value="mod">{{ t('pages.mrpProses.kySourceMod') }}</el-radio-button>
          </el-radio-group>
        </el-form-item>

        <template v-if="kySource === 'crust'">
        <el-form-item :label="t('pages.mrpProses.pilihKy')" required>
          <el-select
            v-model="selectedKy"
            filterable
            clearable
            class="w-full"
            :placeholder="t('pages.mrpProses.pilihKyPlaceholder')"
            @change="onKySelect"
          >
            <el-option v-for="k in paletOptionsForCreate" :key="k" :label="k" :value="k" />
          </el-select>
          <p v-if="!paletOptionsForCreate.length" class="text-sm text-amber-600 mt-1 mb-0">
            {{ t('pages.mrpProses.kyNoMatchFilter') }}
          </p>
          <p v-else-if="selectedKy && !kyCandidateRows.length" class="text-sm text-amber-600 mt-1 mb-0">
            {{ t('pages.mrpProses.kyNoYlStock') }}
          </p>
          <p v-else-if="selectedKy && kyCandidateRows.length && !processKyRows.length" class="text-sm text-slate-500 mt-1 mb-0">
            {{ t('pages.mrpProses.kyCheckMaterialHint') }}
          </p>
        </el-form-item>

        <template v-if="kyCandidateRows.length">
          <div class="mrp-proses-section-title flex items-center justify-between gap-2 flex-wrap">
            <span>{{ t('pages.mrpProses.kyCandidateList') }}</span>
            <div class="flex gap-2">
              <el-button size="small" link type="primary" @click="selectAllKyCandidates">
                {{ t('pages.mrpProses.kySelectAll') }}
              </el-button>
              <el-button size="small" link type="info" @click="clearKyCandidatesForPalet">
                {{ t('pages.mrpProses.kyClearPalet') }}
              </el-button>
            </div>
          </div>
          <el-table
            :data="kyCandidateRows"
            border
            stripe
            size="small"
            class="admin-table mb-3"
            :empty-text="t('common.tableEmpty')"
          >
            <el-table-column width="48" align="center">
              <template #default="{ row }">
                <el-checkbox
                  :model-value="isKyRowChecked(row)"
                  :disabled="!kyRowSelectable(row)"
                  @change="(val) => toggleKyRow(row, val)"
                />
              </template>
            </el-table-column>
            <el-table-column prop="kode_yl" :label="t('pages.mrpProses.ylCode')" min-width="110" show-overflow-tooltip />
            <el-table-column :label="t('pages.mrpProses.thickness')" width="90">
              <template #default="{ row }">{{ dash(row.thickness) }}</template>
            </el-table-column>
            <el-table-column :label="t('common.color')" width="100" show-overflow-tooltip>
              <template #default="{ row }">{{ dash(row.warna || row.color) }}</template>
            </el-table-column>
            <el-table-column :label="t('pages.mrpProses.kyAvailableQty')" width="100" align="right">
              <template #default="{ row }">{{ formatQty(row.stok_qty) }}</template>
            </el-table-column>
            <el-table-column :label="t('pages.mrpProses.kyReservedQty')" width="90" align="right">
              <template #default="{ row }">
                <span :class="row.reserved_qty > 0 ? 'text-amber-600' : 'text-slate-400'">
                  {{ formatQty(row.reserved_qty) }}
                </span>
              </template>
            </el-table-column>
          </el-table>
        </template>
        </template>

        <template v-else>
          <p v-if="!modCandidateRows.length" class="text-sm text-amber-600 mb-2">
            {{ t('pages.mrpProses.kyModEmpty') }}
          </p>
          <div v-else class="mrp-proses-section-title flex items-center justify-between gap-2 flex-wrap">
            <span>{{ t('pages.mrpProses.kyModList') }}</span>
            <el-button size="small" link type="primary" @click="selectAllModCandidates">
              {{ t('pages.mrpProses.kySelectAll') }}
            </el-button>
          </div>
          <el-table
            v-if="modCandidateRows.length"
            :data="modCandidateRows"
            border
            stripe
            size="small"
            class="admin-table mb-3"
            :empty-text="t('common.tableEmpty')"
          >
            <el-table-column width="48" align="center">
              <template #default="{ row }">
                <el-checkbox
                  :model-value="isKyRowChecked(row)"
                  @change="(val) => toggleKyRow(row, val)"
                />
              </template>
            </el-table-column>
            <el-table-column prop="kode_mod" :label="t('pages.mrpGudangMod.kodeMod')" min-width="140" show-overflow-tooltip />
            <el-table-column prop="kode_palet" :label="t('pages.mrpProses.returnKyLama')" min-width="110" show-overflow-tooltip />
            <el-table-column prop="kode_yl" :label="t('pages.mrpProses.ylCode')" min-width="100" show-overflow-tooltip />
            <el-table-column :label="t('pages.mrpProses.rejectSf')" width="90" align="right">
              <template #default="{ row }">{{ formatQty(row.stok_qty) }}</template>
            </el-table-column>
            <el-table-column :label="t('pages.mrpProses.rejectLembar')" width="100" align="right">
              <template #default="{ row }">{{ formatQty(row.lembar_qty) }}</template>
            </el-table-column>
          </el-table>
        </template>

        <template v-if="processKyRows.length">
          <div class="mrp-proses-section-title">{{ t('pages.mrpProses.processKyList') }}</div>
          <el-table
            :data="processKyRows"
            border
            stripe
            size="small"
            class="admin-table mb-3"
            :empty-text="t('common.tableEmpty')"
            :row-class-name="kyRowClassName"
          >
            <el-table-column
              v-if="kySource === 'mod'"
              prop="kode_mod"
              :label="t('pages.mrpGudangMod.kodeMod')"
              min-width="130"
              show-overflow-tooltip
            />
            <el-table-column prop="kode_palet" :label="t('pages.mrpPalet.kodePalet')" min-width="110" show-overflow-tooltip />
            <el-table-column prop="kode_yl" :label="t('pages.mrpProses.ylCode')" min-width="110" show-overflow-tooltip />
            <el-table-column :label="t('pages.mrpProses.thickness')" width="90">
              <template #default="{ row }">{{ dash(row.thickness) }}</template>
            </el-table-column>
            <el-table-column :label="t('common.color')" width="100" show-overflow-tooltip>
              <template #default="{ row }">{{ dash(row.warna || row.color) }}</template>
            </el-table-column>
            <el-table-column :label="kySource === 'mod' ? t('pages.mrpProses.rejectSf') : 'qty'" width="120" align="right">
              <template #default="{ row }">
                <el-input-number
                  v-if="!row.gudang_mod_id"
                  v-model="row.qty"
                  :min="0.01"
                  :max="row.stok_qty > 0 ? Number(row.stok_qty) : undefined"
                  :step="1"
                  :precision="2"
                  controls-position="right"
                  size="small"
                  class="w-full"
                />
                <span v-else>{{ formatQty(row.qty) }}</span>
              </template>
            </el-table-column>
            <el-table-column :label="t('pages.mrpProses.tidakAdaSisa')" width="110" align="center">
              <template #default="{ row }">
                <el-checkbox v-model="row.tidak_ada_sisa" />
              </template>
            </el-table-column>
            <el-table-column :label="t('pages.mrpProses.qtySisaPreview')" width="100" align="right">
              <template #default="{ row }">
                <span v-if="row.tidak_ada_sisa" class="text-slate-400">—</span>
                <span v-else>{{ formatQty(kySisaQty(row)) }}</span>
              </template>
            </el-table-column>
            <el-table-column :label="t('pages.mrpProses.hasilPengukuran')" min-width="120" show-overflow-tooltip>
              <template #default="{ row }">{{ dash(row.hasil_ukur) }}</template>
            </el-table-column>
            <el-table-column :label="t('common.actions')" width="136" align="center" fixed="right">
              <template #default="{ row }">
                <div class="admin-row-actions">
                  <el-tooltip :content="t('pages.mrpProses.prosesUkur')" placement="top">
                    <el-button
                      :icon="VideoPlay"
                      link
                      type="success"
                      :aria-label="t('pages.mrpProses.prosesUkur')"
                      @click="startProsesUkur(row)"
                    />
                  </el-tooltip>
                  <AdminTableActions
                    :show-view="!!row.ukur_rows?.length"
                    :show-delete="true"
                    :view-label="t('pages.mrpProses.ukurDetailTitle')"
                    @view="openKyUkurDetail(row)"
                    @delete="removeProcessKyRow(row)"
                  />
                </div>
              </template>
            </el-table-column>
          </el-table>
        </template>
        <el-form-item :label="t('pages.mrpProses.treatmentList')">
          <div class="mrp-proses-treatment-box">
            <template v-if="treatmentsFiltered.length">
              <el-checkbox-group v-model="form.treatment_list">
                <div
                  v-for="tr in treatmentsFiltered"
                  :key="tr.nama_treatment"
                  class="mrp-proses-treatment-item"
                >
                  <el-checkbox :label="tr.nama_treatment">{{ tr.nama_treatment }}</el-checkbox>
                </div>
              </el-checkbox-group>
            </template>
            <p v-else class="text-sm text-slate-400 mb-0">{{ t('pages.mrpProses.treatmentEmpty') }}</p>
          </div>
        </el-form-item>
          </el-form>
        </div>

        <MrpProsesUkurPanel
          :rows="activeUkurRows"
          :total-size="activeUkurTotalSize"
          :total-qty="activeUkurRows.length"
          :online="scaleOnline"
          :active="!!activeKyKey"
          :can-start="!!activeKyKey"
          :can-stop="scaleOnline && !!activeKyKey"
          :can-add="scaleOnline && !!activeKyKey"
          :can-print="false"
          :can-save="!!activeKyKey && activeUkurRows.length > 0"
          :can-delete="!!activeKyKey"
          :hint="ukurPanelHint"
          @start="panelStart"
          @stop="panelStop"
          @add="panelAddUkur"
          @save="saveKyUkur"
          @delete="panelDeleteUkur"
        />
      </div>

      <el-dialog
        v-model="kyUkurDetailOpen"
        :title="t('pages.mrpProses.ukurDetailTitle')"
        width="480px"
        destroy-on-close
        append-to-body
      >
        <p v-if="kyUkurDetailRow" class="text-sm text-slate-500 mb-3">
          {{ kyUkurDetailRow.kode_palet }} · {{ kyUkurDetailRow.kode_yl }}
        </p>
        <el-table :data="kyUkurDetailRow?.ukur_rows || []" border size="small" :empty-text="t('common.tableEmpty')">
          <el-table-column type="index" width="56" :label="t('common.noLabel')" align="center" />
          <el-table-column :label="t('pages.mrpProses.sizeUkur')" align="right">
            <template #default="{ row }">{{ formatQty(row.size_val) }}</template>
          </el-table-column>
          <el-table-column :label="t('common.actions')" width="88" align="center">
            <template #default="{ row }">
              <AdminTableActions :show-delete="true" @delete="deleteKyUkurDetailRow(row)" />
            </template>
          </el-table-column>
        </el-table>
      </el-dialog>
      <template #footer>
        <el-button @click="createOpen = false">{{ t('common.cancel') }}</el-button>
        <el-button
          type="primary"
          :loading="saving"
          :disabled="!canSaveCreate"
          @click="submit"
        >{{ t('common.save') }}</el-button>
      </template>
    </el-dialog>
  </AdminSection>
</template>

<script setup>
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Plus, Refresh, VideoPlay } from '@element-plus/icons-vue'
import QRCode from 'qrcode'
import AdminSection from '../../../components/AdminSection.vue'
import AdminTableActions from '../../../components/admin/AdminTableActions.vue'
import MrpProsesUkurPanel from './MrpProsesUkurPanel.vue'
import { can } from '../../../security/permissions'
import { buildPageParams, fromElSortChange, normalizePageResult } from '../../../utils/tableQuery'
import {
  mrpCreateProses,
  mrpCreateProsesReject,
  mrpCreateProsesReturn,
  mrpGetProses,
  mrpListMasterKulit,
  mrpListProses,
  mrpListGudangMod,
  mrpListProsesReturn,
  mrpListYl,
  mrpPaletYl,
  mrpProsesAction,
  mrpProsesNextWip,
  mrpProsesReturnLabel,
  mrpProsesRejectLookup,
  mrpProsesReturnLookup,
  mrpProsesRencanaSearch,
  mrpProsesScanRencana,
} from '../../../api/client'

const { t } = useI18n()
const router = useRouter()
const loading = ref(false)
const saving = ref(false)
const createOpen = ref(false)
const activeTab = ref('proses')
const rejectOpen = ref(false)
const rejectSaving = ref(false)
const rejectLookupLoading = ref(false)
const rejectForm = reactive({ kode_wip: '' })
const rejectLookupInfo = ref(null)
const rejectLines = ref([])
const returnOpen = ref(false)
const returnSaving = ref(false)
const returnLookupLoading = ref(false)
const returnLoading = ref(false)
const returnRows = ref([])
const returnPage = ref(1)
const returnPageSize = ref(20)
const returnTotal = ref(0)
const returnSortBy = ref('date_created')
const returnSortDir = ref('desc')
const returnForm = reactive({ kode_wip: '' })
const returnLookupInfo = ref(null)
const returnLines = ref([])
const returnLabelOpen = ref(false)
const returnLabelLoading = ref(false)
const returnLabelPrinting = ref(false)
const returnLabelPayload = ref(null)
const rows = ref([])
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)
const sortBy = ref('date_created')
const sortDir = ref('desc')
const rencanaItems = ref([])
const treatments = ref([])
const scanned = ref(null)
const candidateRows = ref([])
const processRows = ref([])
const ylStock = ref([])
const modStock = ref([])
const kySource = ref('crust')
const paletOptions = ref([])
const kulitMasterByCode = ref({})
const selectedKy = ref('')
const kyCandidateRows = ref([])
const processKyRows = ref([])
const activeKyKey = ref('')
const scaleOnline = ref(false)
const kyUkurDetailOpen = ref(false)
const kyUkurDetailRow = ref(null)
const previewKodeWip = ref('')
const canCreate = computed(() => can('mrpShopfloor', 'create'))
const canSaveCreate = computed(() => {
  if (!processKyRows.value.length) return false
  if (candidateRows.value.length && !processRows.value.length) return false
  return true
})
const ukurPanelHint = computed(() => {
  if (activeKyKey.value) {
    return scaleOnline.value
      ? t('pages.mrpProses.detailUkurEmpty')
      : t('pages.mrpProses.detailUkurHint')
  }
  if (!selectedKy.value) return t('pages.mrpProses.ukurNeedSelectKy')
  if (!processKyRows.value.length) return t('pages.mrpProses.ukurNeedCheckYl')
  return t('pages.mrpProses.ukurPickKyHint')
})

const activeKyRow = computed(() =>
  processKyRows.value.find((row) => kyRowKey(row) === activeKyKey.value) || null,
)
const activeUkurRows = computed(() => activeKyRow.value?.ukur_rows || [])
const activeUkurTotalSize = computed(() =>
  activeUkurRows.value.reduce((sum, row) => sum + (Number(row.size_val) || 0), 0),
)
const form = reactive({
  kode_scan: '',
  rencana_item_id: null,
  treatment_jenis: 'PU',
  treatment_list: [],
})

const treatmentsFiltered = computed(() =>
  treatments.value.filter((tr) => tr.jenis === form.treatment_jenis),
)

function normalizeProsesJenis(raw) {
  const s = String(raw || '').trim()
  if (/suede/i.test(s)) return 'SUEDE'
  return 'PU'
}

function kulitLeatherTypeForCode(code) {
  const k = kulitMasterByCode.value[String(code || '').trim()]
  if (!k) return ''
  const t = String(k.type ?? k.leather_type ?? '')
    .trim()
    .toUpperCase()
  if (t === 'SUEDE' || t === 'SUIDE') return 'SUEDE'
  if (t === 'PU') return 'PU'
  return ''
}

function ylMatchesTreatmentType(yl) {
  const want = normalizeProsesJenis(form.treatment_jenis)
  const kode = String(yl?.kode_yl || '').trim()
  const kUpper = kode.toUpperCase()
  if (want === 'SUEDE') return kUpper === 'SUEDE'
  if (kUpper === 'SUEDE') return false
  if (kUpper === 'PU') return true
  const lt = kulitLeatherTypeForCode(kode)
  if (lt === 'SUEDE') return false
  if (lt === 'PU') return true
  return kode.length > 0
}

function ylPassesProsesKyFilters(yl) {
  return ylMatchesTreatmentType(yl)
}

const paletOptionsForCreate = computed(() => {
  if (!createOpen.value) return paletOptions.value
  const codes = ylStock.value
    .filter((y) => Number(y.qty) > 0 && ylPassesProsesKyFilters(y))
    .map((y) => y.kode_palet)
    .filter(Boolean)
  return [...new Set(codes)].sort((a, b) => a.localeCompare(b, undefined, { numeric: true }))
})

function modRowAsYl(row) {
  return {
    kode_yl: row.kode_yl,
    thickness: row.yl_thickness ?? row.thickness,
    warna: row.yl_warna ?? row.warna,
  }
}

const modCandidateRows = computed(() => {
  if (!createOpen.value || kySource.value !== 'mod') return []
  return modStock.value
    .filter((m) => (m.status || 'in_stock') === 'in_stock')
    .filter((m) => ylPassesProsesKyFilters(modRowAsYl(m)))
    .map((m) => ({
      gudang_mod_id: m.id,
      kode_mod: m.kode_mod,
      kode_palet: m.kode_palet,
      kode_yl: m.kode_yl,
      thickness: m.yl_thickness,
      warna: m.yl_warna,
      stok_qty: Number(m.reject_qty) || 0,
      qty: Number(m.reject_qty) || 0,
      lembar_qty: Number(m.reject_lembar) || 0,
      source: 'mod',
    }))
})

function rowKey(row) {
  const itemId = row.rencana_item_id ?? 'item'
  const poKey = row.po_link_id ?? row.po_id ?? row.no_po ?? 'item'
  return `${itemId}:${poKey}`
}

function removeProcessRow(row) {
  removeProcessRowByKey(rowKey(row))
}

function removeProcessRowByKey(key) {
  processRows.value = processRows.value.filter((r) => rowKey(r) !== key)
  refreshKySelectionAfterFilter()
}

function kyRowKey(row) {
  if (row.gudang_mod_id) return `mod:${row.gudang_mod_id}`
  return `${row.kode_palet}:${row.kode_yl}`
}

function isKyRowChecked(row) {
  return processKyRows.value.some((r) => kyRowKey(r) === kyRowKey(row))
}

function kyRowSelectable(row) {
  return Number(row.stok_qty) > 0
}

function toggleKyRow(row, checked) {
  const key = kyRowKey(row)
  if (checked) {
    if (!kyRowSelectable(row)) return
    if (!processKyRows.value.some((r) => kyRowKey(r) === key)) {
      processKyRows.value.push({
        ...row,
        qty: Number(row.stok_qty) || Number(row.qty) || 0,
        tidak_ada_sisa: false,
        ukur_rows: [],
        hasil_ukur: '',
      })
    }
  } else {
    removeProcessKyRowByKey(key)
  }
}

function selectAllKyCandidates() {
  for (const row of kyCandidateRows.value) {
    if (kyRowSelectable(row) && !isKyRowChecked(row)) toggleKyRow(row, true)
  }
}

function selectAllModCandidates() {
  for (const row of modCandidateRows.value) {
    if (!isKyRowChecked(row)) toggleKyRow(row, true)
  }
}

function onKySourceChange() {
  selectedKy.value = ''
  kyCandidateRows.value = []
  processKyRows.value = []
  activeKyKey.value = ''
  scaleOnline.value = false
  if (kySource.value === 'mod') loadModStock()
}

async function loadModStock() {
  try {
    const data = await mrpListGudangMod(
      buildPageParams({
        page: 1,
        pageSize: 200,
        sortBy: 'date_created',
        sortDir: 'desc',
        extra: { status: 'in_stock' },
      }),
    )
    modStock.value = normalizePageResult(data, { page: 1, pageSize: 200 }).items
  } catch {
    modStock.value = []
  }
}

function clearKyCandidatesForPalet() {
  const palet = selectedKy.value
  if (!palet) return
  processKyRows.value = processKyRows.value.filter((r) => r.kode_palet !== palet)
  if (activeKyKey.value && !activeKyKey.value.startsWith(`${palet}:`)) {
    activeKyKey.value = ''
    scaleOnline.value = false
  }
}

function removeProcessKyRow(row) {
  removeProcessKyRowByKey(kyRowKey(row))
}

function removeProcessKyRowByKey(key) {
  processKyRows.value = processKyRows.value.filter((r) => kyRowKey(r) !== key)
  if (activeKyKey.value === key) {
    activeKyKey.value = ''
    scaleOnline.value = false
  }
}

function kyRowClassName({ row }) {
  return kyRowKey(row) === activeKyKey.value ? 'mrp-proses-ky-row--active' : ''
}

function startProsesUkur(row) {
  activeKyKey.value = kyRowKey(row)
  scaleOnline.value = false
  if (!row.ukur_rows) row.ukur_rows = []
}

function openKyUkurDetail(row) {
  kyUkurDetailRow.value = row
  kyUkurDetailOpen.value = true
}

function deleteKyUkurDetailRow(ukurRow) {
  if (!kyUkurDetailRow.value?.ukur_rows) return
  const key = ukurRow.key ?? ukurRow.id
  kyUkurDetailRow.value.ukur_rows = kyUkurDetailRow.value.ukur_rows.filter(
    (r) => (r.key ?? r.id) !== key,
  )
  refreshKyHasilUkur(kyUkurDetailRow.value)
  if (activeKyKey.value === kyRowKey(kyUkurDetailRow.value) && !kyUkurDetailRow.value.ukur_rows.length) {
    kyUkurDetailRow.value.hasil_ukur = ''
  }
}

function refreshKyHasilUkur(kyRow) {
  const rows = kyRow?.ukur_rows || []
  if (!rows.length) {
    kyRow.hasil_ukur = ''
    return
  }
  const total = rows.reduce((sum, r) => sum + (Number(r.size_val) || 0), 0)
  kyRow.hasil_ukur = `${formatQty(total)} (${rows.length})`
}

function buildKyCandidateRows(kodePalet, stockRows = ylStock.value) {
  const rows = Array.isArray(stockRows) ? stockRows : []
  return rows
    .filter((y) => y.kode_palet === kodePalet && ylPassesProsesKyFilters(y))
    .map((y) => {
      const stockQty = Number(y.qty) || 0
      const availableQty = Number(y.available_qty ?? y.qty) || 0
      const reservedQty = Number(y.reserved_qty ?? Math.max(stockQty - availableQty, 0)) || 0
      return {
        kode_palet: y.kode_palet,
        kode_yl: y.kode_yl,
        thickness: y.thickness,
        warna: y.warna,
        color: y.warna,
        stok_qty: availableQty,
        stock_qty: stockQty,
        reserved_qty: reservedQty,
        qty: availableQty,
      }
    })
}

function syncKyCandidatesFromStock(kodePalet, stockRows = ylStock.value) {
  kyCandidateRows.value = kodePalet ? buildKyCandidateRows(kodePalet, stockRows) : []
}

function refreshKySelectionAfterFilter() {
  processKyRows.value = processKyRows.value.filter((r) => ylPassesProsesKyFilters(r))
  if (selectedKy.value && !paletOptionsForCreate.value.includes(selectedKy.value)) {
    selectedKy.value = ''
    kyCandidateRows.value = []
    activeKyKey.value = ''
    scaleOnline.value = false
    return
  }
  if (selectedKy.value) syncKyCandidatesFromStock(selectedKy.value)
}

async function loadKulitMasterMap() {
  try {
    const all = []
    let pageNum = 1
    const pageSizeLoad = 200
    for (;;) {
      const data = await mrpListMasterKulit({
        page: pageNum,
        page_size: pageSizeLoad,
        sort_by: 'kode_kulit',
        sort_dir: 'asc',
      })
      const pageData = normalizePageResult(data, { page: pageNum, pageSize: pageSizeLoad })
      all.push(...pageData.items)
      if (!pageData.items.length || all.length >= pageData.total) break
      pageNum += 1
    }
    const map = {}
    for (const k of all) {
      const code = String(k.kode_kulit || '').trim()
      if (code) map[code] = k
    }
    kulitMasterByCode.value = map
  } catch {
    kulitMasterByCode.value = {}
  }
}

async function onKySelect(kodePalet) {
  selectedKy.value = kodePalet || ''
  kyCandidateRows.value = []
  if (!kodePalet) return
  try {
    const rows = await mrpPaletYl(kodePalet)
    const list = Array.isArray(rows) ? rows : []
    const others = ylStock.value.filter((y) => y.kode_palet !== kodePalet)
    ylStock.value = [...others, ...list]
    syncKyCandidatesFromStock(kodePalet, list)
  } catch {
    syncKyCandidatesFromStock(kodePalet)
  }
}

function formatRencanaDate(raw) {
  if (raw == null || raw === '') return ''
  const s = String(raw).trim()
  if (/^\d{4}-\d{2}-\d{2}/.test(s)) return s.slice(0, 10)
  const d = new Date(s)
  if (Number.isNaN(d.getTime())) return s
  return d.toISOString().slice(0, 10)
}

function rpiListLabel(it) {
  const rpi = (it.kode_rencana_item || '').trim()
  const nama = (it.nama_rencana || '').trim()
  const tanggal = formatRencanaDate(it.tanggal_rencana)
  return [rpi, nama, tanggal].filter(Boolean).join(' - ')
}

async function fetchRpiSuggestions(queryString, cb) {
  const q = (queryString || '').trim()
  try {
    const data = await mrpProsesRencanaSearch(q)
    cb(data.items || [])
  } catch {
    const needle = q.toLowerCase()
    const local = (rencanaItems.value || []).filter((it) => {
      if (!needle) return true
      const hay = [
        it.kode_rencana_item,
        it.kode_lot_wip,
        it.kode_rencana,
        it.nama_rencana,
      ]
        .map((x) => String(x || '').toLowerCase())
        .join(' ')
      return hay.includes(needle)
    })
    cb(local.slice(0, 30))
  }
}

function onRpiPicked(item) {
  const kode = (item?.kode_rencana_item || '').trim()
  if (!kode) return
  form.kode_scan = kode
  loadItemDetail(kode)
}

function resolveMaterialName(item, po = null) {
  const fromItem = (item?.material_name || '').trim()
  const fromPo = po
    ? (po.material_name || po.item_name || '').trim()
    : ''
  return fromItem || fromPo || (item?.kode_kulit || '').trim()
}

function buildCandidateRows(item, poList = []) {
  const meta = {
    rencana_item_id: item.id,
    kode_rencana_item: item.kode_rencana_item,
    kode_rencana: item.kode_rencana,
    nama_rencana: item.nama_rencana,
    thickness: item.thickness,
    color: item.color,
    emboss: item.emboss,
    color_swatch: item.color_swatch,
  }
  if (poList.length) {
    return poList.map((po) => ({
      ...meta,
      material_name: resolveMaterialName(item, po),
      po_link_id: po.po_link_id,
      po_id: po.po_id,
      no_po: po.no_po,
      item_name: po.item_name,
      qty: po.qty ?? po.qty_outstanding,
      qty_outstanding: po.qty_outstanding,
      qty_proses: po.qty_proses,
    }))
  }
  return [
    {
      ...meta,
      material_name: resolveMaterialName(item),
      po_link_id: null,
      po_id: null,
      no_po: '',
      qty: null,
      qty_proses: null,
    },
  ]
}

function applyScanResult(data) {
  scanned.value = data
  form.rencana_item_id = data.id ?? null
  candidateRows.value = buildCandidateRows(data, data.po_list || [])
  processRows.value = candidateRows.value.map((row) => ({ ...row }))
  refreshKySelectionAfterFilter()
}

function dash(v) {
  const s = (v == null ? '' : String(v)).trim()
  return s || '—'
}

function formatQty(v) {
  const n = Number(v)
  if (!Number.isFinite(n)) return '—'
  return Number.isInteger(n) ? String(n) : n.toLocaleString(undefined, { maximumFractionDigits: 2 })
}

function kySisaQty(row) {
  const target = Number(row?.qty) || 0
  const measured = (row?.ukur_rows || []).reduce((sum, u) => sum + (Number(u.size_val) || 0), 0)
  const sisa = target - measured
  return sisa > 0 ? sisa : 0
}

function statusType(status) {
  const s = String(status || '')
  if (s === 'completed' || s === 'saved') return 'success'
  if (s === 'started') return 'warning'
  if (s === 'draft') return 'info'
  return ''
}

function statusLabel(status) {
  const s = String(status || '')
  const map = {
    draft: t('pages.mrpProses.statusDraft'),
    started: t('pages.mrpProses.statusStarted'),
    saved: t('pages.mrpProses.statusSavedLegacy'),
    completed: t('pages.mrpProses.statusCompleted'),
  }
  return map[s] || s || '—'
}

function onTreatmentJenisChange() {
  const allowed = new Set(treatmentsFiltered.value.map((tr) => tr.nama_treatment))
  form.treatment_list = form.treatment_list.filter((name) => allowed.has(name))
  refreshKySelectionAfterFilter()
}

function onSortChange(payload) {
  const mapped = fromElSortChange(payload)
  sortBy.value = mapped.sortBy || 'date_created'
  sortDir.value = mapped.sortDir || 'desc'
  page.value = 1
  reload()
}

function onReturnSortChange(payload) {
  const mapped = fromElSortChange(payload)
  returnSortBy.value = mapped.sortBy || 'date_created'
  returnSortDir.value = mapped.sortDir || 'desc'
  returnPage.value = 1
  reloadReturn()
}

function onTabChange(name) {
  if (name === 'return' && !returnRows.value.length) reloadReturn()
}

function treatmentItems(raw) {
  if (!raw) return []
  if (Array.isArray(raw)) return raw.filter(Boolean)
  return String(raw)
    .split(',')
    .map((s) => s.trim())
    .filter(Boolean)
}

async function reloadReturn() {
  returnLoading.value = true
  try {
    const data = await mrpListProsesReturn(
      buildPageParams({
        page: returnPage.value,
        pageSize: returnPageSize.value,
        sortBy: returnSortBy.value,
        sortDir: returnSortDir.value,
      }),
    )
    const pageData = normalizePageResult(data, { page: returnPage.value, pageSize: returnPageSize.value })
    returnRows.value = pageData.items
    returnTotal.value = pageData.total
  } catch (e) {
    ElMessage.error(e.message || String(e))
  } finally {
    returnLoading.value = false
  }
}

function resetReturnForm() {
  returnForm.kode_wip = ''
  returnLookupInfo.value = null
  returnLines.value = []
}

function openReturn() {
  resetReturnForm()
  returnOpen.value = true
}

function resetRejectForm() {
  rejectForm.kode_wip = ''
  rejectLookupInfo.value = null
  rejectLines.value = []
}

function openReject() {
  resetRejectForm()
  rejectOpen.value = true
}

async function lookupRejectWip() {
  const wip = rejectForm.kode_wip.trim()
  if (!wip) return
  rejectLookupLoading.value = true
  try {
    const data = await mrpProsesRejectLookup(wip)
    rejectLookupInfo.value = data.persiapan || null
    rejectLines.value = (data.lines || []).map((row) => ({
      ...row,
      reject_sf: Number(row.reject_sf ?? row.reject_qty) || 0,
      lembar_qty: Number(row.lembar_qty) || 0,
    }))
    if (!rejectLines.value.length) {
      ElMessage.warning(t('pages.mrpProses.rejectNoLines'))
    }
  } catch (e) {
    rejectLookupInfo.value = null
    rejectLines.value = []
    ElMessage.error(e.message || String(e))
  } finally {
    rejectLookupLoading.value = false
  }
}

async function submitReject() {
  const wip = rejectForm.kode_wip.trim()
  if (!wip || !rejectLines.value.length) return
  const lines = rejectLines.value
    .filter((row) => Number(row.reject_sf) > 0)
    .map((row) => ({ ky_id: row.ky_id }))
  if (!lines.length) {
    ElMessage.warning(t('pages.mrpProses.rejectNoLines'))
    return
  }
  rejectSaving.value = true
  try {
    await mrpCreateProsesReject({ kode_wip: wip, lines })
    ElMessage.success(t('pages.mrpProses.rejectSaved'))
    rejectOpen.value = false
    router.push('/admin/mrp/gudang-mod')
  } catch (e) {
    ElMessage.error(e.message || String(e))
  } finally {
    rejectSaving.value = false
  }
}

async function lookupReturnWip() {
  const wip = returnForm.kode_wip.trim()
  if (!wip) return
  returnLookupLoading.value = true
  try {
    const data = await mrpProsesReturnLookup(wip)
    returnLookupInfo.value = data.persiapan || null
    returnLines.value = (data.lines || []).map((row) => ({
      ...row,
      max_return_qty: Number(row.return_qty) || Number(row.measured_qty) || 0,
      return_qty: Number(row.return_qty) || Number(row.measured_qty) || 0,
    }))
    if (!returnLines.value.length) {
      ElMessage.warning(t('pages.mrpProses.returnNoLines'))
    }
  } catch (e) {
    returnLookupInfo.value = null
    returnLines.value = []
    ElMessage.error(e.message || String(e))
  } finally {
    returnLookupLoading.value = false
  }
}

async function submitReturn() {
  const wip = returnForm.kode_wip.trim()
  if (!wip || !returnLines.value.length) return
  const lines = returnLines.value
    .filter((row) => Number(row.return_qty) > 0)
    .map((row) => ({ ky_id: row.ky_id, return_qty: Number(row.return_qty) }))
  if (!lines.length) {
    ElMessage.warning(t('pages.mrpProses.returnQtyInvalid'))
    return
  }
  returnSaving.value = true
  try {
    await mrpCreateProsesReturn({ kode_wip: wip, lines })
    ElMessage.success(t('pages.mrpProses.returnSaved'))
    returnOpen.value = false
    activeTab.value = 'return'
    await reloadReturn()
  } catch (e) {
    ElMessage.error(e.message || String(e))
  } finally {
    returnSaving.value = false
  }
}

function escHtml(v) {
  return String(v ?? '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
}

async function qrForCode(code) {
  if (!code) return ''
  try {
    return await QRCode.toDataURL(code, { width: 120, margin: 0, errorCorrectionLevel: 'M' })
  } catch {
    return ''
  }
}

function buildReturnLabelHtml(r, title, tanggal, qrDataUrl = '') {
  const txItems = treatmentItems(r.treatment_list)
  const txHtml = txItems.length
    ? `<ul class="tx-list">${txItems.map((name) => `<li><span>${escHtml(name)}</span><span class="tx-box"></span></li>`).join('')}</ul>`
    : '<div class="tx-empty">—</div>'
  const qrImg = qrDataUrl ? `<img class="label-qr" src="${qrDataUrl}" alt="${escHtml(r.kode_yl_baru)}" />` : ''
  return `<!DOCTYPE html>
<html lang="id"><head><meta charset="UTF-8"/>
<title>${escHtml(title)}</title>
<style>
  @page { size: 4in 4in; margin: 0; }
  body { font-family: Arial, sans-serif; margin: 0; padding: 8px; }
  .label { width: 4in; height: 4in; border: 2px solid #000; padding: 0.14in; background: #fff; margin: 0 auto; }
  .label-head { display: flex; justify-content: space-between; gap: 8px; margin-bottom: 4px; }
  .label-head h2 { margin: 0; font-size: 12px; flex: 1; }
  .label-qr { width: 0.72in; height: 0.72in; }
  table { width: 100%; border-collapse: collapse; font-size: 10px; }
  td { padding: 2px 0; vertical-align: top; }
  td:first-child:not([colspan]) { width: 38%; }
  .tx-title { font-weight: 700; margin-bottom: 2px; }
  .tx-list { list-style: none; margin: 0; padding: 0; }
  .tx-list li { display: flex; justify-content: space-between; padding: 1px 0; }
  .tx-box { width: 10px; height: 10px; border: 1px solid #000; display: inline-block; }
</style></head><body>
<div class="label">
  <div class="label-head"><h2>${escHtml(title)}</h2>${qrImg}</div>
  <table>
    <tr><td>KY lama</td><td><strong>${escHtml(r.kode_palet)}</strong></td></tr>
    <tr><td>Kode YL lama</td><td><strong>${escHtml(r.kode_yl_lama)}</strong></td></tr>
    <tr><td>Kode YL baru</td><td><strong>${escHtml(r.kode_yl_baru)}</strong></td></tr>
    <tr><td>WIP</td><td><strong>${escHtml(r.kode_wip)}</strong></td></tr>
    <tr><td colspan="2"><div class="tx-title">Daftar Treatment</div>${txHtml}</td></tr>
    <tr><td>Qty retur</td><td><strong>${escHtml(r.return_qty)}</strong></td></tr>
    <tr><td>Tanggal</td><td>${escHtml(tanggal)}</td></tr>
  </table>
</div>
</body></html>`
}

async function openReturnLabel(id) {
  returnLabelOpen.value = true
  returnLabelLoading.value = true
  returnLabelPayload.value = null
  try {
    const data = await mrpProsesReturnLabel(id)
    const r = data.return || {}
    const qrDataUrl = await qrForCode(r.kode_yl_baru || r.kode_wip)
    returnLabelPayload.value = {
      title: data.title || t('pages.mrpProses.returnLabelTitle'),
      r,
      tanggal: (r.created_at || '').slice(0, 10) || new Date().toISOString().slice(0, 10),
      qrDataUrl,
    }
  } catch (e) {
    ElMessage.error(e.message || String(e))
    returnLabelOpen.value = false
  } finally {
    returnLabelLoading.value = false
  }
}

function confirmPrintReturnLabel() {
  if (!returnLabelPayload.value) return
  returnLabelPrinting.value = true
  try {
    const { r, title, tanggal, qrDataUrl } = returnLabelPayload.value
    const html = buildReturnLabelHtml(r, title, tanggal, qrDataUrl)
    const win = window.open('', '_blank', 'width=520,height=640')
    if (!win) {
      ElMessage.warning(t('pages.mrpProses.popupBlocked'))
      return
    }
    win.document.write(html)
    win.document.close()
    win.focus()
    setTimeout(() => win.print(), 300)
  } finally {
    returnLabelPrinting.value = false
  }
}

function refreshActiveTab() {
  if (activeTab.value === 'return') reloadReturn()
  else reload()
}

async function reload() {
  loading.value = true
  try {
    const data = await mrpListProses(
      buildPageParams({
        page: page.value,
        pageSize: pageSize.value,
        sortBy: sortBy.value,
        sortDir: sortDir.value,
      }),
    )
    const pageData = normalizePageResult(data, { page: page.value, pageSize: pageSize.value })
    rows.value = pageData.items.length ? pageData.items : (data.persiapan_list || [])
    total.value = pageData.total || rows.value.length
    rencanaItems.value = data.rencana_items || []
    treatments.value = data.treatments || []
    paletOptions.value = data.palet_options || []
    try {
      const ylData = await mrpListYl({ pageSize: 200 })
      ylStock.value = normalizePageResult(ylData, { page: 1, pageSize: 200 }).items
      if (!paletOptions.value.length) {
        paletOptions.value = [...new Set(ylStock.value.map((y) => y.kode_palet).filter(Boolean))]
      }
    } catch {
      ylStock.value = []
    }
  } catch (e) {
    ElMessage.error(e.message || String(e))
  } finally {
    loading.value = false
  }
}

function resetCreateForm() {
  form.kode_scan = ''
  form.rencana_item_id = null
  form.treatment_jenis = 'PU'
  form.treatment_list = []
  scanned.value = null
  candidateRows.value = []
  processRows.value = []
  selectedKy.value = ''
  kyCandidateRows.value = []
  processKyRows.value = []
  activeKyKey.value = ''
  scaleOnline.value = false
  kyUkurDetailOpen.value = false
  kyUkurDetailRow.value = null
  previewKodeWip.value = ''
  kySource.value = 'crust'
  modStock.value = []
}

async function loadNextWipPreview() {
  try {
    const data = await mrpProsesNextWip()
    previewKodeWip.value = data.kode_wip || ''
  } catch {
    previewKodeWip.value = ''
  }
}

async function openCreate() {
  resetCreateForm()
  createOpen.value = true
  loadNextWipPreview()
  await loadKulitMasterMap()
  try {
    const ylData = await mrpListYl({ pageSize: 200 })
    ylStock.value = normalizePageResult(ylData, { page: 1, pageSize: 200 }).items
    if (!paletOptions.value.length) {
      paletOptions.value = [...new Set(ylStock.value.map((y) => y.kode_palet).filter(Boolean))]
    } else {
      // Segarkan opsi palet dari stok aktual (qty > 0).
      const fromStock = [...new Set(ylStock.value.filter((y) => Number(y.qty) > 0).map((y) => y.kode_palet).filter(Boolean))]
      if (fromStock.length) paletOptions.value = fromStock
    }
  } catch {
    /* pakai cache reload */
  }
  if (kySource.value === 'mod') await loadModStock()
}

async function loadItemDetail(kode) {
  if (!kode) {
    scanned.value = null
    candidateRows.value = []
    processRows.value = []
    return
  }
  try {
    const data = await mrpProsesScanRencana(kode)
    applyScanResult(data)
  } catch (e) {
    scanned.value = null
    candidateRows.value = []
    processRows.value = []
    ElMessage.error(e.message || String(e))
  }
}

async function doScan() {
  const kode = form.kode_scan.trim()
  if (!kode) return
  await loadItemDetail(kode)
}

function groupProcessRowsByItem(rows) {
  const groups = new Map()
  for (const row of rows) {
    const itemId = row.rencana_item_id
    if (!itemId) continue
    if (!groups.has(itemId)) groups.set(itemId, [])
    groups.get(itemId).push(row)
  }
  return groups
}

function panelStart() {
  if (!activeKyKey.value) {
    ElMessage.warning(t('pages.mrpProses.ukurPickKyHint'))
    return
  }
  scaleOnline.value = true
}

function panelStop() {
  scaleOnline.value = false
}

function panelAddUkur(size) {
  if (!activeKyRow.value) return
  if (!scaleOnline.value) {
    ElMessage.warning(t('pages.mrpProses.panelStartFirst'))
    return
  }
  const val = Number(size)
  if (!(val > 0)) {
    ElMessage.warning(t('pages.mrpProses.sizeUkur'))
    return
  }
  if (!activeKyRow.value.ukur_rows) activeKyRow.value.ukur_rows = []
  const measured = activeKyRow.value.ukur_rows.reduce(
    (sum, u) => sum + (Number(u.size_val) || 0),
    0,
  )
  const stok = Number(activeKyRow.value.stok_qty)
  if (Number.isFinite(stok) && stok > 0 && measured + val > stok + 1e-9) {
    ElMessage.warning(
      t('pages.mrpProses.ukurExceedStock', {
        total: formatQty(measured + val),
        stok: formatQty(stok),
      }),
    )
    return
  }
  activeKyRow.value.ukur_rows.push({ key: `${Date.now()}-${val}`, size_val: val })
}

function panelDeleteUkur(row) {
  if (!activeKyRow.value?.ukur_rows) return
  const key = row.key ?? row.id
  activeKyRow.value.ukur_rows = activeKyRow.value.ukur_rows.filter((r) => (r.key ?? r.id) !== key)
}

function saveKyUkur() {
  if (!activeKyRow.value) return
  if (!activeKyRow.value.ukur_rows?.length) {
    ElMessage.warning(t('pages.mrpProses.sizeUkur'))
    return
  }
  refreshKyHasilUkur(activeKyRow.value)
  scaleOnline.value = false
  ElMessage.success(t('common.saved'))
}

async function applyKyUkursToProses(persiapanId) {
  const rowsToProcess = processKyRows.value.filter(
    (r) => r.ukur_rows?.length || r.tidak_ada_sisa,
  )
  if (!rowsToProcess.length) return
  await mrpProsesAction(persiapanId, { action: 'start' })
  let detail = await mrpGetProses(persiapanId)
  for (const kyRow of rowsToProcess) {
    let session = detail.ky_sessions?.find(
      (s) => s.kode_palet === kyRow.kode_palet && s.kode_yl === kyRow.kode_yl,
    )
    if (!session?.id) continue
    if (session.status !== 'active') {
      await mrpProsesAction(persiapanId, { action: 'activate_ky', ky_id: session.id })
      detail = await mrpGetProses(persiapanId)
      session =
        detail.ky_sessions?.find((s) => s.id === session.id) ||
        detail.ky_sessions?.find(
          (s) => s.kode_palet === kyRow.kode_palet && s.kode_yl === kyRow.kode_yl,
        )
      if (!session?.id) continue
    }
    for (const u of kyRow.ukur_rows || []) {
      await mrpProsesAction(persiapanId, {
        action: 'add_ukur',
        ky_id: session.id,
        size_val: Number(u.size_val),
      })
    }
    if (kyRow.ukur_rows?.length) {
      await mrpProsesAction(persiapanId, {
        action: 'selesai_ky',
        ky_id: session.id,
        skip_spek_check: true,
      })
      detail = await mrpGetProses(persiapanId)
    }
  }
}

async function submit() {
  if (!processRows.value.length && !processKyRows.value.length) {
    ElMessage.warning(t('pages.mrpProses.processRequired'))
    return
  }
  if (candidateRows.value.length && !processRows.value.length) {
    ElMessage.warning(t('pages.mrpProses.poRequired'))
    return
  }
  if (!processKyRows.value.length) {
    ElMessage.warning(t('pages.mrpProses.kySelectRequired'))
    return
  }
  for (const row of processKyRows.value) {
    const qty = Number(row.qty)
    if (!Number.isFinite(qty) || qty <= 0) {
      ElMessage.warning(t('pages.mrpProses.kyQtyInvalid'))
      return
    }
    if (row.stok_qty != null && qty > Number(row.stok_qty)) {
      ElMessage.warning(t('pages.mrpProses.kyQtyExceed', { stok: formatQty(row.stok_qty) }))
      return
    }
    if (row.tidak_ada_sisa && !row.ukur_rows?.length) {
      ElMessage.warning(t('pages.mrpProses.tidakAdaSisaNeedUkur'))
      return
    }
  }
  const groups = groupProcessRowsByItem(processRows.value)
  if (processKyRows.value.length && groups.size > 1) {
    ElMessage.warning(t('pages.mrpProses.kySingleRpiOnly'))
    return
  }
  saving.value = true
  try {
    const kyLines = processKyRows.value.map((row) => {
      const line = {
        kode_palet: row.kode_palet,
        kode_yl: row.kode_yl,
        target_qty: Number(row.qty),
        tidak_ada_sisa: !!row.tidak_ada_sisa,
      }
      if (row.gudang_mod_id) line.gudang_mod_id = row.gudang_mod_id
      return line
    })
    const created = []
    if (groups.size) {
      for (const [itemId, itemRows] of groups) {
        const poIds = itemRows.map((row) => row.po_id).filter(Boolean)
        const first = itemRows[0]
        const res = await mrpCreateProses({
          rencana_item_id: itemId,
          kode_scan: first.kode_rencana_item || form.kode_scan,
          treatment_jenis: form.treatment_jenis,
          treatment_list: form.treatment_list,
          po_ids: poIds,
          // KY hanya dilampirkan bila 1 RPI (sudah divalidasi di atas).
          ky_lines: kyLines,
        })
        created.push(res)
      }
    } else {
      const itemId = form.rencana_item_id || scanned.value?.id
      if (!itemId) {
        ElMessage.warning(t('pages.mrpProses.scanRpi'))
        saving.value = false
        return
      }
      const res = await mrpCreateProses({
        rencana_item_id: itemId,
        kode_scan: form.kode_scan,
        treatment_jenis: form.treatment_jenis,
        treatment_list: form.treatment_list,
        po_ids: [],
        ky_lines: kyLines,
      })
      created.push(res)
    }
    const primaryId = created[0]?.id
    if (primaryId) {
      try {
        await applyKyUkursToProses(primaryId)
      } catch (ukurErr) {
        ElMessage.warning(
          `${t('common.saved')}: ${ukurErr.message || ukurErr}. ${t('pages.mrpProses.ukurApplyPartialHint')}`,
        )
        createOpen.value = false
        await reload()
        router.push(`/admin/mrp/proses/${primaryId}`)
        return
      }
    }
    ElMessage.success(t('common.saved'))
    createOpen.value = false
    await reload()
    if (created.length === 1) {
      router.push(`/admin/mrp/proses/${created[0].id}`)
    }
  } catch (e) {
    ElMessage.error(e.message || String(e))
  } finally {
    saving.value = false
  }
}

function goDetail(id) {
  router.push(`/admin/mrp/proses/${id}`)
}

onMounted(reload)
</script>

<style scoped>
.mrp-proses-wip-card {
  border: 1px solid var(--el-color-primary-light-7);
  border-radius: 8px;
  padding: 0.75rem 0.85rem;
  background: var(--el-color-primary-light-9);
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}
.mrp-proses-wip-card__label {
  font-size: 0.7rem;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: var(--el-text-color-secondary);
}
.mrp-proses-wip-card__value {
  font-size: 1.05rem;
  font-weight: 700;
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
  color: var(--el-color-primary);
}
.mrp-proses-wip-card__hint {
  font-size: 0.72rem;
  color: var(--el-text-color-secondary);
}
.mrp-proses-scan-card {
  border: 1px solid var(--el-border-color-lighter);
  border-radius: 8px;
  padding: 0.65rem 0.85rem;
  background: var(--el-fill-color-blank);
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
}
.mrp-proses-scan-card__label {
  font-size: 0.7rem;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: var(--el-text-color-secondary);
}
.mrp-proses-scan-card__value {
  font-size: 0.875rem;
  color: var(--el-text-color-primary);
}
.mrp-proses-section-title {
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--el-text-color-primary);
  margin-bottom: 0.5rem;
}
.mrp-proses-treatment-box {
  border: 1px solid var(--el-border-color-lighter);
  border-radius: 8px;
  padding: 0.65rem 0.85rem;
  max-height: 180px;
  overflow-y: auto;
  width: 100%;
}
.mrp-proses-treatment-item {
  margin-bottom: 0.35rem;
}
.mrp-proses-treatment-item:last-child {
  margin-bottom: 0;
}
.admin-row-actions {
  display: inline-flex;
  flex-wrap: nowrap;
  align-items: center;
  justify-content: center;
  gap: 2px;
}
.mrp-proses-create-layout {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 360px;
  gap: 1rem;
  align-items: start;
}
.mrp-proses-create-layout__main {
  min-width: 0;
  max-height: 72vh;
  overflow: auto;
  padding-right: 0.25rem;
}
@media (max-width: 1100px) {
  .mrp-proses-create-layout {
    grid-template-columns: 1fr;
  }
}
:deep(.mrp-proses-ky-row--active) {
  --el-table-tr-bg-color: var(--el-color-primary-light-9);
}
.mrp-proses-tabs {
  margin-bottom: 0.75rem;
}
.mrp-proses-label-sheet__table {
  width: 100%;
  border-collapse: collapse;
  font-size: 11px;
}
.mrp-proses-label-sheet__table td {
  padding: 2px 0;
  vertical-align: top;
}
.mrp-proses-label-sheet__tx-list {
  list-style: none;
  margin: 0;
  padding: 0;
}
.mrp-proses-label-sheet__tx-list li {
  display: flex;
  justify-content: space-between;
  gap: 6px;
  padding: 1px 0;
}
.mrp-proses-label-sheet__box {
  width: 10px;
  height: 10px;
  border: 1px solid #333;
  flex-shrink: 0;
}
.mrp-proses-label-preview__card {
  border: 1px dashed var(--el-border-color);
  padding: 8px;
  background: #fafafa;
}
.mrp-proses-label-sheet__head {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 8px;
  margin-bottom: 6px;
}
.mrp-proses-label-sheet__head h3 {
  margin: 0;
  font-size: 13px;
}
.mrp-proses-label-sheet__qr {
  width: 72px;
  height: 72px;
}
</style>
