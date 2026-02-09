<template>
  <div class="bg-white dark:bg-slate-800 rounded-lg border border-slate-200 dark:border-slate-700 p-4 transition-all duration-300">
    <div class="flex flex-col lg:flex-row lg:items-center gap-3">
      <!-- Search Input -->
      <div class="flex-1 relative group">
        <MagnifyingGlassIcon class="w-4 h-4 text-slate-400 dark:text-slate-500 absolute left-3 top-1/2 transform -translate-y-1/2 transition-colors group-focus-within:text-blue-500" />
        <input
          :value="modelValue"
          @input="$emit('update:modelValue', $event.target.value)"
          type="text"
          :placeholder="placeholder"
          class="w-full pl-10 pr-4 py-2 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-slate-900 dark:text-white placeholder-slate-400 dark:placeholder-slate-500 transition-all duration-200 text-sm"
        />
      </div>
      
      <!-- Filters -->
      <div v-if="filters && filters.length > 0" class="flex items-center gap-2">
        <select
          v-for="filter in filters"
          :key="filter.key"
          :value="filterValues[filter.key]"
          @change="handleFilterChange(filter.key, $event.target.value)"
          class="px-3 py-2 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg focus:ring-2 focus:ring-blue-500 text-slate-900 dark:text-white text-sm transition-all duration-200"
        >
          <option value="">{{ filter.label }}</option>
          <option
            v-for="option in filter.options"
            :key="option.value"
            :value="option.value"
          >
            {{ option.label }}
          </option>
        </select>
      </div>
      
      <!-- Action Buttons -->
      <div class="flex gap-2">
        <button
          @click="$emit('clear')"
          class="px-3 py-2 border border-slate-300 dark:border-slate-600 text-slate-600 dark:text-slate-400 rounded-lg hover:bg-slate-50 dark:hover:bg-slate-700 transition-all duration-200 flex items-center gap-2 text-sm"
        >
          <ArrowPathIcon class="w-4 h-4" />
          <span class="hidden sm:inline">Clear</span>
        </button>
        <button
          v-if="showAddButton"
          @click="$emit('add')"
          class="px-3 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-all duration-200 flex items-center gap-2 shadow-sm hover:shadow text-sm"
        >
          <PlusIcon class="w-4 h-4" />
          <span>{{ addButtonText }}</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, watch } from 'vue'
import {
  MagnifyingGlassIcon,
  PlusIcon,
  ArrowPathIcon
} from '@heroicons/vue/24/outline'

export default {
  name: 'SearchBar',
  components: {
    MagnifyingGlassIcon,
    PlusIcon,
    ArrowPathIcon
  },
  props: {
    modelValue: { type: String, default: '' },
    placeholder: { type: String, default: 'Search...' },
    filters: { type: Array, default: () => [] },
    showAddButton: { type: Boolean, default: true },
    addButtonText: { type: String, default: 'Add New' }
  },
  emits: ['update:modelValue', 'filter-change', 'clear', 'add'],
  setup(props, { emit }) {
    const filterValues = ref({})
    
    // Initialize filter values
    watch(() => props.filters, (newFilters) => {
      newFilters.forEach(filter => {
        if (filterValues.value[filter.key] === undefined) {
          filterValues.value[filter.key] = ''
        }
      })
    }, { immediate: true })
    
    const handleFilterChange = (key, value) => {
      filterValues.value[key] = value
      emit('filter-change', { key, value, all: filterValues.value })
    }
    
    return {
      filterValues,
      handleFilterChange
    }
  }
}
</script>
