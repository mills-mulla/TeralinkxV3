<template>
  <div class="relative">
    <button 
      @click="showDropdown = !showDropdown"
      class="flex items-center gap-2 px-4 py-2 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg hover:border-slate-300 dark:hover:border-slate-600 transition-colors text-sm"
    >
      <svg class="w-4 h-4 text-slate-600 dark:text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z" />
      </svg>
      <span class="text-slate-900 dark:text-white">{{ displayText }}</span>
      <span v-if="selectedCount > 0" class="px-2 py-0.5 bg-blue-500 text-white text-xs rounded-full">{{ selectedCount }}</span>
      <svg class="w-4 h-4 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
      </svg>
    </button>

    <div v-if="showDropdown" class="absolute top-full mt-2 right-0 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg shadow-xl z-50 w-72">
      <div class="p-4 space-y-3">
        <!-- Search -->
        <input 
          v-model="searchQuery"
          type="text"
          placeholder="Search..."
          class="w-full px-3 py-2 text-xs bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white"
        />

        <!-- Options -->
        <div class="max-h-64 overflow-y-auto space-y-1">
          <label 
            v-for="option in filteredOptions" 
            :key="option.value"
            class="flex items-center gap-2 px-3 py-2 hover:bg-slate-50 dark:hover:bg-slate-700 rounded-lg cursor-pointer"
          >
            <input 
              v-model="selected"
              :value="option.value"
              type="checkbox" 
              class="w-4 h-4 text-blue-600 rounded"
            />
            <span class="text-sm text-slate-900 dark:text-white">{{ option.label }}</span>
          </label>
          <div v-if="filteredOptions.length === 0" class="text-center text-slate-400 text-xs py-4">
            No results found
          </div>
        </div>

        <!-- Actions -->
        <div class="flex gap-2 pt-3 border-t border-slate-200 dark:border-slate-700">
          <button 
            @click="clearAll"
            class="flex-1 px-3 py-2 bg-slate-100 dark:bg-slate-700 hover:bg-slate-200 dark:hover:bg-slate-600 text-slate-900 dark:text-white text-xs rounded-lg transition-colors"
          >
            Clear All
          </button>
          <button 
            @click="applyFilters"
            class="flex-1 px-3 py-2 bg-blue-500 hover:bg-blue-600 text-white text-xs rounded-lg transition-colors"
          >
            Apply
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'MultiSelectFilter',
  props: {
    label: {
      type: String,
      default: 'Filter'
    },
    options: {
      type: Array,
      required: true
    }
  },
  emits: ['change'],
  data() {
    return {
      showDropdown: false,
      selected: [],
      searchQuery: ''
    }
  },
  computed: {
    displayText() {
      if (this.selected.length === 0) return this.label
      if (this.selected.length === 1) {
        const option = this.options.find(o => o.value === this.selected[0])
        return option ? option.label : this.label
      }
      return `${this.selected.length} selected`
    },
    selectedCount() {
      return this.selected.length
    },
    filteredOptions() {
      if (!this.searchQuery) return this.options
      const query = this.searchQuery.toLowerCase()
      return this.options.filter(o => o.label.toLowerCase().includes(query))
    }
  },
  methods: {
    clearAll() {
      this.selected = []
    },
    applyFilters() {
      this.$emit('change', this.selected)
      this.showDropdown = false
    }
  }
}
</script>
