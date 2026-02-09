<template>
  <div class="bg-white rounded-2xl shadow-sm border border-slate-200/60 overflow-hidden">
    <!-- Header -->
    <div class="px-6 py-4 border-b border-slate-200/60 flex items-center justify-between">
      <div class="flex items-center space-x-4">
        <h3 class="text-lg font-semibold text-slate-800 flex items-center">
          <component :is="icon" v-if="icon" class="w-5 h-5 text-slate-600 mr-2" />
          {{ title }} ({{ filteredData.length }} found)
        </h3>
        
        <!-- Items per page selector -->
        <div class="flex items-center space-x-2">
          <span class="text-sm text-slate-600">Show:</span>
          <select
            v-model="itemsPerPage"
            @change="handleItemsPerPageChange"
            class="text-sm border border-slate-300 rounded-lg px-2 py-1 focus:ring-2 focus:ring-blue-500"
          >
            <option value="5">5</option>
            <option value="10">10</option>
            <option value="15">15</option>
            <option value="20">20</option>
            <option value="50">50</option>
          </select>
          <span class="text-sm text-slate-600">per page</span>
        </div>
      </div>
      
      <slot name="header-actions">
        <button
          v-if="exportable"
          @click="exportToCSV"
          class="px-4 py-2 bg-slate-100 text-slate-700 rounded-lg hover:bg-slate-200 transition-all duration-300 flex items-center space-x-2 text-sm"
        >
          <ArrowDownTrayIcon class="w-4 h-4" />
          <span>Export CSV</span>
        </button>
      </slot>
    </div>
    
    <!-- Table -->
    <div class="overflow-x-auto">
      <table class="w-full">
        <thead class="bg-slate-50 border-b border-slate-200/60">
          <tr>
            <th
              v-for="column in columns"
              :key="column.key"
              class="px-6 py-4 text-left text-xs font-semibold text-slate-600 uppercase tracking-wider cursor-pointer hover:bg-slate-100"
              @click="column.sortable !== false && sortBy(column.key)"
            >
              <div class="flex items-center space-x-1">
                <span>{{ column.label }}</span>
                <ChevronUpDownIcon v-if="column.sortable !== false" class="w-4 h-4" />
              </div>
            </th>
            <th v-if="actions" class="px-6 py-4 text-left text-xs font-semibold text-slate-600 uppercase tracking-wider">
              Actions
            </th>
          </tr>
        </thead>
        <tbody class="divide-y divide-slate-200/60">
          <tr
            v-for="item in paginatedData"
            :key="item.id"
            class="hover:bg-slate-50 transition-colors duration-200"
          >
            <td
              v-for="column in columns"
              :key="column.key"
              class="px-6 py-4 whitespace-nowrap text-sm"
              :class="column.class || 'text-slate-600'"
            >
              <slot :name="`cell-${column.key}`" :item="item" :value="getNestedValue(item, column.key)">
                {{ formatValue(item, column) }}
              </slot>
            </td>
            <td v-if="actions" class="px-6 py-4 whitespace-nowrap text-sm font-medium">
              <div class="flex space-x-2">
                <button
                  v-if="actions.includes('edit')"
                  @click="$emit('edit', item)"
                  class="text-blue-600 hover:text-blue-800 transition-colors duration-200 p-1 rounded"
                  title="Edit"
                >
                  <PencilSquareIcon class="w-4 h-4" />
                </button>
                <button
                  v-if="actions.includes('delete')"
                  @click="$emit('delete', item)"
                  class="text-rose-600 hover:text-rose-800 transition-colors duration-200 p-1 rounded"
                  title="Delete"
                >
                  <TrashIcon class="w-4 h-4" />
                </button>
                <slot name="custom-actions" :item="item"></slot>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Empty State -->
    <div v-if="filteredData.length === 0" class="text-center py-12">
      <div class="w-16 h-16 bg-slate-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
        <component :is="emptyIcon" class="w-8 h-8 text-slate-400" />
      </div>
      <h3 class="text-lg font-semibold text-slate-600 mb-2">{{ emptyMessage }}</h3>
      <p class="text-slate-500">{{ emptyDescription }}</p>
    </div>

    <!-- Pagination -->
    <div v-if="filteredData.length > 0" class="px-6 py-4 border-t border-slate-200/60 flex items-center justify-between">
      <div class="text-sm text-slate-600">
        Showing {{ startIndex + 1 }} to {{ endIndex }} of {{ filteredData.length }} entries
      </div>
      <div class="flex space-x-2">
        <button
          @click="previousPage"
          :disabled="currentPage === 1"
          :class="[
            'px-3 py-2 rounded-lg border transition-all duration-300',
            currentPage === 1 
              ? 'border-slate-300 text-slate-400 cursor-not-allowed' 
              : 'border-slate-300 text-slate-600 hover:bg-slate-50'
          ]"
        >
          <ChevronLeftIcon class="w-4 h-4" />
        </button>
        <button
          @click="nextPage"
          :disabled="currentPage >= totalPages"
          :class="[
            'px-3 py-2 rounded-lg border transition-all duration-300',
            currentPage >= totalPages
              ? 'border-slate-300 text-slate-400 cursor-not-allowed' 
              : 'border-slate-300 text-slate-600 hover:bg-slate-50'
          ]"
        >
          <ChevronRightIcon class="w-4 h-4" />
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed } from 'vue'
import {
  PencilSquareIcon,
  TrashIcon,
  ChevronLeftIcon,
  ChevronRightIcon,
  ChevronUpDownIcon,
  ArrowDownTrayIcon,
  TableCellsIcon
} from '@heroicons/vue/24/outline'

