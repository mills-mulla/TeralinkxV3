<template>
  <div class="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-5">
    <div class="flex items-center justify-between mb-4">
      <div class="flex items-center gap-2">
        <svg class="w-5 h-5 text-purple-500" fill="currentColor" viewBox="0 0 24 24">
          <path d="M3 13h8V3H3v10zm0 8h8v-6H3v6zm10 0h8V11h-8v10zm0-18v6h8V3h-8z"/>
        </svg>
        <h3 class="text-sm font-medium text-slate-900 dark:text-white">Cohort Retention Analysis</h3>
      </div>
    </div>

    <div v-if="loading" class="text-center py-8 text-slate-400">Loading...</div>
    
    <div v-else class="overflow-x-auto">
      <table class="w-full text-xs">
        <thead>
          <tr class="border-b border-slate-200 dark:border-slate-700">
            <th class="text-left p-2 text-slate-600 dark:text-slate-400">Cohort</th>
            <th class="text-center p-2 text-slate-600 dark:text-slate-400">Size</th>
            <th v-for="i in 6" :key="i" class="text-center p-2 text-slate-600 dark:text-slate-400">M{{ i-1 }}</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="cohort in cohorts" :key="cohort.cohort" class="border-b border-slate-200 dark:border-slate-700">
            <td class="p-2 font-medium text-slate-900 dark:text-white">{{ cohort.cohort }}</td>
            <td class="p-2 text-center text-slate-900 dark:text-white">{{ cohort.size }}</td>
            <td v-for="retention in cohort.retention" :key="retention.month" class="p-2 text-center">
              <div 
                class="rounded px-2 py-1 font-medium"
                :style="{ backgroundColor: getHeatmapColor(retention.rate), color: retention.rate > 50 ? '#fff' : '#1e293b' }"
              >
                {{ retention.rate }}%
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div class="mt-4 flex items-center gap-4 text-xs text-slate-600 dark:text-slate-400">
      <span>Retention Rate:</span>
      <div class="flex items-center gap-2">
        <div class="w-4 h-4 rounded" style="background-color: #ef4444"></div>
        <span>0-25%</span>
      </div>
      <div class="flex items-center gap-2">
        <div class="w-4 h-4 rounded" style="background-color: #f59e0b"></div>
        <span>25-50%</span>
      </div>
      <div class="flex items-center gap-2">
        <div class="w-4 h-4 rounded" style="background-color: #10b981"></div>
        <span>50-75%</span>
      </div>
      <div class="flex items-center gap-2">
        <div class="w-4 h-4 rounded" style="background-color: #3b82f6"></div>
        <span>75-100%</span>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'CohortAnalysis',
  props: {
    data: {
      type: Array,
      default: () => []
    },
    loading: {
      type: Boolean,
      default: false
    }
  },
  computed: {
    cohorts() {
      return this.data
    }
  },
  methods: {
    getHeatmapColor(rate) {
      if (rate >= 75) return '#3b82f6'  // blue
      if (rate >= 50) return '#10b981'  // green
      if (rate >= 25) return '#f59e0b'  // amber
      return '#ef4444'  // red
    }
  }
}
</script>
