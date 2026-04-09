<template>
  <div class="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-5">
    <div class="flex items-center justify-between mb-4">
      <div class="flex items-center gap-2">
        <svg class="w-5 h-5 text-rose-500" fill="currentColor" viewBox="0 0 24 24">
          <path d="M3 13h2v-2H3v2zm0 4h2v-2H3v2zm0-8h2V7H3v2zm4 4h14v-2H7v2zm0 4h14v-2H7v2zM7 7v2h14V7H7z"/>
        </svg>
        <h3 class="text-sm font-medium text-slate-900 dark:text-white">Conversion Funnel Analysis</h3>
      </div>
      <div class="text-right">
        <p class="text-xs text-slate-600 dark:text-slate-400">Overall Conversion</p>
        <p class="text-lg font-bold text-emerald-600 dark:text-emerald-400">{{ data.conversion_rate }}%</p>
      </div>
    </div>

    <div v-if="loading" class="text-center py-8 text-slate-400">Loading...</div>

    <div v-else class="space-y-3">
      <!-- Funnel Stages -->
      <div 
        v-for="(stage, idx) in data.stages" 
        :key="idx"
        class="relative"
      >
        <div class="flex items-center gap-4">
          <!-- Stage Number -->
          <div class="w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold" :class="getStageColor(idx)">
            {{ idx + 1 }}
          </div>

          <!-- Stage Info -->
          <div class="flex-1">
            <div class="flex items-center justify-between mb-1">
              <span class="text-sm font-medium text-slate-900 dark:text-white">{{ stage.name }}</span>
              <div class="flex items-center gap-3">
                <span class="text-sm font-bold text-slate-900 dark:text-white">{{ stage.users }}</span>
                <span class="text-xs px-2 py-1 rounded-full" :class="getRateColor(stage.rate)">
                  {{ stage.rate }}%
                </span>
              </div>
            </div>

            <!-- Progress Bar -->
            <div class="h-2 bg-slate-200 dark:bg-slate-700 rounded-full overflow-hidden">
              <div 
                class="h-full transition-all duration-500"
                :class="getBarColor(idx)"
                :style="{ width: stage.rate + '%' }"
              ></div>
            </div>

            <!-- Drop-off Indicator -->
            <div v-if="stage.dropoff > 0" class="mt-1 flex items-center gap-1 text-xs text-red-600 dark:text-red-400">
              <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 24 24">
                <path d="M16 18l2.29-2.29-4.88-4.88-4 4L2 7.41 3.41 6l6 6 4-4 6.3 6.29L22 12v6z"/>
              </svg>
              <span>{{ stage.dropoff }} users dropped</span>
            </div>
          </div>
        </div>

        <!-- Connector Line -->
        <div v-if="idx < data.stages.length - 1" class="ml-4 h-4 w-0.5 bg-slate-300 dark:bg-slate-600"></div>
      </div>
    </div>

    <!-- Insights -->
    <div class="mt-6 p-4 bg-amber-50 dark:bg-amber-500/10 border border-amber-200 dark:border-amber-500/20 rounded-lg">
      <div class="flex items-start gap-3">
        <svg class="w-5 h-5 text-amber-600 dark:text-amber-400 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 24 24">
          <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z"/>
        </svg>
        <div>
          <p class="text-sm font-medium text-amber-900 dark:text-amber-400">Biggest Drop-off Point</p>
          <p class="text-xs text-amber-700 dark:text-amber-500 mt-1">
            Most users are dropping at <strong>{{ data.biggest_dropoff }}</strong>. Focus optimization efforts here.
          </p>
        </div>
      </div>
    </div>

    <!-- Summary Stats -->
    <div class="mt-4 grid grid-cols-2 gap-4">
      <div class="text-center p-3 bg-slate-50 dark:bg-slate-700/50 rounded-lg">
        <p class="text-xs text-slate-600 dark:text-slate-400">Total Signups</p>
        <p class="text-xl font-bold text-slate-900 dark:text-white">{{ data.total_signups }}</p>
      </div>
      <div class="text-center p-3 bg-slate-50 dark:bg-slate-700/50 rounded-lg">
        <p class="text-xs text-slate-600 dark:text-slate-400">Repeat Customers</p>
        <p class="text-xl font-bold text-emerald-600 dark:text-emerald-400">{{ data.repeat_customers }}</p>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'FunnelAnalysis',
  props: {
    data: {
      type: Object,
      default: () => ({
        stages: [],
        conversion_rate: 0,
        biggest_dropoff: '',
        total_signups: 0,
        repeat_customers: 0
      })
    },
    loading: {
      type: Boolean,
      default: false
    }
  },
  methods: {
    getStageColor(idx) {
      const colors = [
        'bg-blue-500 text-white',
        'bg-purple-500 text-white',
        'bg-cyan-500 text-white',
        'bg-emerald-500 text-white',
        'bg-amber-500 text-white',
        'bg-rose-500 text-white'
      ]
      return colors[idx] || 'bg-slate-500 text-white'
    },
    getBarColor(idx) {
      const colors = [
        'bg-blue-500',
        'bg-purple-500',
        'bg-cyan-500',
        'bg-emerald-500',
        'bg-amber-500',
        'bg-rose-500'
      ]
      return colors[idx] || 'bg-slate-500'
    },
    getRateColor(rate) {
      if (rate >= 75) return 'bg-emerald-100 dark:bg-emerald-500/20 text-emerald-700 dark:text-emerald-400'
      if (rate >= 50) return 'bg-blue-100 dark:bg-blue-500/20 text-blue-700 dark:text-blue-400'
      if (rate >= 25) return 'bg-amber-100 dark:bg-amber-500/20 text-amber-700 dark:text-amber-400'
      return 'bg-red-100 dark:bg-red-500/20 text-red-700 dark:text-red-400'
    }
  }
}
</script>
