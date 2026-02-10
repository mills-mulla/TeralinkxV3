<template>
  <div class="space-y-4">
    <div class="flex items-center justify-between">
      <h2 class="text-lg font-semibold text-slate-900 dark:text-white">A/B Testing Experiments</h2>
      <button class="px-4 py-2 bg-blue-500 hover:bg-blue-600 text-white text-sm rounded-lg transition-colors">
        New Experiment
      </button>
    </div>

    <div v-if="loading" class="text-center py-8 text-slate-400">Loading...</div>

    <div v-else class="space-y-4">
      <div
        v-for="exp in data.experiments"
        :key="exp.id"
        class="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-5"
      >
        <div class="flex items-center justify-between mb-4">
          <div>
            <h3 class="text-sm font-medium text-slate-900 dark:text-white">{{ exp.name }}</h3>
            <p class="text-xs text-slate-500 dark:text-slate-400 mt-1">Started: {{ exp.start_date }}</p>
          </div>
          <span class="px-3 py-1 rounded-full text-xs font-medium" :class="getStatusBadge(exp.status)">
            {{ exp.status }}
          </span>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
          <div
            v-for="variant in exp.variants"
            :key="variant.name"
            class="p-4 rounded-lg border-2"
            :class="variant.name === exp.winner ? 'border-emerald-500 bg-emerald-50 dark:bg-emerald-500/10' : 'border-slate-200 dark:border-slate-700'"
          >
            <div class="flex items-center justify-between mb-2">
              <span class="text-sm font-medium text-slate-900 dark:text-white">{{ variant.name }}</span>
              <svg v-if="variant.name === exp.winner" class="w-5 h-5 text-emerald-500" fill="currentColor" viewBox="0 0 24 24">
                <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
              </svg>
            </div>
            <div class="space-y-2">
              <div class="flex justify-between text-xs">
                <span class="text-slate-600 dark:text-slate-400">Participants</span>
                <span class="font-semibold text-slate-900 dark:text-white">{{ variant.participants }}</span>
              </div>
              <div class="flex justify-between text-xs">
                <span class="text-slate-600 dark:text-slate-400">Conversions</span>
                <span class="font-semibold text-slate-900 dark:text-white">{{ variant.conversions }}</span>
              </div>
              <div class="flex justify-between text-xs">
                <span class="text-slate-600 dark:text-slate-400">Conv. Rate</span>
                <span class="font-bold text-blue-600 dark:text-blue-400">{{ variant.conversion_rate }}%</span>
              </div>
              <div class="flex justify-between text-xs">
                <span class="text-slate-600 dark:text-slate-400">Revenue</span>
                <span class="font-semibold text-emerald-600 dark:text-emerald-400">KSh {{ formatNumber(variant.revenue) }}</span>
              </div>
            </div>
          </div>
        </div>

        <div class="flex items-center justify-between p-3 bg-slate-50 dark:bg-slate-700/50 rounded-lg">
          <div class="flex items-center gap-2">
            <svg class="w-4 h-4 text-blue-500" fill="currentColor" viewBox="0 0 24 24">
              <path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zM9 17H7v-7h2v7zm4 0h-2V7h2v10zm4 0h-2v-4h2v4z"/>
            </svg>
            <span class="text-xs text-slate-600 dark:text-slate-400">Statistical Confidence</span>
          </div>
          <span class="text-sm font-bold" :class="exp.confidence >= 95 ? 'text-emerald-600 dark:text-emerald-400' : 'text-amber-600 dark:text-amber-400'">
            {{ exp.confidence }}%
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ABTesting',
  props: {
    data: {
      type: Object,
      default: () => ({ experiments: [] })
    },
    loading: {
      type: Boolean,
      default: false
    }
  },
  methods: {
    getStatusBadge(status) {
      const badges = {
        'running': 'bg-blue-100 dark:bg-blue-500/20 text-blue-700 dark:text-blue-400',
        'completed': 'bg-emerald-100 dark:bg-emerald-500/20 text-emerald-700 dark:text-emerald-400',
        'paused': 'bg-amber-100 dark:bg-amber-500/20 text-amber-700 dark:text-amber-400',
        'draft': 'bg-slate-100 dark:bg-slate-700 text-slate-700 dark:text-slate-400'
      }
      return badges[status] || 'bg-slate-100 dark:bg-slate-700'
    },
    formatNumber(num) {
      return new Intl.NumberFormat().format(num)
    }
  }
}
</script>
