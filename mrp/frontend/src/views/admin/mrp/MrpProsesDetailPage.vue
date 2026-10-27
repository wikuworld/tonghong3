<template>
  <AdminSection :title="title" :subtitle="t('pages.mrpProses.detailSubtitle')">
    <template #actions>
      <el-button @click="$router.push('/admin/mrp/proses')">{{ t('common.close') }}</el-button>
      <el-button :icon="Refresh" :loading="loading" @click="reload">{{ t('common.refresh') }}</el-button>
      <el-button v-if="canUpdate && persiapan?.status === 'draft'" type="primary" @click="act('start')">
        {{ t('pages.mrpProses.start') }}
      </el-button>
      <el-button
        v-if="canUpdate && persiapan?.status === 'started'"
        type="success"
        @click="act('save')"
      >
        {{ t('pages.mrpProses.finishSave') }}
      </el-button>
      <el-button
        v-if="canUpdate && isDone"
        type="warning"
        @click="reopenPersiapan"
      >
        {{ t('pages.mrpProses.reopen') }}
      </el-button>
      <el-button v-if="persiapan && isDone" @click="openLabelDialog">{{ t('pages.mrpProses.label') }}</el-button>
    </template>

    <div v-loading="loading" class="mrp-proses-detail-layout">
      <div class="mrp-proses-detail-layout__main space-y-4">
        <div v-if="persiapan" class="admin-inner-card mb-4">
          <div class="admin-inner-card__body">
            <div class="mrp-proses-flow mb-3">
              <span
                v-for="step in flowSteps"
                :key="step.key"
                class="mrp-proses-flow__step"
                :class="{
                  'is-done': step.done,
                  'is-current': step.current,
                }"
              >
                {{ step.label }}
              </span>
            </div>

            <div class="mrp-proses-stats">
              <div class="mrp-proses-stat">
                <span class="mrp-proses-stat__label">{{ t('pages.mrpProses.kodeProses') }}</span>
                <span class="mrp-proses-stat__value mrp-proses-stat__value--text">{{ dash(persiapan.kode_proses) }}</span>
              </div>
              <div class="mrp-proses-stat">
                <span class="mrp-proses-stat__label">{{ t('pages.mrpProses.kodeRpi') }}</span>
                <span class="mrp-proses-stat__value mrp-proses-stat__value--text">{{ dash(persiapan.kode_rencana) }}</span>
              </div>
              <div class="mrp-proses-stat">
                <span class="mrp-proses-stat__label">WIP</span>
                <span class="mrp-proses-stat__value mrp-proses-stat__value--text">{{ dash(persiapan.kode_wip) }}</span>
              </div>
              <div class="mrp-proses-stat">
                <span class="mrp-proses-stat__label">{{ t('pages.mrpRencana.poCustomerRef') }}</span>
                <span class="mrp-proses-stat__value mrp-proses-stat__value--text">{{ dash(persiapan.no_po) }}</span>
              </div>
              <div class="mrp-proses-stat">
                <span class="mrp-proses-stat__label">{{ t('pages.mrpRencana.soRef') }}</span>
                <span class="mrp-proses-stat__value mrp-proses-stat__value--text">{{ dash(persiapan.no_so) }}</span>
              </div>
              <div class="mrp-proses-stat">
                <span class="mrp-proses-stat__label">{{ t('common.status') }}</span>
                <span class="mrp-proses-stat__value">
                  <el-tag :type="statusType(persiapan.status)" size="small" effect="plain">
                    {{ statusLabel(persiapan.status) }}
                  </el-tag>
                </span>
              </div>
              <div class="mrp-proses-stat">
                <span class="mrp-proses-stat__label">{{ t('pages.mrpProses.checkpointStatus') }}</span>
                <span class="mrp-proses-stat__value">
                  <el-tag v-if="persiapan.checkpoint_status" size="small" effect="plain">
                    {{ persiapan.checkpoint_status }}
                  </el-tag>
                  <span v-else class="text-gray-400">—</span>
                </span>
              </div>
              <div class="mrp-proses-stat">
                <span class="mrp-proses-stat__label">{{ t('common.color') }}</span>
                <span class="mrp-proses-stat__value mrp-proses-stat__value--text">{{ dash(persiapan.warna) }}</span>
              </div>
              <div class="mrp-proses-stat">
                <span class="mrp-proses-stat__label">{{ t('pages.mrpProses.thickness') }}</span>
                <span class="mrp-proses-stat__value mrp-proses-stat__value--text">{{ dash(persiapan.tebal) }}</span>
              </div>
              <div class="mrp-proses-stat mrp-proses-stat--wide">
                <span class="mrp-proses-stat__label">{{ t('pages.mrpProses.treatmentList') }}</span>
                <span class="mrp-proses-stat__value mrp-proses-stat__value--text">
                  {{ dash(persiapan.treatment_jenis) }} — {{ dash(persiapan.treatment_list) }}
                </span>
              </div>
              <div class="mrp-proses-stat">
                <span class="mrp-proses-stat__label">{{ t('pages.mrpProses.totalSize') }}</span>
                <span class="mrp-proses-stat__value">{{ formatQty(persiapan.total_size) }}</span>
              </div>
            </div>

            <el-alert
              v-if="persiapan.status === 'draft'"
              class="mt-3"
              type="warning"
              :closable="false"
              show-icon
              :title="t('pages.mrpProses.startHint')"
            />
            <el-alert
              v-else-if="persiapan.status === 'started'"
              class="mt-3"
              type="info"
              :closable="false"
              show-icon
              :title="t('pages.mrpProses.kyHint')"
            />
            <el-alert
              v-else-if="isDone"
              class="mt-3"
              type="success"
              :closable="false"
              show-icon
              :title="t('pages.mrpProses.doneHint')"
              :description="canUpdate ? t('pages.mrpProses.reopenHint') : undefined"
            />
          </div>
        </div>

        <div
          v-if="canUpdate && persiapan?.status === 'started' && !activeKy"
          class="admin-inner-card mb-4"
        >
          <div class="admin-inner-card__head">
            <h3 class="admin-inner-card__title">{{ t('pages.mrpProses.addYlSameKyTitle') }}</h3>
            <p class="admin-inner-card__sub mb-0">{{ t('pages.mrpProses.addYlSameKyHint') }}</p>
          </div>
          <div class="admin-inner-card__body space-y-3">
            <template v-if="primaryPalet">
              <div class="mrp-proses-form-row">
                <el-form-item :label="t('pages.mrpPalet.kodePalet')" class="mb-0">
                  <el-input :model-value="primaryPalet" disabled style="min-width: 180px" />
                </el-form-item>
                <el-form-item :label="t('pages.mrpProses.ylCode')" class="mb-0">
                  <el-select
                    v-model="kyForm.kode_yl"
                    filterable
                    clearable
                    :placeholder="t('pages.mrpProses.ylCode')"
                    style="min-width: 180px"
                    @change="onYlChangeSame"
                  >
                    <el-option
                      v-for="y in ylRemainingOnPrimaryPalet"
                      :key="`${y.kode_palet}-${y.kode_yl}`"
                      :label="`${y.kode_yl} (${formatQty(y.qty)})`"
                      :value="y.kode_yl"
                    />
                  </el-select>
                </el-form-item>
                <el-form-item :label="t('pages.mrpProses.targetQty')" class="mb-0">
                  <el-input-number v-model="kyForm.target_qty" :min="0" :step="1" controls-position="right" />
                </el-form-item>
                <el-button
                  type="primary"
                  :loading="kyBusy"
                  :disabled="!canAddYlSamePalet"
                  @click="scanKySamePalet"
                >
                  {{ t('pages.mrpProses.activateKy') }}
                </el-button>
              </div>
              <p v-if="!ylRemainingOnPrimaryPalet.length" class="text-sm text-slate-500 mb-0">
                {{ t('pages.mrpProses.noRemainingYlOnPalet') }}
              </p>
            </template>
            <p v-else class="text-sm text-slate-500 mb-0">{{ t('pages.mrpProses.noPrimaryPaletYet') }}</p>

            <el-divider content-position="left">{{ t('pages.mrpProses.addOtherPaletDivider') }}</el-divider>
            <el-button
              v-if="!showOtherPaletForm"
              link
              type="primary"
              @click="openOtherPaletForm"
            >
              {{ t('pages.mrpProses.addOtherPaletTitle') }}
            </el-button>
            <div v-else class="mrp-proses-form-row">
              <el-form-item :label="t('pages.mrpProses.pilihKy')" class="mb-0">
                <el-select
                  v-model="otherKyForm.kode_palet"
                  filterable
                  clearable
                  :placeholder="t('pages.mrpProses.pilihKyPlaceholder')"
                  style="min-width: 180px"
                  @change="onOtherPaletChange"
                >
                  <el-option
                    v-for="p in otherPaletOptions"
                    :key="p"
                    :label="p"
                    :value="p"
                  />
                </el-select>
              </el-form-item>
              <el-form-item :label="t('pages.mrpProses.ylCode')" class="mb-0">
                <el-select
                  v-model="otherKyForm.kode_yl"
                  filterable
                  clearable
                  :disabled="!otherKyForm.kode_palet"
                  :placeholder="t('pages.mrpProses.ylCode')"
                  style="min-width: 180px"
                  @change="onOtherYlChange"
                >
                  <el-option
                    v-for="y in ylForOtherPalet"
                    :key="`${y.kode_palet}-${y.kode_yl}`"
                    :label="`${y.kode_yl} (${formatQty(y.qty)})`"
                    :value="y.kode_yl"
                  />
                </el-select>
              </el-form-item>
              <el-form-item :label="t('pages.mrpProses.targetQty')" class="mb-0">
                <el-input-number v-model="otherKyForm.target_qty" :min="0" :step="1" controls-position="right" />
              </el-form-item>
              <el-button
                type="primary"
                :loading="kyBusy"
                :disabled="!canAddOtherPalet"
                @click="scanKyOtherPalet"
              >
                {{ t('pages.mrpProses.activateKy') }}
              </el-button>
              <el-button link @click="showOtherPaletForm = false">{{ t('common.cancel') }}</el-button>
            </div>
          </div>
        </div>

        <div class="admin-inner-card mb-4">
          <div class="admin-inner-card__head">
            <h3 class="admin-inner-card__title">{{ t('pages.mrpProses.kySessions') }}</h3>
          </div>
          <el-table
            :data="kySessions"
            border
            stripe
            size="small"
            class="admin-table"
            :empty-text="t('common.tableEmpty')"
            :row-class-name="kyRowClassName"
          >
            <el-table-column prop="kode_palet" :label="t('pages.mrpPalet.kodePalet')" min-width="110" />
            <el-table-column prop="kode_yl" :label="t('common.material')" min-width="100" />
            <el-table-column :label="t('pages.mrpProses.targetQty')" width="90" align="right">
              <template #default="{ row }">{{ formatQty(row.target_qty) }}</template>
            </el-table-column>
            <el-table-column :label="t('pages.mrpProses.actualQty')" width="90" align="right">
              <template #default="{ row }">{{ formatQty(row.actual_qty) }}</template>
            </el-table-column>
            <el-table-column :label="t('pages.mrpProses.hasilPengukuran')" min-width="120" show-overflow-tooltip>
              <template #default="{ row }">{{ hasilForKy(row) }}</template>
            </el-table-column>
            <el-table-column :label="t('common.status')" width="110" align="center">
              <template #default="{ row }">
                <el-tag :type="kyStatusType(row.status)" size="small" effect="plain">
                  {{ kyStatusLabel(row.status) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column :label="t('common.actions')" width="240" align="center" fixed="right">
              <template #default="{ row }">
                <div class="mrp-proses-ky-actions">
                  <AdminTableActions
                    :show-view="!!ukursForKy(row).length"
                    :view-label="t('pages.mrpProses.ukurDetailTitle')"
                    @view="openKyUkurDetail(row)"
                  />
                  <el-button
                    v-if="canUpdate && persiapan?.status === 'started' && row.status === 'planned'"
                    size="small"
                    link
                    type="primary"
                    @click="activateKy(row)"
                  >
                    {{ t('pages.mrpProses.activateKy') }}
                  </el-button>
                  <el-button
                    v-if="canUpdate && persiapan?.status === 'started' && row.status === 'active'"
                    size="small"
                    link
                    type="primary"
                    @click="startUkurForKy(row)"
                  >
                    {{ t('pages.mrpProses.prosesUkur') }}
                  </el-button>
                  <el-button
                    v-if="canUpdate && persiapan?.status === 'started' && row.status === 'active'"
                    size="small"
                    link
                    type="success"
                    @click="finishKy(row)"
                  >
                    {{ t('pages.mrpProses.finishKy') }}
                  </el-button>
                  <el-button
                    v-if="canUpdate && persiapan?.status === 'started' && row.status === 'selesai'"
                    size="small"
                    link
                    type="warning"
                    @click="reopenKy(row)"
                  >
                    {{ t('pages.mrpProses.reopenKy') }}
                  </el-button>
                </div>
              </template>
            </el-table-column>
          </el-table>
        </div>

        <div v-if="rpiAllocations.length" class="admin-inner-card mb-4">
          <div class="admin-inner-card__head">
            <h3 class="admin-inner-card__title">{{ t('pages.mrpProses.rpiSoListTitle') }}</h3>
            <p class="admin-inner-card__sub mb-0">{{ t('pages.mrpProses.rpiSoListHint') }}</p>
          </div>
          <el-table
            :data="rpiAllocations"
            border
            stripe
            size="small"
            class="admin-table"
            :empty-text="t('common.tableEmpty')"
          >
            <el-table-column prop="no_so" :label="t('pages.mrpRencana.soRef')" min-width="120" show-overflow-tooltip />
            <el-table-column prop="lot_no" :label="t('common.lotNo')" min-width="140" show-overflow-tooltip>
              <template #default="{ row }">
                <span class="mrp-lot-badge">{{ row.lot_no || '—' }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="material_name" :label="t('pages.mrpRencana.material')" min-width="130" show-overflow-tooltip />
            <el-table-column prop="color" :label="t('pages.mrpRencana.color')" min-width="100" show-overflow-tooltip />
            <el-table-column prop="emboss" :label="t('pages.mrpRencana.emboss')" min-width="90" show-overflow-tooltip />
            <el-table-column :label="t('pages.mrpPacking.colQtyRpi')" width="100" align="right">
              <template #default="{ row }">{{ formatQty(row.qty_rpi) }}</template>
            </el-table-column>
            <el-table-column
              v-if="canUpdate"
              :label="t('common.actions')"
              width="120"
              align="center"
              fixed="right"
            >
              <template #default="{ row }">
                <el-button size="small" link type="primary" @click="openChangeLot(row)">
                  {{ t('pages.mrpProses.changeLotBtn') }}
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </div>

      <MrpProsesUkurPanel
        v-if="canUpdate && persiapan?.status === 'started'"
        class="mrp-proses-detail-layout__side"
        :rows="activeKyUkurs"
        :total-size="activeKyUkurTotal"
        :total-qty="activeKyUkurs.length"
        :online="scaleOnline"
        :active="!!activeKy"
        :can-start="!!activeKy"
        :can-stop="scaleOnline && !!activeKy"
        :can-add="scaleOnline && !!activeKy"
        :can-print="false"
        :can-save="!!activeKy && activeKyUkurs.length > 0"
        :can-delete="!!activeKy && scaleOnline"
        :hint="ukurPanelHint"
        @start="onPanelStart"
        @stop="scaleOnline = false"
        @add="panelAddUkur"
        @save="finishActiveKy"
        @delete="panelDeleteUkur"
      />
    </div>

    <el-dialog
      v-model="kyUkurDetailOpen"
      :title="t('pages.mrpProses.ukurDetailTitle')"
      width="520px"
      destroy-on-close
      append-to-body
    >
      <p v-if="kyUkurDetailRow" class="text-sm text-slate-500 mb-3">
        {{ kyUkurDetailRow.kode_palet }} · {{ kyUkurDetailRow.kode_yl }}
      </p>
      <el-table :data="kyUkurDetailList" border size="small" :empty-text="t('common.tableEmpty')">
        <el-table-column type="index" width="56" :label="t('common.noLabel')" align="center" />
        <el-table-column :label="t('pages.mrpProses.sizeUkur')" align="right">
          <template #default="{ row }">{{ formatQty(row.size_val) }}</template>
        </el-table-column>
        <el-table-column prop="created_at" :label="t('common.date')" min-width="140" />
        <el-table-column
          v-if="canUpdate && persiapan?.status === 'started'"
          :label="t('common.actions')"
          width="88"
          align="center"
        >
          <template #default="{ row }">
            <AdminTableActions :show-delete="true" @delete="deleteUkur(row.id)" />
          </template>
        </el-table-column>
      </el-table>
    </el-dialog>

    <el-dialog
      v-model="labelDialogOpen"
      :title="t('pages.mrpProses.labelPrintTitle')"
      width="560px"
      destroy-on-close
      append-to-body
      class="mrp-proses-label-dialog"
    >
      <div v-loading="labelLoading" class="mrp-proses-label-dialog__body">
        <el-form label-position="top" class="mb-3" @submit.prevent>
          <el-form-item :label="t('pages.mrpProses.labelQty')" required>
            <el-input-number
              v-model="labelQty"
              :min="1"
              :max="99"
              :step="1"
              controls-position="right"
            />
          </el-form-item>
        </el-form>

        <p class="text-sm text-slate-500 mb-2">{{ t('pages.mrpProses.labelPreviewHint', { n: labelQty }) }}</p>

        <div v-if="labelPayload" class="mrp-proses-label-preview">
          <div
            v-for="i in labelQty"
            :key="i"
            class="mrp-proses-label-preview__card"
          >
            <div class="mrp-proses-label-sheet">
              <div class="mrp-proses-label-sheet__head">
                <h3>{{ labelPayload.title }}</h3>
                <img
                  v-if="labelPayload.qrDataUrl"
                  :src="labelPayload.qrDataUrl"
                  class="mrp-proses-label-sheet__qr"
                  :alt="dash(labelPayload.p.kode_wip)"
                />
              </div>
              <table>
                <tr><td>Kode Proses</td><td><strong>{{ dash(labelPayload.p.kode_proses) }}</strong></td></tr>
                <tr><td>Kode WIP</td><td><strong>{{ dash(labelPayload.p.kode_wip) }}</strong></td></tr>
                <tr><td>Rencana</td><td>{{ dash(labelPayload.p.kode_rencana) }}</td></tr>
                <tr><td>{{ t('common.color') }}</td><td>{{ dash(labelPayload.p.warna) }}</td></tr>
                <tr><td>{{ t('pages.mrpProses.thickness') }}</td><td>{{ dash(labelPayload.p.tebal) }}</td></tr>
                <tr><td>Emboss</td><td>{{ dash(labelPayload.p.emboss) }}</td></tr>
                <tr><td>{{ t('pages.mrpProses.treatmentJenis') }}</td><td>{{ dash(labelPayload.p.treatment_jenis) }}</td></tr>
                <tr>
                  <td colspan="2" class="mrp-proses-label-sheet__tx">
                    <div class="mrp-proses-label-sheet__tx-title">{{ t('pages.mrpProses.treatmentList') }}</div>
                    <ul v-if="treatmentItems(labelPayload.p.treatment_list).length" class="mrp-proses-label-sheet__tx-list">
                      <li v-for="(name, ti) in treatmentItems(labelPayload.p.treatment_list)" :key="ti">
                        <span>{{ name }}</span>
                        <span class="mrp-proses-label-sheet__box" aria-hidden="true" />
                      </li>
                    </ul>
                    <div v-else class="mrp-proses-label-sheet__tx-empty">—</div>
                  </td>
                </tr>
                <tr><td>{{ t('pages.mrpProses.labelPcs') }}</td><td><strong>{{ formatQty(labelPayload.p.jml_pcs) }}</strong></td></tr>
                <tr><td>{{ t('pages.mrpProses.labelTotalQtySf') }}</td><td><strong>{{ formatQty(labelPayload.p.total_size) }}</strong></td></tr>
                <tr><td>{{ t('common.date') }}</td><td>{{ dash(labelPayload.tanggal) }}</td></tr>
              </table>
              <div class="mrp-proses-label-sheet__copy">{{ i }}/{{ labelQty }}</div>
            </div>
          </div>
        </div>
      </div>
      <template #footer>
        <el-button @click="labelDialogOpen = false">{{ t('common.cancel') }}</el-button>
        <el-button type="primary" :loading="labelPrinting" :disabled="!labelPayload || labelQty < 1" @click="confirmPrintLabels">
          {{ t('pages.mrpProses.labelPrintAction') }}
        </el-button>
      </template>
    </el-dialog>

    <el-dialog
      v-model="changeLotOpen"
      :title="t('pages.mrpProses.changeLotTitle')"
      width="920px"
      destroy-on-close
      append-to-body
    >
      <p class="text-sm text-slate-500 mb-3">{{ t('pages.mrpProses.changeLotHint') }}</p>
      <div v-if="changeLotRow" class="mrp-proses-change-lot-current mb-3">
        <span>{{ t('pages.mrpProses.changeLotCurrent') }}:</span>
        <strong>{{ dash(changeLotRow.no_so) }}</strong>
        <span>·</span>
        <strong>{{ dash(changeLotRow.lot_no) }}</strong>
        <span>·</span>
        <span>{{ t('pages.mrpPacking.colQtyRpi') }} {{ formatQty(changeLotRow.qty_rpi) }}</span>
      </div>
      <el-form v-loading="changeLotLoading" label-position="top">
        <el-form-item :label="t('pages.mrpProses.changeLotPickPo')" required>
          <el-input
            v-model="changeLotSearch"
            clearable
            size="small"
            class="mb-2"
            :placeholder="t('pages.mrpProses.changeLotSearch')"
            :disabled="!changeLotPoRows.length"
          />
          <el-table
            :data="filteredChangeLotPoRows"
            border
            stripe
            size="small"
            class="admin-table"
            row-key="id"
            highlight-current-row
            :current-row-key="changeLotSelectedPoId"
            max-height="360"
            :empty-text="changeLotPoRows.length ? t('common.tableEmpty') : t('pages.mrpGudangSisa.assignSoEmpty')"
            @current-change="onChangeLotPoSelect"
          >
            <el-table-column
              prop="lot_no"
              :label="t('common.lotNo')"
              min-width="150"
              show-overflow-tooltip
            />
            <el-table-column :label="t('pages.mrpRencana.soRef')" min-width="120" show-overflow-tooltip>
              <template #default="{ row }">{{ dash(row.no_so || row.no_po) }}</template>
            </el-table-column>
            <el-table-column prop="customer" :label="t('common.customer')" min-width="140" show-overflow-tooltip />
            <el-table-column prop="item_name" :label="t('common.material')" min-width="160" show-overflow-tooltip />
            <el-table-column prop="warna" :label="t('common.color')" min-width="110" show-overflow-tooltip />
            <el-table-column prop="emboss" :label="t('pages.mrpRencana.emboss')" width="90" show-overflow-tooltip />
            <el-table-column :label="t('pages.mrpRencana.qtyAllocatable')" width="110" align="right">
              <template #default="{ row }">{{ formatQty(row.qty_outstanding) }}</template>
            </el-table-column>
          </el-table>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="changeLotOpen = false">{{ t('common.cancel') }}</el-button>
        <el-button
          type="primary"
          :loading="changeLotSaving"
          :disabled="!changeLotSelectedPoId"
          @click="submitChangeLot"
        >
          {{ t('common.save') }}
        </el-button>
      </template>
    </el-dialog>
  </AdminSection>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Refresh } from '@element-plus/icons-vue'
import AdminSection from '../../../components/AdminSection.vue'
import AdminTableActions from '../../../components/admin/AdminTableActions.vue'
import MrpProsesUkurPanel from './MrpProsesUkurPanel.vue'
import { can } from '../../../security/permissions'
import {
  mrpGetProses,
  mrpListYl,
  mrpProsesAction,
  mrpProsesChangeLot,
  mrpProsesLabel,
  mrpRencanaItemListPo,
} from '../../../api/client'
import QRCode from 'qrcode'

const { t } = useI18n()
const route = useRoute()
const loading = ref(false)
const kyBusy = ref(false)
const persiapan = ref(null)
const kySessions = ref([])
const rpiAllocations = ref([])
const ukurs = ref([])
const changeLotOpen = ref(false)
const changeLotLoading = ref(false)
const changeLotSaving = ref(false)
const changeLotRow = ref(null)
const changeLotPoRows = ref([])
const changeLotSearch = ref('')
const changeLotSelectedPoId = ref(null)
const ylStock = ref([])
const scaleOnline = ref(false)
const kyUkurDetailOpen = ref(false)
const kyUkurDetailRow = ref(null)
const labelDialogOpen = ref(false)
const labelLoading = ref(false)
const labelPrinting = ref(false)
const labelQty = ref(1)
const labelPayload = ref(null)
const kyForm = reactive({
  kode_palet: '',
  kode_yl: '',
  target_qty: 0,
})
const otherKyForm = reactive({
  kode_palet: '',
  kode_yl: '',
  target_qty: 0,
})
const showOtherPaletForm = ref(false)

const canUpdate = computed(() => can('mrpShopfloor', 'update'))
const kyUkurDetailList = computed(() =>
  kyUkurDetailRow.value ? ukursForKy(kyUkurDetailRow.value) : [],
)
const title = computed(() => persiapan.value?.kode_proses || t('pages.mrpProses.title'))
const isDone = computed(() => ['saved', 'completed'].includes(persiapan.value?.status || ''))
const activeKy = computed(() => kySessions.value.find((s) => s.status === 'active') || null)
const activeKyUkurs = computed(() => (activeKy.value ? ukursForKy(activeKy.value) : []))
const activeKyUkurTotal = computed(() =>
  activeKyUkurs.value.reduce((sum, r) => sum + (Number(r.size_val) || 0), 0),
)
const usedYlKeys = computed(() => {
  const keys = new Set()
  for (const s of kySessions.value) {
    const p = (s.kode_palet || '').trim()
    const y = (s.kode_yl || '').trim()
    if (p && y) keys.add(`${p}:${y}`)
  }
  return keys
})
/** KY utama = palet yang sudah dipakai di proses (sesi pertama). */
const primaryPalet = computed(() => {
  const hit = kySessions.value.find((s) => (s.kode_palet || '').trim())
  return (hit?.kode_palet || '').trim()
})
const paletOptions = computed(() =>
  [...new Set(ylStock.value.map((y) => y.kode_palet).filter(Boolean))].sort(),
)
const otherPaletOptions = computed(() =>
  paletOptions.value.filter((p) => p !== primaryPalet.value),
)
const ylRemainingOnPrimaryPalet = computed(() => {
  const p = primaryPalet.value
  if (!p) return []
  return ylStock.value.filter(
    (y) =>
      y.kode_palet === p &&
      Number(y.qty) > 0 &&
      !usedYlKeys.value.has(`${p}:${y.kode_yl}`),
  )
})
const ylForOtherPalet = computed(() => {
  const p = otherKyForm.kode_palet
  if (!p) return []
  return ylStock.value.filter(
    (y) =>
      y.kode_palet === p &&
      Number(y.qty) > 0 &&
      !usedYlKeys.value.has(`${p}:${y.kode_yl}`),
  )
})
const canAddYlSamePalet = computed(
  () =>
    !!primaryPalet.value &&
    !!kyForm.kode_yl &&
    Number(kyForm.target_qty) > 0,
)
const canAddOtherPalet = computed(
  () =>
    !!otherKyForm.kode_palet &&
    !!otherKyForm.kode_yl &&
    Number(otherKyForm.target_qty) > 0,
)
const ukurPanelHint = computed(() => {
  if (!activeKy.value) return t('pages.mrpProses.ukurNeedActiveKy')
  if (!scaleOnline.value) return t('pages.mrpProses.detailUkurHint')
  if (!activeKyUkurs.value.length) return t('pages.mrpProses.detailUkurEmpty')
  return t('pages.mrpProses.detailUkurHint')
})

const filteredChangeLotPoRows = computed(() => {
  const q = changeLotSearch.value.trim().toLowerCase()
  if (!q) return changeLotPoRows.value
  return changeLotPoRows.value.filter((po) =>
    [po.no_so, po.no_po, po.customer, po.item_name, po.warna, po.tebal, po.lot_no, po.emboss]
      .map((x) => String(x || '').toLowerCase())
      .some((s) => s.includes(q)),
  )
})

const flowSteps = computed(() => {
  const s = persiapan.value?.status || 'draft'
  const order = ['draft', 'started', 'completed']
  const normalized = s === 'saved' ? 'completed' : s
  const idx = Math.max(0, order.indexOf(normalized))
  return [
    { key: 'draft', label: t('pages.mrpProses.statusDraft'), done: idx > 0, current: idx === 0 },
    { key: 'started', label: t('pages.mrpProses.statusStarted'), done: idx > 1, current: idx === 1 },
    { key: 'completed', label: t('pages.mrpProses.statusCompleted'), done: idx >= 2, current: idx === 2 },
  ]
})

function dash(v) {
  const s = (v == null ? '' : String(v)).trim()
  return s || '—'
}

function formatQty(v) {
  const n = Number(v)
  if (!Number.isFinite(n)) return '—'
  return Number.isInteger(n) ? String(n) : n.toLocaleString(undefined, { maximumFractionDigits: 2 })
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

function kyStatusType(status) {
  const s = String(status || '')
  if (s === 'active') return 'warning'
  if (s === 'planned') return 'info'
  return 'success'
}

function kyStatusLabel(status) {
  const s = String(status || '')
  if (s === 'active') return t('pages.mrpProses.kyActive')
  if (s === 'planned') return t('pages.mrpProses.kyPlanned')
  return t('pages.mrpProses.kyDone')
}

async function loadYlStock() {
  try {
    const data = await mrpListYl({ pageSize: 200 })
    ylStock.value = Array.isArray(data) ? data : data?.items || data?.data || []
  } catch {
    ylStock.value = []
  }
}

async function reload() {
  loading.value = true
  try {
    const data = await mrpGetProses(route.params.id)
    persiapan.value = data.persiapan
    kySessions.value = data.ky_sessions || []
    rpiAllocations.value = data.rpi_allocations || []
    ukurs.value = data.ukurs || []
    if (!activeKy.value) scaleOnline.value = false
    // Prefill form tambah YL ke palet utama.
    if (primaryPalet.value) kyForm.kode_palet = primaryPalet.value
  } catch (e) {
    ElMessage.error(e.message || String(e))
  } finally {
    loading.value = false
  }
}

async function act(action, extra = {}) {
  try {
    const res = await mrpProsesAction(route.params.id, { action, ...extra })
    const msg = res.message || t('common.saved')
    if (res.clamped || (typeof msg === 'string' && /lebih ukur|clamp/i.test(msg))) {
      ElMessage.warning(msg)
    } else {
      ElMessage.success(msg)
    }
    await reload()
    return true
  } catch (e) {
    ElMessage.error(e.message || String(e))
    return false
  }
}

function ukursForKy(kyRow) {
  return ukurs.value.filter((u) => u.ky_id === kyRow.id)
}

function hasilForKy(kyRow) {
  const rows = ukursForKy(kyRow)
  if (!rows.length) return '—'
  const total = rows.reduce((sum, r) => sum + (Number(r.size_val) || 0), 0)
  return `${formatQty(total)} (${rows.length})`
}

function kyRowClassName({ row }) {
  return row.status === 'active' ? 'mrp-proses-ky-row--active' : ''
}

function openKyUkurDetail(kyRow) {
  kyUkurDetailRow.value = kyRow
  kyUkurDetailOpen.value = true
}

function onChangeLotPoSelect(row) {
  changeLotSelectedPoId.value = row?.id ?? null
}

async function openChangeLot(row) {
  const itemId = persiapan.value?.rencana_item_id
  if (!itemId) {
    ElMessage.warning(t('pages.mrpProses.changeLotNoRpi'))
    return
  }
  changeLotRow.value = row
  changeLotSearch.value = ''
  changeLotSelectedPoId.value = null
  changeLotPoRows.value = []
  changeLotOpen.value = true
  changeLotLoading.value = true
  try {
    const data = await mrpRencanaItemListPo(itemId)
    const currentPoId = Number(row.po_id || 0)
    changeLotPoRows.value = (data.po_list || []).filter((po) => Number(po.id) !== currentPoId)
    if (!changeLotPoRows.value.length) {
      ElMessage.warning(t('pages.mrpGudangSisa.assignSoEmpty'))
    }
  } catch (e) {
    ElMessage.error(e.message || String(e))
    changeLotOpen.value = false
  } finally {
    changeLotLoading.value = false
  }
}

async function submitChangeLot() {
  if (!changeLotRow.value?.rip_id || !changeLotSelectedPoId.value) {
    ElMessage.warning(t('pages.mrpProses.changeLotPickRequired'))
    return
  }
  const selected = changeLotPoRows.value.find((p) => p.id === changeLotSelectedPoId.value)
  const needQty = Number(changeLotRow.value.qty_rpi || 0)
  const outstanding = Number(selected?.qty_outstanding || 0)
  if (selected && needQty > outstanding + 1e-9) {
    ElMessage.warning(
      t('pages.mrpProses.changeLotQtyExceed', {
        need: formatQty(needQty),
        avail: formatQty(outstanding),
      }),
    )
    return
  }
  changeLotSaving.value = true
  try {
    const res = await mrpProsesChangeLot(route.params.id, {
      rip_id: changeLotRow.value.rip_id,
      new_po_id: changeLotSelectedPoId.value,
    })
    rpiAllocations.value = res.rpi_allocations || rpiAllocations.value
    ElMessage.success(res.message || t('common.saved'))
    changeLotOpen.value = false
    await reload()
  } catch (e) {
    ElMessage.error(e.message || String(e))
  } finally {
    changeLotSaving.value = false
  }
}

function deleteUkur(ukurId) {
  return act('delete_ukur', { ukur_id: ukurId })
}

function onYlChangeSame() {
  const y = ylRemainingOnPrimaryPalet.value.find((r) => r.kode_yl === kyForm.kode_yl)
  kyForm.target_qty = y ? Number(y.qty) || 0 : 0
}

function openOtherPaletForm() {
  showOtherPaletForm.value = true
  otherKyForm.kode_palet = ''
  otherKyForm.kode_yl = ''
  otherKyForm.target_qty = 0
}

function onOtherPaletChange() {
  otherKyForm.kode_yl = ''
  otherKyForm.target_qty = 0
}

function onOtherYlChange() {
  const y = ylForOtherPalet.value.find((r) => r.kode_yl === otherKyForm.kode_yl)
  otherKyForm.target_qty = y ? Number(y.qty) || 0 : 0
}

async function scanKySamePalet() {
  if (!canAddYlSamePalet.value) {
    ElMessage.warning(t('pages.mrpProses.kyRequired'))
    return
  }
  kyBusy.value = true
  try {
    const ok = await act('scan_ky', {
      kode_palet: primaryPalet.value,
      kode_yl: kyForm.kode_yl,
      target_qty: Number(kyForm.target_qty) || 0,
    })
    if (ok) {
      kyForm.kode_yl = ''
      kyForm.target_qty = 0
      kyForm.kode_palet = primaryPalet.value
      scaleOnline.value = true
      await loadYlStock()
    }
  } finally {
    kyBusy.value = false
  }
}

async function scanKyOtherPalet() {
  if (!canAddOtherPalet.value) {
    ElMessage.warning(t('pages.mrpProses.kyRequired'))
    return
  }
  kyBusy.value = true
  try {
    const ok = await act('scan_ky', {
      kode_palet: otherKyForm.kode_palet,
      kode_yl: otherKyForm.kode_yl,
      target_qty: Number(otherKyForm.target_qty) || 0,
    })
    if (ok) {
      otherKyForm.kode_palet = ''
      otherKyForm.kode_yl = ''
      otherKyForm.target_qty = 0
      showOtherPaletForm.value = false
      scaleOnline.value = true
      await loadYlStock()
    }
  } finally {
    kyBusy.value = false
  }
}

function activateKy(row) {
  return act('activate_ky', { ky_id: row.id }).then((ok) => {
    if (ok) scaleOnline.value = true
  })
}

function startUkurForKy(_row) {
  scaleOnline.value = true
  ElMessage.success(t('pages.mrpProses.detailUkurHint'))
}

function onPanelStart() {
  if (!activeKy.value) {
    ElMessage.warning(t('pages.mrpProses.ukurNeedActiveKy'))
    return
  }
  scaleOnline.value = true
}

function finishKy(row) {
  return act('selesai_ky', { ky_id: row.id }).then((ok) => {
    if (ok) scaleOnline.value = false
  })
}

async function reopenPersiapan() {
  try {
    await ElMessageBox.confirm(t('pages.mrpProses.reopenConfirm'), t('pages.mrpProses.reopen'), {
      type: 'warning',
      confirmButtonText: t('pages.mrpProses.reopen'),
      cancelButtonText: t('common.cancel'),
    })
  } catch {
    return
  }
  await act('reopen')
}

async function reopenKy(row) {
  try {
    await ElMessageBox.confirm(
      t('pages.mrpProses.reopenKyConfirm', {
        yl: row.kode_yl || row.id,
        qty: formatQty(row.qty_consumed || row.actual_qty || 0),
      }),
      t('pages.mrpProses.reopenKy'),
      {
        type: 'warning',
        confirmButtonText: t('pages.mrpProses.reopenKy'),
        cancelButtonText: t('common.cancel'),
      },
    )
  } catch {
    return
  }
  const ok = await act('reopen_ky', { ky_id: row.id })
  if (ok) scaleOnline.value = true
}

async function finishActiveKy() {
  if (!activeKy.value) return
  await finishKy(activeKy.value)
  scaleOnline.value = false
}

async function panelAddUkur(size) {
  if (!activeKy.value) {
    ElMessage.warning(t('pages.mrpProses.ukurNeedActiveKy'))
    return
  }
  if (!scaleOnline.value) {
    ElMessage.warning(t('pages.mrpProses.panelStartFirst'))
    return
  }
  const val = Number(size)
  if (!(val > 0)) {
    ElMessage.warning(t('pages.mrpProses.sizeUkur'))
    return
  }
  await act('add_ukur', { ky_id: activeKy.value.id, size_val: val })
}

function panelDeleteUkur(row) {
  if (row?.id == null) return
  return deleteUkur(row.id)
}

function esc(v) {
  return String(v ?? '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
}

function treatmentItems(raw) {
  return String(raw || '')
    .split(',')
    .map((s) => s.trim())
    .filter(Boolean)
}

function buildTreatmentChecklistHtml(raw) {
  const items = treatmentItems(raw)
  if (!items.length) {
    return '<div class="tx-empty">—</div>'
  }
  const lis = items
    .map(
      (name) =>
        `<li><span class="tx-name">${esc(name)}</span><span class="tx-box" aria-hidden="true"></span></li>`,
    )
    .join('')
  return `<ul class="tx-list">${lis}</ul>`
}

async function wipQrDataUrl(kodeWip) {
  const code = String(kodeWip || '').trim()
  if (!code) return ''
  try {
    return await QRCode.toDataURL(code, {
      width: 120,
      margin: 0,
      errorCorrectionLevel: 'M',
    })
  } catch {
    return ''
  }
}

function buildLabelHtml(p, labelTitle, tanggal, qty, qrDataUrl = '') {
  const copies = Math.max(1, Math.min(99, Number(qty) || 1))
  const txHtml = buildTreatmentChecklistHtml(p.treatment_list)
  const wip = String(p.kode_wip || '').trim()
  const qrImg = qrDataUrl
    ? `<img class="label-qr" src="${qrDataUrl}" alt="${esc(wip)}" />`
    : ''
  const sheets = []
  for (let i = 1; i <= copies; i += 1) {
    sheets.push(`
  <div class="label${i < copies ? ' label--break' : ''}">
    <div class="label-head">
      <h2>${esc(labelTitle)}</h2>
      ${qrImg}
    </div>
    <table>
      <tr><td>Kode Proses</td><td><strong>${esc(p.kode_proses)}</strong></td></tr>
      <tr><td>Kode WIP</td><td><strong>${esc(p.kode_wip)}</strong></td></tr>
      <tr><td>Rencana</td><td>${esc(p.kode_rencana || '—')}</td></tr>
      <tr><td>Warna</td><td>${esc(p.warna || '—')}</td></tr>
      <tr><td>Tebal</td><td>${esc(p.tebal || '—')}</td></tr>
      <tr><td>Emboss</td><td>${esc(p.emboss || '—')}</td></tr>
      <tr><td>Jenis treatment</td><td>${esc(p.treatment_jenis || '—')}</td></tr>
      <tr>
        <td colspan="2" class="tx-cell">
          <div class="tx-title">${esc(t('pages.mrpProses.treatmentList'))}</div>
          ${txHtml}
        </td>
      </tr>
      <tr><td>${esc(t('pages.mrpProses.labelPcs'))}</td><td><strong>${esc(p.jml_pcs ?? 0)}</strong></td></tr>
      <tr><td>Total Qty (Sf)</td><td><strong>${esc(p.total_size ?? 0)}</strong></td></tr>
      <tr><td>Tanggal</td><td>${esc(tanggal)}</td></tr>
    </table>
    <div class="label-copy">${i}/${copies}</div>
  </div>`)
  }
  return `<!DOCTYPE html>
<html lang="id"><head><meta charset="UTF-8"/>
<title>Label WIP - ${esc(p.kode_proses)} (${copies})</title>
<style>
  @page { size: 4in 4in; margin: 0; }
  * { box-sizing: border-box; }
  body {
    font-family: Arial, Helvetica, sans-serif;
    margin: 0;
    padding: 8px;
    background: #f3f3f3;
  }
  .label {
    position: relative;
    width: 4in;
    height: 4in;
    border: 2px solid #000;
    padding: 0.14in 0.16in 0.12in;
    margin: 0 auto 12px;
    background: #fff;
    page-break-inside: avoid;
    overflow: hidden;
    display: flex;
    flex-direction: column;
  }
  .label--break { page-break-after: always; }
  .label-head {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    gap: 8px;
    margin-bottom: 4px;
  }
  .label-head h2 {
    margin: 0;
    flex: 1 1 auto;
    font-size: 12px;
    line-height: 1.2;
    text-align: left;
    letter-spacing: 0.02em;
    padding-top: 2px;
  }
  .label-qr {
    flex: 0 0 auto;
    width: 0.72in;
    height: 0.72in;
    display: block;
  }
  .label table {
    width: 100%;
    border-collapse: collapse;
    font-size: 10px;
    line-height: 1.25;
    flex: 1 1 auto;
  }
  .label td { padding: 1px 0; vertical-align: top; }
  .label td:first-child:not([colspan]) { width: 34%; color: #222; padding-right: 4px; }
  .tx-cell { padding-top: 3px !important; padding-bottom: 3px !important; }
  .tx-title { font-weight: 700; margin-bottom: 2px; }
  .tx-list {
    list-style: none;
    margin: 0;
    padding: 0;
  }
  .tx-list li {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 6px;
    padding: 1px 0;
  }
  .tx-name { flex: 1 1 auto; min-width: 0; }
  .tx-box {
    flex: 0 0 auto;
    width: 11px;
    height: 11px;
    border: 1.5px solid #000;
    display: inline-block;
  }
  .tx-empty { color: #666; }
  .label-copy {
    margin-top: 4px;
    padding-top: 4px;
    border-top: 1px dashed #999;
    text-align: center;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 0.04em;
  }
  .no-print { text-align: center; margin: 12px 0; }
  @media print {
    body { padding: 0; background: #fff; }
    .no-print { display: none; }
    .label {
      margin: 0;
      width: 4in;
      height: 4in;
      border-width: 2px;
    }
  }
</style></head><body>
${sheets.join('\n')}
  <p class="no-print"><button type="button" onclick="window.print()">Cetak</button></p>
</body></html>`
}

async function openLabelDialog() {
  labelQty.value = 1
  labelPayload.value = null
  labelDialogOpen.value = true
  labelLoading.value = true
  try {
    const data = await mrpProsesLabel(route.params.id)
    const p = data.persiapan || {}
    labelPayload.value = {
      title: data.title || 'STIKER LOT WIP PRODUKSI',
      p,
      tanggal: p.date_saved || p.date_created || '',
      qrDataUrl: await wipQrDataUrl(p.kode_wip),
    }
  } catch (e) {
    labelDialogOpen.value = false
    ElMessage.error(e.message || String(e))
  } finally {
    labelLoading.value = false
  }
}

async function confirmPrintLabels() {
  const payload = labelPayload.value
  if (!payload) return
  const qty = Math.max(1, Math.min(99, Number(labelQty.value) || 1))
  labelPrinting.value = true
  try {
    // Catat setiap cetak (audit reprint) jika user boleh update.
    if (canUpdate.value) {
      const ok = await act('reprint')
      if (!ok) return
    }
    const qrDataUrl = payload.qrDataUrl || (await wipQrDataUrl(payload.p?.kode_wip))
    const html = buildLabelHtml(payload.p, payload.title, payload.tanggal, qty, qrDataUrl)
    const w = window.open('', '_blank')
    if (!w) {
      ElMessage.warning(t('pages.mrpProses.popupBlocked'))
      return
    }
    w.document.write(html)
    w.document.close()
    try {
      w.focus()
      w.print()
    } catch {
      /* ignore */
    }
    labelDialogOpen.value = false
  } catch (e) {
    ElMessage.error(e.message || String(e))
  } finally {
    labelPrinting.value = false
  }
}

onMounted(async () => {
  await Promise.all([reload(), loadYlStock()])
})
</script>

<style scoped>
.mrp-proses-flow {
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem;
}
.mrp-proses-flow__step {
  font-size: 0.75rem;
  padding: 0.25rem 0.65rem;
  border-radius: 999px;
  border: 1px solid var(--el-border-color);
  color: var(--el-text-color-secondary);
  background: var(--el-fill-color-blank);
}
.mrp-proses-flow__step.is-done {
  border-color: var(--el-color-success-light-5);
  color: var(--el-color-success);
  background: var(--el-color-success-light-9);
}
.mrp-proses-flow__step.is-current {
  border-color: var(--el-color-primary-light-5);
  color: var(--el-color-primary);
  background: var(--el-color-primary-light-9);
  font-weight: 600;
}
.mrp-proses-stats {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 0.6rem;
}
.mrp-proses-stat {
  border: 1px solid var(--el-border-color-lighter);
  border-radius: 8px;
  padding: 0.65rem 0.75rem;
  min-height: 3.4rem;
}
.mrp-proses-stat--wide {
  grid-column: span 2;
}
.mrp-proses-stat__label {
  display: block;
  font-size: 0.7rem;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: var(--el-text-color-secondary);
  margin-bottom: 0.2rem;
}
.mrp-proses-stat__value {
  font-size: 1rem;
  font-weight: 600;
  color: var(--el-text-color-primary);
}
.mrp-proses-stat__value--text {
  font-size: 0.875rem;
  font-weight: 500;
  word-break: break-word;
}
.mrp-proses-form-row {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  align-items: flex-end;
}
.mrp-proses-ky-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.25rem;
  align-items: center;
  justify-content: center;
}
@media (max-width: 900px) {
  .mrp-proses-stats {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
  .mrp-proses-stat--wide {
    grid-column: span 2;
  }
}
.mrp-proses-detail-layout {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(320px, 360px);
  gap: 1rem;
  align-items: start;
}
.mrp-proses-detail-layout__main {
  min-width: 0;
}
.mrp-proses-detail-layout__side {
  position: sticky;
  top: 0.75rem;
}
@media (max-width: 1100px) {
  .mrp-proses-detail-layout {
    grid-template-columns: 1fr;
  }
  .mrp-proses-detail-layout__side {
    position: static;
  }
}
:deep(.mrp-proses-ky-row--active) {
  --el-table-tr-bg-color: var(--el-color-primary-light-9);
}
.mrp-proses-label-preview {
  max-height: 52vh;
  overflow: auto;
  display: flex;
  flex-direction: column;
  gap: 0.85rem;
  padding: 0.25rem 0.15rem 0.5rem;
}
.mrp-proses-label-preview__card {
  display: flex;
  justify-content: center;
}
.mrp-proses-label-sheet {
  position: relative;
  width: 4in;
  min-height: 4in;
  max-width: 100%;
  border: 2px solid #111;
  padding: 0.45rem 0.55rem 0.4rem;
  background: #fff;
  display: flex;
  flex-direction: column;
  box-sizing: border-box;
}
.mrp-proses-label-sheet__head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 0.45rem;
  margin-bottom: 0.3rem;
}
.mrp-proses-label-sheet h3 {
  margin: 0;
  flex: 1 1 auto;
  font-size: 0.75rem;
  font-weight: 700;
  text-align: left;
  line-height: 1.25;
  padding-top: 0.1rem;
}
.mrp-proses-label-sheet__qr {
  flex: 0 0 auto;
  width: 0.72in;
  height: 0.72in;
  display: block;
}
.mrp-proses-label-sheet table {
  width: 100%;
  font-size: 0.68rem;
  line-height: 1.25;
  border-collapse: collapse;
  flex: 1 1 auto;
}
.mrp-proses-label-sheet td {
  padding: 0.1rem 0;
  vertical-align: top;
}
.mrp-proses-label-sheet td:first-child:not([colspan]) {
  width: 34%;
  color: #555;
  padding-right: 0.25rem;
}
.mrp-proses-label-sheet__tx-title {
  font-weight: 700;
  margin-bottom: 0.15rem;
  color: #333;
}
.mrp-proses-label-sheet__tx-list {
  list-style: none;
  margin: 0;
  padding: 0;
}
.mrp-proses-label-sheet__tx-list li {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.4rem;
  padding: 0.05rem 0;
}
.mrp-proses-label-sheet__box {
  flex: 0 0 auto;
  width: 0.7rem;
  height: 0.7rem;
  border: 1.5px solid #111;
  display: inline-block;
}
.mrp-proses-label-sheet__tx-empty {
  color: #888;
}
.mrp-proses-label-sheet__copy {
  margin-top: 0.35rem;
  padding-top: 0.3rem;
  border-top: 1px dashed #999;
  text-align: center;
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.04em;
}
.mrp-lot-badge {
  display: inline-block;
  max-width: 100%;
  padding: 1px 7px;
  border-radius: 5px;
  border: 1px solid #e2e8f0;
  background: #f8fafc;
  font-size: 12px;
  font-weight: 500;
}
.mrp-proses-change-lot-current {
  display: flex;
  flex-wrap: wrap;
  gap: 0.35rem 0.5rem;
  align-items: center;
  padding: 0.65rem 0.85rem;
  border-radius: 8px;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  font-size: 0.875rem;
  color: #64748b;
}
</style>
