<template>
  <div class="space-y-4">
    <!-- Key Financial Metrics -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
      <div class="bg-white dark:bg-slate-800 rounded-xl p-4 border border-slate-200 dark:border-slate-700">
        <div class="flex items-center gap-2 mb-2">
          <svg class="w-5 h-5 text-blue-500" fill="currentColor" viewBox="0 0 24 24">
            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1.41 16.09V20h-2.67v-1.93c-1.71-.36-3.16-1.46-3.27-3.4h1.96c.1 1.05.82 1.87 2.65 1.87 1.96 0 2.4-.98 2.4-1.59 0-.83-.44-1.61-2.67-2.14-2.48-.6-4.18-1.62-4.18-3.67 0-1.72 1.39-2.84 3.11-3.21V4h2.67v1.95c1.86.45 2.79 1.86 2.85 3.39H14.3c-.05-1.11-.64-1.87-2.22-1.87-1.5 0-2.4.68-2.4 1.64 0 .84.65 1.39 2.67 1.91s4.18 1.39 4.18 3.91c-.01 1.83-1.38 2.83-3.12 3.16z"/>
          </svg>
          <span class="text-xs text-slate-600 dark:text-slate-400">MRR</span>
        </div>
        <p class="text-2xl font-bold text-slate-900 dark:text-white">KSh {{ formatNumber(metrics.mrr) }}</p>
        <p class="text-xs text-emerald-600 dark:text-emerald-400 mt-1">+{{ metrics.growth_rate }}% growth</p>
      </div>

      <div class="bg-white dark:bg-slate-800 rounded-xl p-4 border border-slate-200 dark:border-slate-700">
        <div class="flex items-center gap-2 mb-2">
          <svg class="w-5 h-5 text-emerald-500" fill="currentColor" viewBox="0 0 24 24">
            <path d="M16 6l2.29 2.29-4.88 4.88-4-4L2 16.59 3.41 18l6-6 4 4 6.3-6.29L22 12V6z"/>
          </svg>
          <span class="text-xs text-slate-600 dark:text-slate-400">ARR</span>
        </div>
        <p class="text-2xl font-bold text-slate-900 dark:text-white">KSh {{ formatNumber(metrics.arr) }}</p>
        <p class="text-xs text-slate-500 dark:text-slate-400 mt-1">Annual recurring</p>
      </div>

      <div class="bg-white dark:bg-slate-800 rounded-xl p-4 border border-slate-200 dark:border-slate-700">
        <div class="flex items-center gap-2 mb-2">
          <svg class="w-5 h-5 text-purple-500" fill="currentColor" viewBox="0 0 24 24">
            <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/>
          </svg>
          <span class="text-xs text-slate-600 dark:text-slate-400">ARPU</span>
        </div>
        <p class="text-2xl font-bold text-slate-900 dark:text-white">KSh {{ formatNumber(metrics.arpu) }}</p>
        <p class="text-xs text-slate-500 dark:text-slate-400 mt-1">Per user/month</p>
      </div>

      <div class="bg-white dark:bg-slate-800 rounded-xl p-4 border border-slate-200 dark:border-slate-700">
        <div class="flex items-center gap-2 mb-2">
          <svg class="w-5 h-5 text-amber-500" fill="currentColor" viewBox="0 0 24 24">
            <path d="M12 17.27L18.18 21l-1.64-7.03L22 9.24l-7.19-.61L12 2 9.19 8.63 2 9.24l5.46 4.73L5.82 21z"/>
          </svg>
          <span class="text-xs text-slate-600 dark:text-slate-400">LTV</span>
        </div>
        <p class="text-2xl font-bold text-slate-900 dark:text-white">KSh {{ formatNumber(metrics.ltv) }}</p>
        <p class="text-xs text-slate-500 dark:text-slate-400 mt-1">Lifetime value</p>
      </div>
    </div>

    <!-- Package Performance -->
    <div class="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-5">
      <div class="flex items-center gap-2 mb-4">
        <svg class="w-5 h-5 text-cyan-500" fill="currentColor" viewBox="0 0 24 24">
          <path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zM9 17H7v-7h2v7zm4 0h-2V7h2v10zm4 0h-2v-4h2v4z"/>
        </svg>
        <h3 class="text-sm font-medium text-slate-900 dark:text-white">Package Performance & Margins</h3>
      </div>

      <div v-if="loading" class="text-center py-8 text-slate-400">Loading...</div>

      <div v-else class="overflow-x-auto">
        <table class="w-full text-xs">
          <thead class="border-b border-slate-200 dark:border-slate-700">
            <tr>
              <th class="text-left p-2 text-slate-600 dark:text-slate-400">Package</th>
              <th class="text-center p-2 text-slate-600 dark:text-slate-400">Sales</th>
              <th class="text-center p-2 text-slate-600 dark:text-slate-400">Revenue</th>
              <th class="text-center p-2 text-slate-600 dark:text-slate-400">Profit</th>
              <th class="text-center p-2 text-slate-600 dark:text-slate-400">Margin</th>
            </tr>
          </thead>
          <tbody>
            <tr 
              v-for="pkg in packages" 
              :key="pkg.name"
              class="border-b border-slate-200 dark:border-slate-700"
            >
              <td class="p-2 font-medium text-slate-900 dark:text-white">{{ pkg.name }}</td>
              <td class="p-2 text-center text-slate-900 dark:text-white">{{ pkg.sales }}</td>
              <td class="p-2 text-center text-slate-900 dark:text-white">KSh {{ formatNumber(pkg.revenue) }}</td>
              <td class="p-2 text-center text-slate-900 dark:text-white">KSh {{ formatNumber(pkg.profit) }}</td>
              <td class="p-2 text-center">
                <span 
                  class="px-2 py-1 rounded-full font-medium"
                  :class="pkg.margin >= 50 ? 'bg-emerald-100 dark:bg-emerald-500/20 text-emerald-700 dark:text-emerald-400' : pkg.margin >= 30 ? 'bg-blue-100 dark:bg-blue-500/20 text-blue-700 dark:text-blue-400' : 'bg-amber-100 dark:bg-amber-500/20 text-amber-700 dark:text-amber-400'"
                >
                  {{ pkg.margin }}%
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'FinancialAnalytics',
  props: {
    metrics: {
      type: Object,
      default: () => ({
        mrr: 0,
        arr: 0,
        arpu: 0,
        ltv: 0,
        growth_rate: 0
      })
    },
    packages: {
      type: Array,
      default: () => []
    },
    loading: {
      type: Boolean,
      default: false
    }
  },
  methods: {
    formatNumber(num) {
      return new Intl.NumberFormat().format(num)
    }
  }
}
</script>
