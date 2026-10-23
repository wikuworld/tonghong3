<template>
  <AdminSection :title="pageTitle" :subtitle="pageSubtitle">
    <template #actions>
      <el-button :icon="Refresh" :loading="loading" @click="reload">{{ t('common.refresh') }}</el-button>
      <el-button v-if="canCreate" type="primary" :icon="Plus" @click="openCreate">{{ t('common.create') }}</el-button>
    </template>

    <div class="admin-inner-card">
      <el-table :data="rows" v-loading="loading" border stripe size="small" class="admin-table" :empty-text="t('common.tableEmpty')" @sort-change="onSortChange">
        <el-table-column type="index" width="56" :label="t('common.noLabel')" align="center">
          <template #default="{ $index }">{{ (page - 1) * pageSize + $index + 1 }}</template>
        </el-table-column>
        <el-table-column prop="nama" :label="t('common.name')" min-width="220" sortable="custom" />
        <el-table-column prop="created_at" :label="t('common.date')" min-width="140" sortable="custom" />
        <el-table-column v-if="canCreate" :label="t('common.actions')" width="112" align="center" fixed="right">
          <template #default="{ row }">
            <AdminTableActions
              :show-edit="true"
              :show-delete="true"
              @edit="openEdit(row)"
              @delete="remove(row)"
            />
          </template>
        </el-table-column>
      </el-table>
      <div class="mt-3 flex justify-end">
        <el-pagination
          v-model:current-page="page"
          v-model:page-size="pageSize"
          :total="total"
          :page-sizes="[20, 50, 100]"
          layout="total, sizes, prev, pager, next"
          background
          small
          @current-change="reload"
          @size-change="() => { page = 1; reload() }"
        />
      </div>
    </div>

    <el-dialog v-model="dialogOpen" :title="editId ? t('common.edit') : t('common.create')" width="420px" destroy-on-close>
      <el-form label-position="top">
        <el-form-item :label="t('common.name')" required>
          <el-input v-model="form.nama" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogOpen = false">{{ t('common.cancel') }}</el-button>
        <el-button type="primary" :loading="saving" @click="submit">{{ t('common.save') }}</el-button>
      </template>
    </el-dialog>
  </AdminSection>
</template>

<script setup>
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Refresh } from '@element-plus/icons-vue'
import AdminSection from '../../../components/AdminSection.vue'
import AdminTableActions from '../../../components/admin/AdminTableActions.vue'
import { can } from '../../../security/permissions'
import {
  mrpCreateBentukKulit,
  mrpCreateSkala,
  mrpDeleteBentukKulit,
  mrpDeleteSkala,
  mrpListBentukKulit,
  mrpListSkala,
  mrpUpdateBentukKulit,
  mrpUpdateSkala,
} from '../../../api/client'
import { buildPageParams, fromElSortChange, normalizePageResult } from '../../../utils/tableQuery'

const { t } = useI18n()
const route = useRoute()
const kind = computed(() => String(route.meta?.mrpLookup || 'bentuk-kulit'))

const pageTitle = computed(() =>
  kind.value === 'skala'
    ? t('pages.mrpMasterSkala.title')
    : t('pages.mrpMasterBentukKulit.title'),
)
const pageSubtitle = computed(() =>
  kind.value === 'skala'
    ? t('pages.mrpMasterSkala.subtitle')
    : t('pages.mrpMasterBentukKulit.subtitle'),
)

const api = computed(() =>
  kind.value === 'skala'
    ? {
        list: mrpListSkala,
        create: mrpCreateSkala,
        update: mrpUpdateSkala,
        remove: mrpDeleteSkala,
      }
    : {
        list: mrpListBentukKulit,
        create: mrpCreateBentukKulit,
        update: mrpUpdateBentukKulit,
        remove: mrpDeleteBentukKulit,
      },
)

const loading = ref(false)
const saving = ref(false)
const dialogOpen = ref(false)
const editId = ref(null)
const rows = ref([])
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)
const sortBy = ref('nama')
const sortDir = ref('asc')
const canCreate = computed(() => can('mrpShopfloor', 'create'))
const form = reactive({ nama: '' })

async function reload() {
  loading.value = true
  try {
    const data = await api.value.list(
      buildPageParams({
        page: page.value,
        pageSize: pageSize.value,
        sortBy: sortBy.value,
        sortDir: sortDir.value,
      }),
    )
    const pageData = normalizePageResult(data, { page: page.value, pageSize: pageSize.value })
    rows.value = pageData.items
    total.value = pageData.total
  } catch (e) {
    ElMessage.error(e.message || String(e))
  } finally {
    loading.value = false
  }
}

function onSortChange(payload) {
  const mapped = fromElSortChange(payload)
  sortBy.value = mapped.sortBy || 'nama'
  sortDir.value = mapped.sortDir || 'asc'
  page.value = 1
  reload()
}

function openCreate() {
  editId.value = null
  form.nama = ''
  dialogOpen.value = true
}

function openEdit(row) {
  editId.value = row.id
  form.nama = row.nama
  dialogOpen.value = true
}

async function submit() {
  const nama = String(form.nama || '').trim()
  if (!nama) {
    ElMessage.warning(t('common.fillRequired'))
    return
  }
  saving.value = true
  try {
    if (editId.value) await api.value.update(editId.value, { nama })
    else await api.value.create({ nama })
    ElMessage.success(t('common.saved'))
    dialogOpen.value = false
    await reload()
  } catch (e) {
    ElMessage.error(e.message || String(e))
  } finally {
    saving.value = false
  }
}

async function remove(row) {
  try {
    await ElMessageBox.confirm(t('common.confirm'), { type: 'warning' })
    await api.value.remove(row.id)
    ElMessage.success(t('common.saved'))
    await reload()
  } catch (e) {
    if (e !== 'cancel') ElMessage.error(e.message || String(e))
  }
}

watch(kind, () => {
  page.value = 1
  sortBy.value = 'nama'
  sortDir.value = 'asc'
  reload()
})

onMounted(reload)
</script>
