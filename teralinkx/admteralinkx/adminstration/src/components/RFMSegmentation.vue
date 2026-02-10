<template>
  <div class="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-5">
    <div class="flex items-center justify-between mb-4">
      <div class="flex items-center gap-2">
        <svg class="w-5 h-5 text-indigo-500" fill="currentColor" viewBox="0 0 24 24">
          <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
        </svg>
        <h3 class="text-sm font-medium text-slate-900 dark:text-white">Customer Segmentation (RFM)</h3>
      </div>
    </div>

    <div v-if="loading" class="text-center py-8 text-slate-400">Loading...</div>

    <div v-else>
      <!-- Segment Summary -->
      <div class="grid grid-cols-2 md:grid-cols-3 gap-3 mb-4">
        <div 
          v-for="(data, segment) in summary" 
          :key="segment"
          class="p-3 rounded-lg border"
          :class="getSegmentStyle(segment)"
        >
          <div class="flex items-center gap-2 mb-1">
            <div class="w-2 h-2 rounded-full" :class="getSegmentDot(segment)"></div>
            <span class="text-xs font-medium">{{ segment }}</span>
          </div>
          <p class="text-xl font-bold">{{ data.count }}</p>
          <p class="text-xs opacity-75 mt-1">KSh {{ formatNumber(data.total_value) }}</p>
        </div>
      </div>

      <!-- Top Customers Table -->
      <div class="mt-4">
        <h4 class="text-xs font-medium text-slate-600 dark:text-slate-400 mb-2">Top Customers by RFM Score</h4>
        <div class="overflow-x-auto">
          <table class="w-full text-xs">
            <thead class="border-b border-slate-200 dark:border-slate-700">
              <tr>
                <th class="text-left p-2 text-slate-600 dark:text-slate-400">Customer</th>
                <th class="text-center p-2 text-slate-600 dark:text-slate-400">Segment</th>
                <th class="text-center p-2 text-slate-600 dark:text-slate-400">Recency</th>
                <th class="text-center p-2 text-slate-600 dark:text-slate-400">Frequency</th>
                <th class="text-center p-2 text-slate-600 dark:text-slate-400">Monetary</th>
                <th class="text-center p-2 text-slate-600 dark:text-slate-400">Score</th>
              </tr>
            </thead>
            <tbody>
              <tr 
                v-for="customer in topCustomers" 
                :key="customer.user_id"
                class="border-b border-slate-200 dark:border-slate-700"
              >
                <td class="p-2 text-slate-900 dark:text-white">{{ customer.username }}</td>
                <td class="p-2 text-center">
                  <span class="px-2 py-1 rounded-full text-xs" :class="getSegmentBadge(customer.segment)">
                    {{ customer.segment }}
                  </span>
                </td>
                <td class="p-2 text-center text-slate-900 dark:text-white">{{ customer.recency }}d</td>
                <td class="p-2 text-center text-slate-900 dark:text-white">{{ customer.frequency }}</td>
                <td class="p-2 text-center text-slate-900 dark:text-white">{{ formatNumber(customer.monetary) }}</td>
                <td class="p-2 text-center">
                  <span class="font-bold text-blue-600 dark:text-blue-400">{{ customer.rfm_score }}</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'RFMSegmentation',
  props: {
    segments: {
      type: Array,
      default: () => []
    },
    summary: {
      type: Object,
      default: () => ({})
    },
    loading: {
      type: Boolean,
      default: false
    }
  },
  computed: {
    topCustomers() {
      return this.segments.slice(0, 10).sort((a, b) => b.rfm_score - a.rfm_score)
    }
  },
  methods: {
    getSegmentStyle(segment) {
      const styles = {
        'Champions': 'bg-blue-50 dark:bg-blue-500/10 border-blue-200 dark:border-blue-500/20 text-blue-700 dark:text-blue-400',
        'Loyal': 'bg-emerald-50 dark:bg-emerald-500/10 border-emerald-200 dark:border-emerald-500/20 text-emerald-700 dark:text-emerald-400',
        'New': 'bg-purple-50 dark:bg-purple-500/10 border-purple-200 dark:border-purple-500/20 text-purple-700 dark:text-purple-400',
        'At Risk': 'bg-amber-50 dark:bg-amber-500/10 border-amber-200 dark:border-amber-500/20 text-amber-700 dark:text-amber-400',
        'Lost': 'bg-red-50 dark:bg-red-500/10 border-red-200 dark:border-red-500/20 text-red-700 dark:text-red-400',
        'Potential': 'bg-cyan-50 dark:bg-cyan-500/10 border-cyan-200 dark:border-cyan-500/20 text-cyan-700 dark:text-cyan-400'
      }
      return styles[segment] || 'bg-slate-50 dark:bg-slate-700 border-slate-200 dark:border-slate-600'
    },
    getSegmentDot(segment) {
      const dots = {
        'Champions': 'bg-blue-500',
        'Loyal': 'bg-emerald-500',
        'New': 'bg-purple-500',
        'At Risk': 'bg-amber-500',
        'Lost': 'bg-red-500',
        'Potential': 'bg-cyan-500'
      }
      return dots[segment] || 'bg-slate-500'
    },
    getSegmentBadge(segment) {
      const badges = {
        'Champions': 'bg-blue-100 dark:bg-blue-500/20 text-blue-700 dark:text-blue-400',
        'Loyal': 'bg-emerald-100 dark:bg-emerald-500/20 text-emerald-700 dark:text-emerald-400',
        'New': 'bg-purple-100 dark:bg-purple-500/20 text-purple-700 dark:text-purple-400',
        'At Risk': 'bg-amber-100 dark:bg-amber-500/20 text-amber-700 dark:text-amber-400',
        'Lost': 'bg-red-100 dark:bg-red-500/20 text-red-700 dark:text-red-400',
        'Potential': 'bg-cyan-100 dark:bg-cyan-500/20 text-cyan-700 dark:text-cyan-400'
      }
      return badges[segment] || 'bg-slate-100 dark:bg-slate-700'
    },
    formatNumber(num) {
      return new Intl.NumberFormat().format(num)
    }
  }
}
</script>
