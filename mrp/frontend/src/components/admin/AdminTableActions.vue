<template>
  <div class="admin-row-actions">
    <el-tooltip v-if="showView" :content="viewLabelResolved" placement="top">
      <el-button
        :icon="View"
        link
        type="primary"
        :aria-label="viewLabelResolved"
        @click="emit('view')"
      />
    </el-tooltip>
    <el-tooltip v-if="showEdit" :content="editLabelResolved" placement="top">
      <el-button
        :icon="EditPen"
        link
        type="warning"
        :aria-label="editLabelResolved"
        @click="emit('edit')"
      />
    </el-tooltip>
    <el-tooltip v-if="showDelete" :content="deleteLabelResolved" placement="top">
      <el-button
        :icon="Delete"
        link
        type="danger"
        :aria-label="deleteLabelResolved"
        @click="emit('delete')"
      />
    </el-tooltip>
    <el-dropdown
      v-if="moreItems.length"
      trigger="click"
      @command="(cmd) => emit('more', cmd)"
    >
      <el-button link type="primary" class="admin-more-trigger" :aria-label="moreAriaLabelResolved">
        <span class="admin-more-kebab" aria-hidden="true"><i /><i /><i /></span>
      </el-button>
      <template #dropdown>
        <el-dropdown-menu>
          <el-dropdown-item
            v-for="item in moreItems"
            :key="String(item.command)"
            :command="item.command"
            :icon="item.icon"
            :divided="Boolean(item.divided)"
            :disabled="Boolean(item.disabled)"
          >
            {{ item.label }}
          </el-dropdown-item>
        </el-dropdown-menu>
      </template>
    </el-dropdown>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { Delete, EditPen, View } from '@element-plus/icons-vue'

const props = defineProps({
  showView: { type: Boolean, default: false },
  showEdit: { type: Boolean, default: false },
  showDelete: { type: Boolean, default: false },
  /** @type {{ command: string|number, label: string, icon?: any, divided?: boolean, disabled?: boolean }[]} */
  moreItems: { type: Array, default: () => [] },
  moreAriaLabel: { type: String, default: '' },
  viewLabel: { type: String, default: '' },
  editLabel: { type: String, default: '' },
  deleteLabel: { type: String, default: '' },
})

const emit = defineEmits(['view', 'edit', 'delete', 'more'])
const { t } = useI18n()

const viewLabelResolved = computed(() => props.viewLabel || t('common.detail'))
const editLabelResolved = computed(() => props.editLabel || t('common.edit'))
const deleteLabelResolved = computed(() => props.deleteLabel || t('common.delete'))
const moreAriaLabelResolved = computed(
  () => props.moreAriaLabel || t('common.moreActions'),
)
</script>

<style scoped>
.admin-row-actions {
  display: inline-flex;
  flex-wrap: nowrap;
  align-items: center;
  justify-content: center;
  gap: 2px;
}

.admin-more-trigger {
  padding: 4px 6px;
  height: auto;
}

.admin-more-kebab {
  display: inline-flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 2px;
  width: 14px;
  height: 14px;
}

.admin-more-kebab i {
  display: block;
  width: 3px;
  height: 3px;
  border-radius: 50%;
  background: currentColor;
}
</style>