export default {
  name: 'DataTable',
  components: {
    PencilSquareIcon,
    TrashIcon,
    ChevronLeftIcon,
    ChevronRightIcon,
    ChevronUpDownIcon,
    ArrowDownTrayIcon
  },
  props: {
    title: { type: String, required: true },
    data: { type: Array, required: true },
    columns: { type: Array, required: true },
    actions: { type: Array, default: () => ['edit', 'delete'] },
    icon: { type: Object, default: () => TableCellsIcon },
    emptyIcon: { type: Object, default: () => TableCellsIcon },
    emptyMessage: { type: String, default: 'No data found' },
    emptyDescription: { type: String, default: 'No records match your criteria.' },
    exportable: { type: Boolean, default: true }
  },
  emits: ['edit', 'delete'],
  setup(props) {
    const currentPage = ref(1)
    const itemsPerPage = ref(10)
    const sortKey = ref('')
    const sortOrder = ref('asc')

    const filteredData = computed(() => props.data)

    const sortedData = computed(() => {
      if (!sortKey.value) return filteredData.value
      
      return [...filteredData.value].sort((a, b) => {
        const aVal = getNestedValue(a, sortKey.value)
        const bVal = getNestedValue(b, sortKey.value)
        
        if (aVal < bVal) return sortOrder.value === 'asc' ? -1 : 1
        if (aVal > bVal) return sortOrder.value === 'asc' ? 1 : -1
        return 0
      })
    })

    const totalPages = computed(() => Math.ceil(sortedData.value.length / itemsPerPage.value))
    const startIndex = computed(() => (currentPage.value - 1) * itemsPerPage.value)
    const endIndex = computed(() => Math.min(startIndex.value + itemsPerPage.value, sortedData.value.length))
    const paginatedData = computed(() => sortedData.value.slice(startIndex.value, endIndex.value))

    const getNestedValue = (obj, path) => {
      return path.split('.').reduce((acc, part) => acc?.[part], obj)
    }

    const formatValue = (item, column) => {
      const value = getNestedValue(item, column.key)
      
      if (column.format) {
        return column.format(value, item)
      }
      
      return value ?? 'N/A'
    }

    const sortBy = (key) => {
      if (sortKey.value === key) {
        sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc'
      } else {
        sortKey.value = key
        sortOrder.value = 'asc'
      }
    }

    const nextPage = () => {
      if (currentPage.value < totalPages.value) {
        currentPage.value++
      }
    }

    const previousPage = () => {
      if (currentPage.value > 1) {
        currentPage.value--
      }
    }

    const handleItemsPerPageChange = () => {
      currentPage.value = 1
    }

    const exportToCSV = () => {
      const headers = props.columns.map(col => col.label).join(',')
      const rows = filteredData.value.map(item => 
        props.columns.map(col => {
          const value = getNestedValue(item, col.key)
          return `"${value ?? ''}"`
        }).join(',')
      )
      
      const csv = [headers, ...rows].join('\n')
      const blob = new Blob([csv], { type: 'text/csv' })
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = `${props.title.toLowerCase().replace(/\s+/g, '_')}_${new Date().toISOString().split('T')[0]}.csv`
      link.click()
      window.URL.revokeObjectURL(url)
    }

    return {
      currentPage,
      itemsPerPage,
      filteredData,
      paginatedData,
      totalPages,
      startIndex,
      endIndex,
      getNestedValue,
      formatValue,
      sortBy,
      nextPage,
      previousPage,
      handleItemsPerPageChange,
      exportToCSV
    }
  }
}
</script>
