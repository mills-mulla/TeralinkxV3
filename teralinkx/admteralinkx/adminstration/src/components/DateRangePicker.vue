<template>
  <div class="relative">
    <button 
      @click="showPicker = !showPicker"
      class="flex items-center gap-2 px-4 py-2 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg hover:border-slate-300 dark:hover:border-slate-600 transition-colors text-sm"
    >
      <svg class="w-4 h-4 text-slate-600 dark:text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
      </svg>
      <span class="text-slate-900 dark:text-white">{{ displayText }}</span>
      <svg class="w-4 h-4 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
      </svg>
    </button>

    <div v-if="showPicker" class="absolute top-full mt-2 right-0 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg shadow-xl z-50 w-80">
      <div class="p-4 space-y-3">
        <!-- Presets -->
        <div class="grid grid-cols-2 gap-2">
          <button 
            v-for="preset in presets" 
            :key="preset.value"
            @click="selectPreset(preset)"
            class="px-3 py-2 text-xs rounded-lg transition-colors"
            :class="selectedPreset === preset.value ? 'bg-blue-500 text-white' : 'bg-slate-100 dark:bg-slate-700 text-slate-900 dark:text-white hover:bg-slate-200 dark:hover:bg-slate-600'"
          >
            {{ preset.label }}
          </button>
        </div>

        <!-- Custom Range -->
        <div class="pt-3 border-t border-slate-200 dark:border-slate-700 space-y-2">
          <div>
            <label class="text-xs text-slate-600 dark:text-slate-400 mb-1 block">Start Date</label>
            <input 
              v-model="customStart" 
              type="date" 
              class="w-full px-3 py-2 text-xs bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white"
            />
          </div>
          <div>
            <label class="text-xs text-slate-600 dark:text-slate-400 mb-1 block">End Date</label>
            <input 
              v-model="customEnd" 
              type="date" 
              class="w-full px-3 py-2 text-xs bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white"
            />
          </div>
        </div>

        <!-- Compare Toggle -->
        <div class="pt-3 border-t border-slate-200 dark:border-slate-700">
          <label class="flex items-center gap-2 cursor-pointer">
            <input 
              v-model="compareEnabled" 
              type="checkbox" 
              class="w-4 h-4 text-blue-600 rounded"
            />
            <span class="text-xs text-slate-900 dark:text-white">Compare with previous period</span>
          </label>
        </div>

        <!-- Actions -->
        <div class="flex gap-2 pt-3 border-t border-slate-200 dark:border-slate-700">
          <button 
            @click="applyRange"
            class="flex-1 px-3 py-2 bg-blue-500 hover:bg-blue-600 text-white text-xs rounded-lg transition-colors"
          >
            Apply
          </button>
          <button 
            @click="showPicker = false"
            class="px-3 py-2 bg-slate-100 dark:bg-slate-700 hover:bg-slate-200 dark:hover:bg-slate-600 text-slate-900 dark:text-white text-xs rounded-lg transition-colors"
          >
            Cancel
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'DateRangePicker',
  emits: ['change'],
  data() {
    return {
      showPicker: false,
      selectedPreset: 'last7days',
      customStart: '',
      customEnd: '',
      compareEnabled: false,
      presets: [
        { label: 'Today', value: 'today' },
        { label: 'Yesterday', value: 'yesterday' },
        { label: 'Last 7 Days', value: 'last7days' },
        { label: 'Last 30 Days', value: 'last30days' },
        { label: 'This Month', value: 'thismonth' },
        { label: 'Last Month', value: 'lastmonth' },
        { label: 'Last 90 Days', value: 'last90days' },
        { label: 'This Year', value: 'thisyear' }
      ]
    }
  },
  computed: {
    displayText() {
      const preset = this.presets.find(p => p.value === this.selectedPreset)
      if (preset) return preset.label
      if (this.customStart && this.customEnd) {
        return `${this.customStart} - ${this.customEnd}`
      }
      return 'Select Date Range'
    }
  },
  methods: {
    selectPreset(preset) {
      this.selectedPreset = preset.value
      const { start, end } = this.getPresetDates(preset.value)
      this.customStart = start
      this.customEnd = end
    },
    getPresetDates(preset) {
      const today = new Date()
      const formatDate = (date) => date.toISOString().split('T')[0]
      
      switch(preset) {
        case 'today':
          return { start: formatDate(today), end: formatDate(today) }
        case 'yesterday':
          const yesterday = new Date(today)
          yesterday.setDate(yesterday.getDate() - 1)
          return { start: formatDate(yesterday), end: formatDate(yesterday) }
        case 'last7days':
          const week = new Date(today)
          week.setDate(week.getDate() - 7)
          return { start: formatDate(week), end: formatDate(today) }
        case 'last30days':
          const month = new Date(today)
          month.setDate(month.getDate() - 30)
          return { start: formatDate(month), end: formatDate(today) }
        case 'last90days':
          const quarter = new Date(today)
          quarter.setDate(quarter.getDate() - 90)
          return { start: formatDate(quarter), end: formatDate(today) }
        case 'thismonth':
          const monthStart = new Date(today.getFullYear(), today.getMonth(), 1)
          return { start: formatDate(monthStart), end: formatDate(today) }
        case 'lastmonth':
          const lastMonthStart = new Date(today.getFullYear(), today.getMonth() - 1, 1)
          const lastMonthEnd = new Date(today.getFullYear(), today.getMonth(), 0)
          return { start: formatDate(lastMonthStart), end: formatDate(lastMonthEnd) }
        case 'thisyear':
          const yearStart = new Date(today.getFullYear(), 0, 1)
          return { start: formatDate(yearStart), end: formatDate(today) }
        default:
          return { start: formatDate(today), end: formatDate(today) }
      }
    },
    applyRange() {
      this.$emit('change', {
        start: this.customStart,
        end: this.customEnd,
        compare: this.compareEnabled,
        preset: this.selectedPreset
      })
      this.showPicker = false
    }
  },
  mounted() {
    this.selectPreset(this.presets[2]) // Default to Last 7 Days
  }
}
</script>
