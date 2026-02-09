<template>
  <div class="bg-white rounded-2xl shadow-sm border border-slate-200/60 p-6">
    <div class="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
      <!-- Search Input -->
      <div class="flex-1">
        <div class="relative">
          <MagnifyingGlassIcon class="w-5 h-5 text-slate-400 absolute left-3 top-1/2 transform -translate-y-1/2" />
          <input
            :value="modelValue"
            @input="$emit('update:modelValue', $event.target.value)"
            type="text"
            :placeholder="placeholder"
            class="w-full pl-10 pr-4 py-3 border border-slate-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-300"
          />
        </div>
      </div>
      
      <!-- Filters -->
      <div v-if="filters && filters.length > 0" class="flex items-center space-x-3">
        <select
          v-for="filter in filters"
          :key="filter.key"
          :value="filterValues[filter.key]"
          @change="handleFilterChange(filter.key, $event.target.value)"
          class="px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 text-sm"
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
      <div class="flex space-x-3">
        <button
          @click="$emit('clear')"
          class="px-4 py-3 border border-slate-300 text-slate-600 rounded-xl hover:bg-slate-50 transition-all duration-300 flex items-center space-x-2"
        >
          <ArrowPathIcon class="w-4 h-4" />
          <span>Clear</span>
        </button>
        <button
          v-if="showAddButton"
          @click="$emit('add')"
          class="px-4 py-3 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-xl hover:from-blue-500 hover:to-purple-500 transition-all duration-300 flex items-center space-x-2 shadow-lg hover:shadow-xl"
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
