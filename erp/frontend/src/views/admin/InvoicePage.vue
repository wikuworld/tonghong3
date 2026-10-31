<template>
  <AdminSection :title="t('pages.invoice.title')" :subtitle="t('pages.invoice.subtitle')">
    <template #actions>
      <el-input
        v-if="tab === 'list'"
        v-model="keyword"
        :placeholder="t('pages.invoice.searchPlaceholder')"
        clearable
        class="invoice-toolbar-search"
      />
      <span v-if="tabLoading" class="text-xs text-slate-500">{{ t('common.loadingData') }}</span>
      <el-button :icon="Refresh" :loading="tabLoading" @click="refreshCurrentTab">{{ t('common.refresh') }}</el-button>
      <el-tooltip
        v-if="canCreate"
        :content="t('pages.invoice.createFallbackHint')"
        placement="bottom"
      >
        <el-button :icon="Plus" @click="openCreate">{{ t('pages.invoice.createFallback') }}</el-button>
      </el-tooltip>
    </template>

    <el-tabs v-model="tab" @tab-change="onTabChange">
      <el-tab-pane name="list">
        <template #label>
          <span class="flex items-center gap-1">
            {{ t('pages.invoice.tabList') }}
            <el-badge v-if="invoiceListCount > 0" :value="invoiceListCount" :max="99" type="primary" />
          </span>
        </template>

        <div class="invoice-stats mb-4">
          <div class="invoice-stat">
            <span class="invoice-stat__value">{{ listStats.total }}</span>
            <span class="invoice-stat__label">{{ t('common.total') }}</span>
          </div>
          <div class="invoice-stat invoice-stat--shown">
            <span class="invoice-stat__value">{{ listStats.shown }}</span>
            <span class="invoice-stat__label">{{ t('pages.invoice.shownRows') }}</span>
          </div>
          <div class="invoice-stat invoice-stat--amount">
            <span class="invoice-stat__value">{{ formatNum(listStats.amount) }}</span>
            <span class="invoice-stat__label">{{ t('pages.invoice.totalAmount') }} (USD)</span>
          </div>
        </div>

        <div class="admin-table-scroll">
          <el-table
            :data="rows"
            v-loading="loading"
            border
            stripe
            size="small"
            class="admin-table invoice-list-table"
            :empty-text="t('pages.invoice.tableEmpty')"
            @sort-change="onListSortChange"
          >
            <el-table-column type="index" :label="t('common.noLabel')" width="50" align="center" fixed="left"
              :index="(i) => (page - 1) * pageSize + i + 1" />
            <el-table-column prop="invoice_number" :label="t('common.invoiceNo')" min-width="150" show-overflow-tooltip sortable="custom">
              <template #default="{ row }">
                <el-button link type="primary" @click="openDetail(row)">
                  {{ row.invoice_number || `#${row.id}` }}
                </el-button>
              </template>
            </el-table-column>
            <el-table-column prop="delivery_id" :label="t('pages.invoice.deliveryId')" width="110" align="center">
              <template #default="{ row }">
                <el-button v-if="row.delivery_id" link type="primary" @click="goDelivery(row.delivery_id)">
                  {{ row.delivery_id }}
                </el-button>
                <span v-else>—</span>
              </template>
            </el-table-column>
            <el-table-column prop="po_number" :label="t('pages.mrpRencana.soRef')" min-width="150" show-overflow-tooltip>
              <template #default="{ row }">
                <el-button v-if="row.po_id" link type="primary" @click="goPo(row.po_id)">
                  {{ row.po_number || `#${row.po_id}` }}
                </el-button>
                <span v-else>{{ row.po_number || '—' }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="customer_name" :label="t('common.customer')" min-width="180" show-overflow-tooltip />
            <el-table-column prop="invoice_date" :label="t('common.date')" width="120" sortable="custom">
              <template #default="{ row }">{{ formatDate(row.invoice_date) }}</template>
            </el-table-column>
            <el-table-column :label="t('pages.invoice.dueDate')" width="120">
              <template #default="{ row }">{{ formatDate(row.due_date) }}</template>
            </el-table-column>
            <el-table-column :label="`${t('common.total')} (USD)`" min-width="120" align="right">
              <template #default="{ row }">{{ formatNum(row.total_amount) }}</template>
            </el-table-column>
            <el-table-column prop="payment_status" :label="t('common.status')" width="110" align="center" sortable="custom">
              <template #default="{ row }">{{ row.payment_status || '—' }}</template>
            </el-table-column>
            <el-table-column :label="t('common.actions')" width="96" fixed="right" align="center">
              <template #default="{ row }">
                <AdminTableActions
                  :show-view="true"
                  :more-items="invoiceListMoreItems(row)"
                  @view="openDetail(row)"
                  @more="(cmd) => handleInvoiceListMore(row, cmd)"
                />
              </template>
            </el-table-column>
          </el-table>
        </div>

        <div v-if="rows.length" class="invoice-total-bar">
          <span>{{ t('pages.invoice.filteredTotal') }}: {{ formatCurrency(filteredTotalAmount, 'USD') }}</span>
        </div>
        <div class="mt-3 flex justify-end">
          <el-pagination
            v-model:current-page="page"
            v-model:page-size="pageSize"
            size="small"
            background
            layout="total, sizes, prev, pager, next"
            :total="totalRows"
            :page-sizes="[20, 50, 100, 200]"
          />
        </div>
      </el-tab-pane>

      <el-tab-pane name="outstanding">
        <template #label>
          <span class="flex items-center gap-1">
            {{ t('pages.invoice.tabOutstanding') }}
            <el-badge v-if="outstandingCount > 0" :value="outstandingCount" :max="99" type="danger" />
          </span>
        </template>

        <div class="filter-panel mb-4">
          <p class="filter-panel__title">{{ t('common.filter') }}</p>
          <el-form class="filter-form" label-position="top">
            <el-row :gutter="12">
              <el-col :xs="24" :sm="12" :md="8" :lg="5">
                <el-form-item :label="t('pages.invoice.filterKeyword')">
                  <el-input v-model="outstandingQ" clearable :placeholder="t('pages.invoice.filterKeyword')" @keyup.enter="loadOutstanding" />
                </el-form-item>
              </el-col>
              <el-col :xs="24" :sm="12" :md="8" :lg="5">
                <el-form-item :label="t('pages.invoice.filterCustomer')">
                  <el-select v-model="outstandingCustomerId" clearable filterable class="w-full" @change="loadOutstanding">
                    <el-option v-for="c in customers" :key="c.id" :label="c.name" :value="c.id" />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :xs="24" :sm="12" :md="8" :lg="4">
                <el-form-item :label="t('pages.invoice.colStatusAr')">
                  <el-select v-model="outstandingArStatus" clearable class="w-full" @change="onArStatusChange">
                    <el-option :label="t('pages.invoice.modeStatusAll')" value="" />
                    <el-option :label="t('pages.invoice.statusNotOverdue')" value="not_overdue" />
                    <el-option :label="t('pages.invoice.statusOverdue')" value="overdue" />
                    <el-option :label="t('pages.invoice.statusClosed')" value="closed" />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :xs="24" :sm="12" :md="8" :lg="4">
                <el-form-item :label="t('pages.invoice.filter')">
                  <el-select v-model="outstandingMode" class="w-full" @change="loadOutstanding">
                    <el-option :label="t('pages.invoice.modeAll')" value="all" />
                    <el-option :label="t('pages.invoice.modeDue7d')" value="due7" />
                    <el-option :label="t('pages.invoice.modeOverdue')" value="overdue" />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :xs="24" :sm="12" :md="8" :lg="4">
                <el-form-item :label="t('pages.invoice.displayOptions')">
                  <el-checkbox v-model="openOnly" @change="loadOutstanding">{{ t('pages.invoice.openOnly') }}</el-checkbox>
                  <el-checkbox v-model="hidePo" @change="loadOutstanding">{{ t('pages.invoice.hidePo') }}</el-checkbox>
                </el-form-item>
              </el-col>
              <el-col :xs="24" :sm="8" :md="6" :lg="2" class="invoice-filter-action-col">
                <el-form-item label="&nbsp;">
                  <el-button class="w-full" :icon="RefreshLeft" @click="resetOutstandingFilters">{{ t('common.reset') }}</el-button>
                </el-form-item>
              </el-col>
            </el-row>
          </el-form>
        </div>

        <div class="admin-action-bar mb-3">
          <p class="admin-action-bar__hint">{{ t('pages.invoice.printTandaTerima') }} — {{ outstandingSelected.length }} dipilih</p>
          <div class="admin-action-bar__buttons">
            <el-button
              v-if="canUpdate"
              type="primary"
              :disabled="!outstandingSelected.length"
              :loading="tandaTerimaSaving"
              @click="openTandaTerima"
            >
              {{ t('pages.invoice.printTandaTerima') }}
            </el-button>
          </div>
        </div>

        <div class="invoice-stats mb-4">
          <div class="invoice-stat">
            <span class="invoice-stat__value">{{ outstandingStats.total }}</span>
            <span class="invoice-stat__label">{{ t('common.total') }}</span>
          </div>
          <div class="invoice-stat invoice-stat--unpaid">
            <span class="invoice-stat__value">{{ outstandingStats.open }}</span>
            <span class="invoice-stat__label">{{ t('pages.invoice.unpaid') }}</span>
          </div>
          <div class="invoice-stat invoice-stat--paid">
            <span class="invoice-stat__value">{{ outstandingStats.closed }}</span>
            <span class="invoice-stat__label">{{ t('pages.invoice.statusClosed') }}</span>
          </div>
          <div class="invoice-stat invoice-stat--amount">
            <span class="invoice-stat__value">{{ formatNum(outstandingStats.balance) }}</span>
            <span class="invoice-stat__label">{{ t('pages.invoice.colBalance') }}</span>
          </div>
        </div>

        <div class="admin-table-scroll">
          <el-table
            :data="outstandingRows"
            v-loading="outstandingLoading"
            border
            stripe
            size="small"
            class="admin-table invoice-outstanding-table"
            :empty-text="t('pages.invoice.tableEmpty')"
            row-key="id"
            @selection-change="onOutstandingSelection"
            @sort-change="onOutstandingSortChange"
          >
            <el-table-column type="selection" width="44" fixed="left" />
            <el-table-column type="index" :label="t('common.noLabel')" width="48" align="center" fixed="left"
              :index="(i) => (outstandingPage - 1) * outstandingPageSize + i + 1" />
            <el-table-column prop="invoice_number" :label="t('common.invoiceNo')" min-width="140" show-overflow-tooltip fixed="left" sortable="custom" />
            <el-table-column prop="invoice_date" :label="t('common.date')" width="110" sortable="custom">
              <template #default="{ row }">{{ formatDate(row.invoice_date) }}</template>
            </el-table-column>
            <el-table-column :label="t('pages.invoice.colQty')" width="90" align="right">
              <template #default="{ row }">{{ formatQty(row.qty_total) }}</template>
            </el-table-column>
            <el-table-column :label="t('pages.invoice.colAmount')" width="110" align="right">
              <template #default="{ row }">{{ formatNum(row.total_amount) }}</template>
            </el-table-column>
            <el-table-column :label="t('pages.invoice.colDeduction')" width="100" align="right">
              <template #default="{ row }">{{ formatNum(row.deduction_amount) }}</template>
            </el-table-column>
            <el-table-column :label="t('pages.invoice.paymentAmount')" width="110" align="right">
              <template #default="{ row }">{{ formatNum(row.payment_amount) }}</template>
            </el-table-column>
            <el-table-column :label="t('pages.invoice.paymentDate')" width="110">
              <template #default="{ row }">{{ formatDate(row.payment_date) }}</template>
            </el-table-column>
            <el-table-column :label="t('pages.invoice.colBalance')" width="110" align="right">
              <template #default="{ row }">{{ formatNum(row.balance_after_deduct) }}</template>
            </el-table-column>
            <el-table-column prop="term_of_payment" :label="t('pages.invoice.colTerms')" min-width="120" show-overflow-tooltip />
            <el-table-column :label="t('pages.invoice.dueDate')" width="110">
              <template #default="{ row }">{{ formatDate(row.due_date) }}</template>
            </el-table-column>
            <el-table-column prop="ar_status" :label="t('pages.invoice.colStatusAr')" width="120" align="center" sortable="custom">
              <template #default="{ row }">
                <el-tag size="small" :type="arStatusType(row.ar_status)">{{ arStatusLabel(row.ar_status) }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="tax_invoice_no" :label="t('pages.invoice.taxInvoiceNo')" min-width="120" show-overflow-tooltip />
            <el-table-column :label="t('pages.invoice.colDokumenBc')" min-width="120" show-overflow-tooltip>
              <template #default="{ row }">{{ row.dokumen_bc || row.bc_number || row.nopen || '—' }}</template>
            </el-table-column>
            <el-table-column :label="t('pages.invoice.colBcDate')" width="110">
              <template #default="{ row }">{{ formatDate(row.bc_date) }}</template>
            </el-table-column>
            <el-table-column prop="received_by" :label="t('pages.invoice.colReceivedBy')" min-width="140" show-overflow-tooltip />
            <el-table-column :label="t('pages.invoice.colReceivedDate')" width="110">
              <template #default="{ row }">{{ formatDate(row.received_date) }}</template>
            </el-table-column>
            <el-table-column :label="t('common.actions')" width="72" fixed="right" align="center">
              <template #default="{ row }">
                <AdminTableActions
                  v-if="canUpdate"
                  :more-items="invoiceOutstandingMoreItems"
                  @more="(cmd) => handleInvoiceOutstandingMore(row, cmd)"
                />
              </template>
            </el-table-column>
          </el-table>
        </div>
        <div class="mt-3 flex justify-end">
          <el-pagination
            v-model:current-page="outstandingPage"
            v-model:page-size="outstandingPageSize"
            size="small"
            background
            layout="total, sizes, prev, pager, next"
            :total="outstandingTotal"
            :page-sizes="[20, 50, 100, 200]"
          />
        </div>
      </el-tab-pane>
    </el-tabs>

    <el-dialog v-model="detailVisible" :title="t('pages.invoice.dialogDetail')" width="920px" destroy-on-close align-center @closed="onDetailClosed">
      <div v-loading="detailLoading">
        <el-descriptions v-if="detailRow" :column="2" border size="small" class="mb-4">
          <el-descriptions-item :label="t('common.invoiceNo')">{{ detailRow.invoice_number }}</el-descriptions-item>
          <el-descriptions-item :label="t('common.status')">{{ detailRow.payment_status || '—' }}</el-descriptions-item>
          <el-descriptions-item :label="t('pages.invoice.deliveryId')">
            <el-button v-if="detailRow.delivery_id" link type="primary" @click="goDelivery(detailRow.delivery_id)">
              {{ detailRow.delivery_id }}
            </el-button>
            <span v-else>—</span>
          </el-descriptions-item>
          <el-descriptions-item :label="t('pages.mrpRencana.soRef')">
            <el-button v-if="detailRow.po_id" link type="primary" @click="goPo(detailRow.po_id)">
              {{ detailRow.po_number || `#${detailRow.po_id}` }}
            </el-button>
            <span v-else>{{ detailRow.po_number || '—' }}</span>
          </el-descriptions-item>
          <el-descriptions-item :label="t('common.customer')">{{ detailRow.customer_name || '—' }}</el-descriptions-item>
          <el-descriptions-item :label="t('pages.invoice.termOfPayment')">{{ detailRow.term_of_payment || '—' }}</el-descriptions-item>
          <el-descriptions-item :label="t('common.date')">{{ formatDate(detailRow.invoice_date) }}</el-descriptions-item>
          <el-descriptions-item :label="t('pages.invoice.dueDate')">{{ formatDate(detailRow.due_date) || t('common.emptyValue') }}</el-descriptions-item>
          <el-descriptions-item :label="t('common.total')">{{ formatNum(detailRow.total_amount) }}</el-descriptions-item>
          <el-descriptions-item :label="t('pages.invoice.colQty')">{{ formatQty(detailQtyTotal) }}</el-descriptions-item>
          <el-descriptions-item v-if="detailRow.total_in_words" :label="t('pages.invoice.sayTotalWords')" :span="2">
            {{ detailRow.total_in_words }}
          </el-descriptions-item>
        </el-descriptions>

        <p class="mb-2 text-sm font-medium text-slate-700">{{ t('pages.invoice.linesTitle') }}</p>
        <el-table
          :data="detailLines"
          border
          stripe
          size="small"
          class="admin-table"
          :empty-text="t('pages.invoice.linesEmpty')"
        >
          <el-table-column type="index" :label="t('common.noLabel')" width="50" align="center" />
          <el-table-column prop="item_description" :label="t('pages.invoice.item')" min-width="200" show-overflow-tooltip />
          <el-table-column prop="color" :label="t('common.color')" min-width="110" show-overflow-tooltip />
          <el-table-column :label="t('pages.invoice.qtySf')" width="100" align="right">
            <template #default="{ row }">{{ formatQty(row.qty) }}</template>
          </el-table-column>
          <el-table-column :label="t('pages.invoice.unitPriceUsd')" width="120" align="right">
            <template #default="{ row }">{{ formatNum(row.unit_price) }}</template>
          </el-table-column>
          <el-table-column :label="t('pages.invoice.amountUsd')" width="120" align="right">
            <template #default="{ row }">{{ formatNum(row.amount) }}</template>
          </el-table-column>
          <el-table-column prop="roll" label="Roll" width="70" align="center" />
          <el-table-column :label="t('pages.invoice.netWeight')" width="100" align="right">
            <template #default="{ row }">{{ formatQty(row.net_weight) }}</template>
          </el-table-column>
          <el-table-column :label="t('pages.invoice.grossWeight')" width="100" align="right">
            <template #default="{ row }">{{ formatQty(row.gross_weight) }}</template>
          </el-table-column>
        </el-table>
      </div>
      <template #footer>
        <div class="flex flex-wrap items-center justify-end gap-2">
          <el-button
            v-if="canPrint && detailRow?.delivery_id"
            :loading="printLoading"
            @click="openCommercialInvoiceHtml"
          >
            {{ t('pages.invoice.openCommercialInvoice') }}
          </el-button>
          <el-button
            v-if="canPrint && detailRow?.delivery_id"
            type="primary"
            plain
            :loading="printLoading"
            @click="downloadCommercialInvoicePdf"
          >
            {{ t('pages.invoice.downloadCommercialInvoicePdf') }}
          </el-button>
          <el-button type="primary" :icon="Close" @click="detailVisible = false">{{ t('pages.invoice.closeDetail') }}</el-button>
        </div>
      </template>
    </el-dialog>

    <el-dialog v-model="formVisible" :title="t('pages.invoice.dialogAddFallback')" width="560px" destroy-on-close align-center>
      <el-alert type="warning" :closable="false" show-icon class="mb-4">
        {{ t('pages.invoice.createFallbackDialogHint') }}
      </el-alert>
      <el-form label-position="top">
        <el-form-item :label="t('pages.invoice.deliverySentLabel')" required>
          <el-select
            v-model="form.delivery_id"
            filterable
            clearable
            class="w-full"
            :placeholder="t('pages.invoice.pickSentDelivery')"
            @change="onDeliveryPick"
          >
            <el-option
              v-for="d in deliveriesReady"
              :key="d.id"
              :label="deliveryOptionLabel(d)"
              :value="d.id"
            />
          </el-select>
          <span class="mt-1 block text-xs text-slate-500">{{ t('pages.invoice.deliveryFallbackHint') }}</span>
        </el-form-item>
        <el-form-item :label="t('pages.mrpRencana.soRef')">
          <el-select v-model="form.po_id" filterable clearable class="w-full" @change="onPoPick">
            <el-option v-for="p in poList" :key="p.id" :label="p.po_number" :value="p.id" />
          </el-select>
          <span class="mt-1 block text-xs text-slate-500">{{ t('pages.invoice.deliveryValidationHint') }}</span>
        </el-form-item>
        <el-form-item :label="t('common.invoiceNo')">
          <el-input v-model="form.invoice_number" clearable :placeholder="t('pages.invoice.invoiceNoOptionalPlaceholder')" />
        </el-form-item>
        <el-form-item :label="t('common.customer')">
          <el-input v-model="form.customer_name" />
        </el-form-item>
        <el-form-item :label="t('common.date')">
          <el-date-picker
            v-model="form.invoice_date"
            type="date"
            class="w-full"
            value-format="YYYY-MM-DD"
            @change="onTermOrDateChange"
          />
        </el-form-item>
        <el-form-item :label="t('pages.invoice.termOfPayment')">
          <el-input v-model="form.term_of_payment" @change="onTermOrDateChange" />
        </el-form-item>
        <el-form-item :label="t('pages.invoice.dueDate')">
          <el-date-picker
            v-model="form.due_date"
            type="date"
            class="w-full"
            value-format="YYYY-MM-DD"
            :placeholder="t('pages.invoice.dueDateAutoHint')"
          />
        </el-form-item>
        <el-form-item :label="t('common.total') + ' (USD)'">
          <el-input v-model="form.total_amount" type="number" step="0.01" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button :icon="Close" @click="formVisible = false">{{ t('common.cancel') }}</el-button>
        <el-button v-if="canCreate" type="primary" :icon="Check" :loading="saving" @click="submit">{{ t('common.save') }}</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="extraDetailsVisible" :title="t('pages.invoice.extraDetailsTitle')" width="520px" destroy-on-close align-center>
      <el-form label-position="top">
        <el-form-item :label="t('pages.invoice.taxInvoiceNo')">
          <el-input v-model="extraDetails.tax_invoice_no" />
        </el-form-item>
        <el-form-item :label="t('pages.invoice.taxInvoiceDate')">
          <el-date-picker v-model="extraDetails.tax_invoice_date" type="date" class="w-full" value-format="YYYY-MM-DD" />
        </el-form-item>
        <el-form-item :label="t('pages.invoice.colDokumenBc')">
          <el-input v-model="extraDetails.nopen" :placeholder="t('pages.invoice.nopen')" />
        </el-form-item>
        <el-form-item :label="t('pages.invoice.colBcDate')">
          <el-date-picker v-model="extraDetails.bc_date" type="date" class="w-full" value-format="YYYY-MM-DD" clearable />
        </el-form-item>
        <el-form-item :label="t('pages.invoice.nomorAju')">
          <el-input v-model="extraDetails.nomor_aju" />
        </el-form-item>
        <el-form-item :label="t('pages.invoice.colReceivedBy')">
          <el-input v-model="extraDetails.received_by" />
        </el-form-item>
        <el-form-item :label="t('pages.invoice.colReceivedDate')">
          <el-date-picker v-model="extraDetails.received_date" type="date" class="w-full" value-format="YYYY-MM-DD" clearable />
        </el-form-item>
        <el-form-item :label="t('pages.invoice.receiptNo')">
          <el-input v-model="extraDetails.receipt_no" clearable />
        </el-form-item>
        <el-form-item :label="t('pages.invoice.dueDate')">
          <el-date-picker v-model="extraDetails.due_date" type="date" class="w-full" value-format="YYYY-MM-DD" clearable />
        </el-form-item>
        <el-divider content-position="left">{{ t('pages.invoice.creditNoteSection') }}</el-divider>
        <el-form-item :label="t('pages.invoice.creditNoteAmount')">
          <el-input v-model="extraDetails.credit_note_amount" type="number" step="0.01" />
        </el-form-item>
        <el-form-item :label="t('pages.invoice.oiaExportUsd')">
          <el-input v-model="extraDetails.oia_export_usd" type="number" step="0.01" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button :icon="Close" @click="extraDetailsVisible = false">{{ t('common.cancel') }}</el-button>
        <el-button v-if="canUpdate" type="primary" :icon="Check" :loading="extraDetailsSaving" @click="saveExtraDetails">{{ t('common.save') }}</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="paymentVisible" :title="t('pages.invoice.receivePaymentTitle')" width="440px" destroy-on-close align-center>
      <el-form label-position="top">
        <el-alert v-if="paymentForm.invoice_number" type="info" :closable="false" class="mb-3" :title="paymentForm.invoice_number" />
        <el-form-item :label="t('pages.invoice.paymentAmount')" required>
          <el-input v-model="paymentForm.payment_amount" type="number" step="0.01" />
        </el-form-item>
        <el-form-item :label="t('pages.invoice.paymentDate')" required>
          <el-date-picker v-model="paymentForm.payment_date" type="date" class="w-full" value-format="YYYY-MM-DD" />
        </el-form-item>
        <el-form-item :label="t('pages.invoice.paymentRemark')">
          <el-input v-model="paymentForm.payment_remark" maxlength="120" clearable />
        </el-form-item>
        <el-form-item :label="t('pages.invoice.paymentBankAccount')">
          <el-input v-model="paymentForm.payment_bank_account" maxlength="100" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button :icon="Close" @click="paymentVisible = false">{{ t('common.cancel') }}</el-button>
        <el-button v-if="canUpdate" type="success" :icon="Check" :loading="paymentSaving" @click="savePayment">{{ t('common.save') }}</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="tandaTerimaVisible" :title="t('pages.invoice.tandaTerimaDialogTitle')" width="480px" destroy-on-close align-center>
      <el-form label-position="top">
        <p class="mb-3 text-sm text-slate-600">{{ outstandingSelected.length }} invoice · {{ tandaTerimaForm.customer_name || '—' }}</p>
        <el-form-item :label="t('pages.invoice.colReceivedBy')">
          <el-input v-model="tandaTerimaForm.received_by" clearable />
        </el-form-item>
        <el-form-item :label="t('pages.invoice.colReceivedDate')">
          <el-date-picker v-model="tandaTerimaForm.received_date" type="date" class="w-full" value-format="YYYY-MM-DD" />
        </el-form-item>
        <el-form-item :label="t('pages.invoice.receiptNo')">
          <el-input v-model="tandaTerimaForm.receipt_no" clearable :placeholder="'Auto: NNN/MM/YYYY'" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button :icon="Close" @click="tandaTerimaVisible = false">{{ t('common.cancel') }}</el-button>
        <el-button type="default" :loading="tandaTerimaSaving" @click="submitTandaTerima('html')">HTML</el-button>
        <el-button type="primary" :loading="tandaTerimaSaving" @click="submitTandaTerima('pdf')">PDF</el-button>
      </template>
    </el-dialog>
  </AdminSection>
</template>

<script setup>
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Plus, Check, Close, Refresh, RefreshLeft } from '@element-plus/icons-vue'
import AdminSection from '../../components/AdminSection.vue'
import AdminTableActions from '../../components/admin/AdminTableActions.vue'
import { can } from '../../security/permissions'
import { formatCurrency, formatDate, formatNumber } from '../../utils/format'
import { buildPageParams, fromElSortChange, normalizePageResult } from '../../utils/tableQuery'
import {
  createInvoice,
  fetchAuthenticatedDocument,
  getInvoice,
  listCustomers,
  listDelivery,
  listDeliveryDetails,
  listInvoice,
  listInvoiceDetails,
  getDelivery,
  listOutstandingInvoice,
  listPo,
  tandaTerimaBatchHtmlPath,
  tandaTerimaBatchPdfPath,
  toIsoDate,
  updateInvoice,
} from '../../api/client'

const { t } = useI18n()
const route = useRoute()
const router = useRouter()
const canCreate = can('invoice', 'create')
const canUpdate = can('invoice', 'update')
const canPrint = can('invoice', 'print') || can('invoice', 'view')
const loading = ref(false)
const saving = ref(false)
const keyword = ref('')
const rows = ref([])
const page = ref(1)
const pageSize = ref(20)
const totalRows = ref(0)
const sortBy = ref(null)
const sortDir = ref('desc')
const tab = ref('list')
const outstandingRows = ref([])
const outstandingLoading = ref(false)
const outstandingPage = ref(1)
const outstandingPageSize = ref(20)
const outstandingTotal = ref(0)
const outstandingSortBy = ref(null)
const outstandingSortDir = ref('desc')
const outstandingMode = ref('all')
const outstandingArStatus = ref('')
const outstandingCustomerId = ref(null)
const outstandingQ = ref('')
const openOnly = ref(true)
const hidePo = ref(false)
const outstandingSelected = ref([])
const invoiceIdSet = ref([])
const extraDetailsVisible = ref(false)
const extraDetailsSaving = ref(false)
const extraDetails = reactive({
  id: null,
  tax_invoice_no: '',
  tax_invoice_date: '',
  nopen: '',
  bc_date: '',
  nomor_aju: '',
  received_by: '',
  received_date: '',
  receipt_no: '',
  due_date: '',
  credit_note_amount: '',
  oia_export_usd: '',
})
const paymentVisible = ref(false)
const paymentSaving = ref(false)
const paymentForm = reactive({
  id: null,
  invoice_number: '',
  payment_amount: '',
  payment_date: '',
  payment_remark: '',
  payment_bank_account: '',
})
const tandaTerimaVisible = ref(false)
const tandaTerimaSaving = ref(false)
const tandaTerimaForm = reactive({
  customer_name: '',
  received_by: '',
  received_date: '',
  receipt_no: '',
})
const poList = ref([])
const customers = ref([])
const deliveries = ref([])

const tabLoading = computed(() => (tab.value === 'list' ? loading.value : outstandingLoading.value))

function formatNum(v) {
  return formatCurrency(v, 'USD')
}

function formatQty(v) {
  return formatNumber(v, 2)
}

function arStatusLabel(st) {
  const key = String(st || '').toLowerCase()
  if (key === 'closed') return t('pages.invoice.statusClosed')
  if (key === 'overdue') return t('pages.invoice.statusOverdue')
  return t('pages.invoice.statusNotOverdue')
}

function arStatusType(st) {
  const key = String(st || '').toLowerCase()
  if (key === 'closed') return 'success'
  if (key === 'overdue') return 'danger'
  return 'warning'
}

const invoicedDeliveryIds = computed(() => {
  const ids = new Set()
  for (const r of invoiceIdSet.value || []) {
    const did = Number(r.delivery_id)
    if (Number.isFinite(did) && did > 0) ids.add(did)
  }
  return ids
})

const deliveriesReady = computed(() =>
  (deliveries.value || []).filter((d) => {
    const st = (d.status || '').toLowerCase()
    if (st !== 'sent') return false
    if (invoicedDeliveryIds.value.has(Number(d.id))) return false
    return true
  }),
)

async function load() {
  loading.value = true
  try {
    const [invRaw, invIdsRaw, po, cust, del] = await Promise.all([
      listInvoice(
        buildPageParams({
          page: page.value,
          pageSize: pageSize.value,
          sortBy: sortBy.value,
          sortDir: sortDir.value,
          extra: { q: keyword.value.trim() || undefined },
        }),
      ),
      listInvoice({ page_size: 200 }),
      listPo(),
      listCustomers(),
      listDelivery({ page_size: 200 }),
    ])
    const invPage = normalizePageResult(invRaw, { page: page.value, pageSize: pageSize.value })
    invoiceIdSet.value = normalizePageResult(invIdsRaw).items
    poList.value = po
    customers.value = cust
    deliveries.value = normalizePageResult(del).items
    rows.value = invPage.items.map((r) => ({
      ...r,
      invoice_date: r.invoice_date ? String(r.invoice_date).slice(0, 10) : '',
    }))
    totalRows.value = invPage.total
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  } finally {
    loading.value = false
  }
}

function onListSortChange(payload) {
  const { sortBy: sb, sortDir: sd } = fromElSortChange(payload)
  sortBy.value = sb
  sortDir.value = sd
  page.value = 1
  load()
}

function onOutstandingSortChange(payload) {
  const { sortBy: sb, sortDir: sd } = fromElSortChange(payload)
  outstandingSortBy.value = sb
  outstandingSortDir.value = sd
  outstandingPage.value = 1
  loadOutstanding()
}

function refreshCurrentTab() {
  if (tab.value === 'list') load()
  else loadOutstanding()
}

function onTabChange(name) {
  if (name === 'outstanding') loadOutstanding()
}

function tabFromRoute() {
  return String(route.query.tab || '') === 'outstanding' ? 'outstanding' : 'list'
}

async function applyRouteQuery() {
  const nextTab = tabFromRoute()
  if (nextTab !== tab.value) tab.value = nextTab
  if (tab.value === 'outstanding') await loadOutstanding()

  const invoiceId = Number(route.query.invoice_id)
  if (!Number.isNaN(invoiceId) && invoiceId > 0) {
    tab.value = 'list'
    const target = rows.value.find((r) => Number(r.id) === invoiceId)
    if (target) openDetail(target)
    return
  }

  const deliveryId = Number(route.query.delivery_id)
  if (Number.isNaN(deliveryId) || deliveryId <= 0) return
  const wantCreate = String(route.query.create || '') === '1' || route.query.amount != null
  let existing = null
  try {
    const found = await listInvoice({ delivery_id: deliveryId, page_size: 50 })
    const items = normalizePageResult(found).items
    existing = items.length ? items[0] : null
  } catch {
    existing = (rows.value || []).find((r) => Number(r.delivery_id) === deliveryId) || null
  }
  if (existing) {
    tab.value = 'list'
    openDetail(existing)
    return
  }
  if (!canCreate || !wantCreate) return
  if (formVisible.value && Number(form.delivery_id) === deliveryId) return
  ElMessage.info(t('pages.invoice.preferAutoThin'))
  await openCreateFromDelivery(deliveryId, route.query.amount)
}

onMounted(async () => {
  await load()
  await applyRouteQuery()
})

async function loadOutstanding() {
  outstandingLoading.value = true
  try {
    const params = buildPageParams({
      page: outstandingPage.value,
      pageSize: outstandingPageSize.value,
      sortBy: outstandingSortBy.value,
      sortDir: outstandingSortDir.value,
      extra: {
        hide_po: hidePo.value,
        open_only: openOnly.value,
      },
    })
    if (outstandingMode.value === 'overdue') params.overdue_only = true
    if (outstandingMode.value === 'due7') params.due_within_days = 7
    if (outstandingArStatus.value) params.ar_status = outstandingArStatus.value
    if (outstandingCustomerId.value) params.customer_id = outstandingCustomerId.value
    if (outstandingQ.value.trim()) params.q = outstandingQ.value.trim()
    // If filtering specifically for closed, don't force open_only
    if (outstandingArStatus.value === 'closed') params.open_only = false
    const pageData = normalizePageResult(await listOutstandingInvoice(params), {
      page: outstandingPage.value,
      pageSize: outstandingPageSize.value,
    })
    outstandingRows.value = pageData.items
    outstandingTotal.value = pageData.total
    outstandingSelected.value = []
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  } finally {
    outstandingLoading.value = false
  }
}

function onArStatusChange() {
  if (outstandingArStatus.value === 'closed') openOnly.value = false
  loadOutstanding()
}

function resetOutstandingFilters() {
  outstandingMode.value = 'all'
  outstandingArStatus.value = ''
  outstandingCustomerId.value = null
  outstandingQ.value = ''
  openOnly.value = true
  hidePo.value = false
  outstandingPage.value = 1
  loadOutstanding()
}

function onOutstandingSelection(rows) {
  outstandingSelected.value = rows || []
}

const invoiceOutstandingMoreItems = computed(() => [
  { command: 'extraDetails', label: t('pages.invoice.actionExtraDetails') },
  { command: 'receivePayment', label: t('pages.invoice.actionReceivePayment') },
])

function handleInvoiceOutstandingMore(row, command) {
  if (command === 'extraDetails') openExtraDetails(row)
  else if (command === 'receivePayment') openReceivePayment(row)
}

function openExtraDetails(row) {
  extraDetails.id = row.id
  extraDetails.tax_invoice_no = row.tax_invoice_no || ''
  extraDetails.tax_invoice_date = row.tax_invoice_date || ''
  extraDetails.nopen = row.dokumen_bc || row.bc_number || row.nopen || ''
  extraDetails.bc_date = row.bc_date || ''
  extraDetails.nomor_aju = row.nomor_aju || ''
  extraDetails.received_by = row.received_by || ''
  extraDetails.received_date = row.received_date || ''
  extraDetails.receipt_no = row.receipt_no || ''
  extraDetails.due_date = row.due_date || ''
  extraDetails.credit_note_amount = row.credit_note_amount ?? ''
  extraDetails.oia_export_usd = row.oia_export_usd ?? ''
  extraDetailsVisible.value = true
}

async function saveExtraDetails() {
  if (!extraDetails.id) return
  extraDetailsSaving.value = true
  try {
    await updateInvoice(extraDetails.id, {
      tax_invoice_no: extraDetails.tax_invoice_no || undefined,
      tax_invoice_date: toIsoDate(extraDetails.tax_invoice_date) || undefined,
      nopen: extraDetails.nopen || undefined,
      bc_date: toIsoDate(extraDetails.bc_date) || undefined,
      nomor_aju: extraDetails.nomor_aju || undefined,
      received_by: extraDetails.received_by || undefined,
      received_date: toIsoDate(extraDetails.received_date) || undefined,
      receipt_no: extraDetails.receipt_no || undefined,
      due_date: toIsoDate(extraDetails.due_date) || undefined,
      credit_note_amount:
        extraDetails.credit_note_amount === '' ? undefined : Number(extraDetails.credit_note_amount),
      oia_export_usd: extraDetails.oia_export_usd === '' ? undefined : Number(extraDetails.oia_export_usd),
    })
    ElMessage.success(t('pages.invoice.detailsSaved'))
    extraDetailsVisible.value = false
    await loadOutstanding()
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  } finally {
    extraDetailsSaving.value = false
  }
}

function openReceivePayment(row) {
  paymentForm.id = row.id
  paymentForm.invoice_number = row.invoice_number || `#${row.id}`
  paymentForm.payment_amount = row.payment_amount ?? row.balance_after_deduct ?? ''
  paymentForm.payment_date = row.payment_date || toIsoDate(new Date())
  paymentForm.payment_remark = row.payment_remark || ''
  paymentForm.payment_bank_account = row.payment_bank_account || ''
  paymentVisible.value = true
}

async function savePayment() {
  if (!paymentForm.id) return
  const amt = Number(paymentForm.payment_amount)
  if (!Number.isFinite(amt) || amt < 0) {
    ElMessage.warning(t('pages.invoice.paymentAmount'))
    return
  }
  if (!paymentForm.payment_date) {
    ElMessage.warning(t('pages.invoice.paymentDate'))
    return
  }
  paymentSaving.value = true
  try {
    await updateInvoice(paymentForm.id, {
      payment_amount: amt,
      payment_date: toIsoDate(paymentForm.payment_date),
      payment_remark: paymentForm.payment_remark || undefined,
      payment_bank_account: paymentForm.payment_bank_account || undefined,
    })
    ElMessage.success(t('pages.invoice.paymentSaved'))
    paymentVisible.value = false
    await loadOutstanding()
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  } finally {
    paymentSaving.value = false
  }
}

function openTandaTerima() {
  if (!outstandingSelected.value.length) {
    ElMessage.warning(t('pages.invoice.tandaTerimaPickWarning'))
    return
  }
  const custKeys = new Set(
    outstandingSelected.value.map((r) => String(r.customer_id || r.customer_name || '')),
  )
  if (custKeys.size > 1) {
    ElMessage.warning(t('pages.invoice.tandaTerimaSameCustomer'))
    return
  }
  const first = outstandingSelected.value[0]
  tandaTerimaForm.customer_name = first.customer_name || ''
  tandaTerimaForm.received_by = first.received_by || ''
  tandaTerimaForm.received_date = toIsoDate(new Date())
  tandaTerimaForm.receipt_no = ''
  tandaTerimaVisible.value = true
}

async function submitTandaTerima(mode) {
  const ids = outstandingSelected.value.map((r) => r.id).filter(Boolean)
  if (!ids.length) {
    ElMessage.warning(t('pages.invoice.tandaTerimaPickWarning'))
    return
  }
  tandaTerimaSaving.value = true
  try {
    const body = {
      invoice_ids: ids,
      received_by: tandaTerimaForm.received_by || undefined,
      received_date: toIsoDate(tandaTerimaForm.received_date) || undefined,
      receipt_no: tandaTerimaForm.receipt_no || undefined,
      stamp_invoices: true,
    }
    const path = mode === 'pdf' ? tandaTerimaBatchPdfPath() : tandaTerimaBatchHtmlPath()
    await fetchAuthenticatedDocument(path, {
      method: 'POST',
      body,
      mode: mode === 'pdf' ? 'download' : 'open',
      downloadFallbackName: 'tanda_terima.pdf',
    })
    ElMessage.success(t('pages.invoice.tandaTerimaSuccess'))
    tandaTerimaVisible.value = false
    await loadOutstanding()
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  } finally {
    tandaTerimaSaving.value = false
  }
}

const filteredTotalAmount = computed(() =>
  rows.value.reduce((sum, r) => sum + (Number(r.total_amount) || 0), 0),
)

const listStats = computed(() => ({
  total: totalRows.value,
  shown: rows.value.length,
  amount: filteredTotalAmount.value,
}))

const outstandingStats = computed(() => {
  const rows = outstandingRows.value || []
  return {
    total: outstandingTotal.value,
    open: rows.filter((r) => r.ar_status !== 'closed').length,
    closed: rows.filter((r) => r.ar_status === 'closed').length,
    balance: rows.reduce((s, r) => s + (Number(r.balance_after_deduct) || 0), 0),
  }
})

const invoiceListCount = computed(() => totalRows.value)

const outstandingCount = computed(() => outstandingTotal.value)

const detailVisible = ref(false)
const detailRow = ref(null)
const detailLines = ref([])
const detailLoading = ref(false)
const printLoading = ref(false)

const detailQtyTotal = computed(() =>
  (detailLines.value || []).reduce((sum, row) => sum + (Number(row?.qty) || 0), 0),
)

function invoiceListMoreItems(row) {
  const items = []
  if (canPrint && row?.delivery_id) {
    items.push({ command: 'print_ci', label: t('pages.invoice.openCommercialInvoice') })
    items.push({ command: 'print_ci_pdf', label: t('pages.invoice.downloadCommercialInvoicePdf') })
  }
  return items
}

async function handleInvoiceListMore(row, cmd) {
  if (cmd === 'print_ci') {
    await printCommercialInvoice(row?.delivery_id, 'html')
    return
  }
  if (cmd === 'print_ci_pdf') {
    await printCommercialInvoice(row?.delivery_id, 'pdf')
  }
}

async function printCommercialInvoice(deliveryId, mode = 'html') {
  const did = Number(deliveryId)
  if (!Number.isFinite(did) || did <= 0) {
    ElMessage.warning(t('pages.invoice.printNeedsDelivery'))
    return
  }
  printLoading.value = true
  try {
    if (mode === 'pdf') {
      await fetchAuthenticatedDocument(`/documents/commercial-invoice/${did}/pdf`, {
        mode: 'download',
        downloadFallbackName: `commercial_invoice_${did}.pdf`,
      })
    } else {
      await fetchAuthenticatedDocument(`/documents/commercial-invoice/${did}`, { mode: 'open' })
    }
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  } finally {
    printLoading.value = false
  }
}

async function openCommercialInvoiceHtml() {
  await printCommercialInvoice(detailRow.value?.delivery_id, 'html')
}

async function downloadCommercialInvoicePdf() {
  await printCommercialInvoice(detailRow.value?.delivery_id, 'pdf')
}

async function openDetail(row) {
  if (!row?.id) return
  detailVisible.value = true
  detailLoading.value = true
  detailLines.value = []
  detailRow.value = { ...row }
  try {
    const [full, lines] = await Promise.all([
      getInvoice(row.id),
      listInvoiceDetails(row.id),
    ])
    detailRow.value = {
      ...row,
      ...full,
      invoice_date: full?.invoice_date ? String(full.invoice_date).slice(0, 10) : row.invoice_date,
      due_date: full?.due_date ? String(full.due_date).slice(0, 10) : row.due_date,
    }
    detailLines.value = Array.isArray(lines) ? lines : []
    // Refresh list totals after lazy sync of lines
    if (full?.total_amount != null) {
      const idx = rows.value.findIndex((r) => Number(r.id) === Number(row.id))
      if (idx >= 0) {
        rows.value[idx] = {
          ...rows.value[idx],
          total_amount: full.total_amount,
          payment_status: full.payment_status,
        }
      }
    }
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  } finally {
    detailLoading.value = false
  }
}

function onDetailClosed() {
  detailRow.value = null
  detailLines.value = []
}

function goPo(poId) {
  if (!poId) return
  router.push({ path: '/admin/po', query: { po_id: String(poId) } })
}

function goDelivery(deliveryId) {
  if (!deliveryId) return
  router.push({ path: '/admin/delivery', query: { delivery_id: String(deliveryId) } })
}

const formVisible = ref(false)
const form = reactive({
  delivery_id: null,
  customer_id: null,
  po_id: null,
  invoice_number: '',
  customer_name: '',
  invoice_date: '',
  due_date: '',
  total_amount: '',
  term_of_payment: '',
})

function parsePaymentTermDays(term) {
  if (!term) return null
  const m = String(term).match(/\d+/)
  if (m) return Number(m[0])
  if (/advance/i.test(String(term))) return 0
  return null
}

function addDaysIso(isoDate, days) {
  if (!isoDate || days == null || !Number.isFinite(Number(days))) return ''
  const d = new Date(`${String(isoDate).slice(0, 10)}T00:00:00`)
  if (Number.isNaN(d.getTime())) return ''
  d.setDate(d.getDate() + Number(days))
  return toIsoDate(d)
}

/** Isi term + jatuh tempo dari payment_terms customer (tidak menimpa nilai yang sudah diisi). */
function applyCustomerPaymentTerms(customer, { forceDue = false } = {}) {
  if (!form.term_of_payment && customer?.payment_terms) {
    form.term_of_payment = String(customer.payment_terms)
  }
  if ((forceDue || !form.due_date) && form.invoice_date && form.term_of_payment) {
    const days = parsePaymentTermDays(form.term_of_payment)
    if (days != null) {
      form.due_date = addDaysIso(form.invoice_date, days)
    }
  }
}

function onTermOrDateChange() {
  // Hitung ulang due saat term/tanggal berubah (form create; due masih boleh di-override manual setelahnya)
  if (form.invoice_date && form.term_of_payment) {
    const days = parsePaymentTermDays(form.term_of_payment)
    if (days != null) {
      form.due_date = addDaysIso(form.invoice_date, days)
    }
  }
}

function onPoPick(pid) {
  if (!pid) return
  const p = poList.value.find((x) => x.id === pid)
  if (!p) return
  if (p.customer_id) {
    form.customer_id = p.customer_id
    const c = customers.value.find((x) => x.id === p.customer_id)
    form.customer_name = c?.name || ''
    applyCustomerPaymentTerms(c)
  }
  form.invoice_number = form.invoice_number || `INV-${p.po_number}`
}

function deliveryOptionLabel(d) {
  const no = d.delivery_number || `DLV-${d.id}`
  return `${no} ${t('common.dotSeparator')} ${d.status}`
}

async function onDeliveryPick(did) {
  if (!did) {
    form.customer_id = null
    form.customer_name = ''
    form.po_id = null
    return
  }
  let d = deliveries.value.find((x) => x.id === did)
  if (!d) {
    try {
      d = await getDelivery(did)
      if (d && !deliveries.value.some((x) => Number(x.id) === Number(d.id))) {
        deliveries.value = [...deliveries.value, d]
      }
    } catch {
      d = null
    }
  }
  if (d?.customer_id) {
    form.customer_id = d.customer_id
    const c = customers.value.find((x) => x.id === d.customer_id)
    form.customer_name = c?.name || d.customer_name || ''
    applyCustomerPaymentTerms(c)
  }
  if (!form.invoice_date) {
    form.invoice_date = toIsoDate(d?.delivery_date || new Date())
  }
  // Hitung ulang due setelah invoice_date terisi
  if (form.customer_id) {
    applyCustomerPaymentTerms(customers.value.find((x) => x.id === form.customer_id))
  }
  form.po_id = null
  try {
    const lines = await listDeliveryDetails(did)
    const poIds = [...new Set((lines || []).map((l) => l.po_id).filter((id) => id != null))]
    if (poIds.length === 1) {
      form.po_id = poIds[0]
      onPoPick(poIds[0])
    }
  } catch {
    form.po_id = null
  }
}

function resetCreateForm() {
  form.delivery_id = null
  form.customer_id = null
  form.po_id = null
  form.invoice_number = ''
  form.customer_name = ''
  form.invoice_date = ''
  form.due_date = ''
  form.total_amount = ''
  form.term_of_payment = ''
}

function openCreate() {
  resetCreateForm()
  if (!deliveriesReady.value.length) {
    ElMessage.info(t('pages.invoice.noFallbackDeliveries'))
    return
  }
  formVisible.value = true
}

async function openCreateFromDelivery(deliveryId, amountRaw) {
  const existing = (rows.value || []).find((r) => Number(r.delivery_id) === Number(deliveryId))
  if (existing) {
    openDetail(existing)
    ElMessage.info(t('pages.invoice.preferAutoThin'))
    return
  }
  resetCreateForm()
  form.delivery_id = deliveryId
  form.invoice_date = toIsoDate(new Date())
  const amt = Number(amountRaw)
  if (Number.isFinite(amt) && amt > 0) form.total_amount = String(amt)
  formVisible.value = true
  await onDeliveryPick(deliveryId)
}

async function submit() {
  if (!form.delivery_id) {
    ElMessage.warning(t('pages.invoice.pickSentDeliveryWarning'))
    return
  }
  const p = poList.value.find((x) => x.id === form.po_id)
  saving.value = true
  try {
    await createInvoice({
      delivery_id: form.delivery_id,
      customer_id: form.customer_id || undefined,
      po_id: form.po_id || undefined,
      invoice_number: form.invoice_number || undefined,
      po_number: p?.po_number || undefined,
      customer_name: form.customer_name || undefined,
      invoice_date: toIsoDate(form.invoice_date) || undefined,
      due_date: toIsoDate(form.due_date) || undefined,
      total_amount: form.total_amount ? Number(form.total_amount) : undefined,
      term_of_payment: form.term_of_payment || undefined,
    })
    ElMessage.success(t('pages.invoice.saved'))
    formVisible.value = false
    await load()
    tab.value = 'outstanding'
    await loadOutstanding()
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  } finally {
    saving.value = false
  }
}

watch(
  () => [route.query.invoice_id, route.query.tab, route.query.delivery_id, route.query.amount, route.query.create],
  async () => {
    await applyRouteQuery()
  },
)

let listFilterTimer = null
watch(keyword, () => {
  page.value = 1
  if (listFilterTimer) clearTimeout(listFilterTimer)
  listFilterTimer = setTimeout(() => load(), 300)
})
watch([page, pageSize], () => {
  if (tab.value === 'list') load()
})
watch([outstandingPage, outstandingPageSize], () => {
  if (tab.value === 'outstanding') loadOutstanding()
})
</script>

<style scoped>
.invoice-flow-hint :deep(.el-alert__title) {
  font-weight: 600;
}

.invoice-stats {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
}

@media (min-width: 640px) {
  .invoice-stats {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}

.invoice-stat {
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  background: #fff;
  padding: 12px 14px;
}

.invoice-stat__value {
  display: block;
  font-size: 1.2rem;
  font-weight: 700;
  line-height: 1.2;
  color: #0f172a;
  word-break: break-word;
}

.invoice-stat__label {
  display: block;
  margin-top: 4px;
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.03em;
  text-transform: uppercase;
  color: #64748b;
}

.invoice-stat--shown .invoice-stat__value {
  color: #0369a1;
}

.invoice-stat--amount .invoice-stat__value {
  color: #15803d;
}

.invoice-stat--unpaid .invoice-stat__value {
  color: #b45309;
}

.invoice-stat--paid .invoice-stat__value {
  color: #15803d;
}

.invoice-filter-action-col {
  display: flex;
  align-items: flex-end;
}

.invoice-list-table {
  width: 100%;
  min-width: 1080px;
}

.invoice-outstanding-table {
  width: 100%;
  min-width: 1180px;
}

.invoice-total-bar {
  margin-top: 12px;
  display: flex;
  justify-content: flex-end;
  gap: 16px;
  font-size: 14px;
  font-weight: 600;
  color: #334155;
}
</style>
