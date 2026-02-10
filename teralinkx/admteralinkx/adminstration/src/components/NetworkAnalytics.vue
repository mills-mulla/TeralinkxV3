<template>
  <div class="space-y-4">
    <!-- Overall Network Health -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
      <div class="bg-white dark:bg-slate-800 rounded-xl p-4 border border-slate-200 dark:border-slate-700">
        <div class="flex items-center gap-2 mb-2">
          <svg class="w-5 h-5 text-blue-500" fill="currentColor" viewBox="0 0 24 24">
            <path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z"/>
          </svg>
          <span class="text-xs text-slate-600 dark:text-slate-400">Total Locations</span>
        </div>
        <p class="text-2xl font-bold text-slate-900 dark:text-white">{{ data.overall?.total_locations || 0 }}</p>
      </div>

      <div class="bg-white dark:bg-slate-800 rounded-xl p-4 border border-slate-200 dark:border-slate-700">
        <div class="flex items-center gap-2 mb-2">
          <svg class="w-5 h-5 text-emerald-500" fill="currentColor" viewBox="0 0 24 24">
            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
          </svg>
          <span class="text-xs text-slate-600 dark:text-slate-400">Capacity</span>
        </div>
        <p class="text-2xl font-bold text-slate-900 dark:text-white">{{ data.overall?.total_capacity || 0 }}</p>
      </div>

      <div class="bg-white dark:bg-slate-800 rounded-xl p-4 border border-slate-200 dark:border-slate-700">
        <div class="flex items-center gap-2 mb-2">
          <svg class="w-5 h-5 text-purple-500" fill="currentColor" viewBox="0 0 24 24">
            <path d="M11.99 2C6.47 2 2 6.48 2 12s4.47 10 9.99 10C17.52 22 22 17.52 22 12S17.52 2 11.99 2zM12 20c-4.42 0-8-3.58-8-8s3.58-8 8-8 8 3.58 8 8-3.58 8-8 8zm.5-13H11v6l5.25 3.15.75-1.23-4.5-2.67z"/>
          </svg>
          <span class="text-xs text-slate-600 dark:text-slate-400">Active Sessions</span>
        </div>
        <p class="text-2xl font-bold text-slate-900 dark:text-white">{{ data.overall?.total_active_sessions || 0 }}</p>
      </div>

      <div class="bg-white dark:bg-slate-800 rounded-xl p-4 border border-slate-200 dark:border-slate-700">
        <div class="flex items-center gap-2 mb-2">
          <svg class="w-5 h-5 text-amber-500" fill="currentColor" viewBox="0 0 24 24">
            <path d="M3.5 18.49l6-6.01 4 4L22 6.92l-1.41-1.41-7.09 7.97-4-4L2 16.99z"/>
          </svg>
          <span class="text-xs text-slate-600 dark:text-slate-400">Utilization</span>
        </div>
        <p class="text-2xl font-bold text-slate-900 dark:text-white">{{ data.overall?.overall_utilization || 0 }}%</p>
      </div>
    </div>

    <!-- Location Health Status -->
    <div class="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-5">
      <div class="flex items-center gap-2 mb-4">
        <svg class="w-5 h-5 text-cyan-500" fill="currentColor" viewBox="0 0 24 24">
          <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
        </svg>
        <h3 class="text-sm font-medium text-slate-900 dark:text-white">Location Network Health</h3>
      </div>

      <div v-if="loading" class="text-center py-8 text-slate-400">Loading...</div>

      <div v-else class="space-y-2">
        <div 
          v-for="location in data.locations" 
          :key="location.location_id"
          class="p-4 rounded-lg border transition-colors"
          :class="getLocationBorder(location.health_status)"
        >
          <div class="flex items-center justify-between mb-2">
            <div class="flex items-center gap-3">
              <div class="w-3 h-3 rounded-full" :class="getHealthDot(location.health_status)"></div>
              <div>
                <p class="text-sm font-medium text-slate-900 dark:text-white">{{ location.location_name }}</p>
                <p class="text-xs text-slate-500 dark:text-slate-400">{{ location.router_ip }}</p>
              </div>
            </div>
            <span class="px-3 py-1 rounded-full text-xs font-medium" :class="getHealthBadge(location.health_status)">
              {{ location.health_status }}
            </span>
          </div>

          <div class="grid grid-cols-4 gap-4 mt-3">
            <div>
              <p class="text-xs text-slate-600 dark:text-slate-400">Active</p>
              <p class="text-sm font-bold text-slate-900 dark:text-white">{{ location.active_sessions }}</p>
            </div>
            <div>
              <p class="text-xs text-slate-600 dark:text-slate-400">Capacity</p>
              <p class="text-sm font-bold text-slate-900 dark:text-white">{{ location.max_capacity }}</p>
            </div>
            <div>
              <p class="text-xs text-slate-600 dark:text-slate-400">Utilization</p>
              <p class="text-sm font-bold" :class="getUtilizationColor(location.utilization)">{{ location.utilization }}%</p>
            </div>
            <div>
              <p class="text-xs text-slate-600 dark:text-slate-400">Vouchers</p>
              <p class="text-sm font-bold text-slate-900 dark:text-white">{{ location.total_vouchers }}</p>
            </div>
          </div>

          <!-- Utilization Bar -->
          <div class="mt-3 h-2 bg-slate-200 dark:bg-slate-700 rounded-full overflow-hidden">
            <div 
              class="h-full transition-all duration-500"
              :class="getUtilizationBar(location.utilization)"
              :style="{ width: location.utilization + '%' }"
            ></div>
          </div>
        </div>
      </div>
    </div>

    <!-- Health Summary -->
    <div class="grid grid-cols-3 gap-4">
      <div class="bg-emerald-50 dark:bg-emerald-500/10 border border-emerald-200 dark:border-emerald-500/20 rounded-lg p-4">
        <p class="text-xs text-emerald-600 dark:text-emerald-400 mb-1">Healthy</p>
        <p class="text-2xl font-bold text-emerald-700 dark:text-emerald-300">{{ data.overall?.healthy_locations || 0 }}</p>
      </div>
      <div class="bg-amber-50 dark:bg-amber-500/10 border border-amber-200 dark:border-amber-500/20 rounded-lg p-4">
        <p class="text-xs text-amber-600 dark:text-amber-400 mb-1">Warning</p>
        <p class="text-2xl font-bold text-amber-700 dark:text-amber-300">{{ data.overall?.warning_locations || 0 }}</p>
      </div>
      <div class="bg-red-50 dark:bg-red-500/10 border border-red-200 dark:border-red-500/20 rounded-lg p-4">
        <p class="text-xs text-red-600 dark:text-red-400 mb-1">Critical</p>
        <p class="text-2xl font-bold text-red-700 dark:text-red-300">{{ data.overall?.critical_locations || 0 }}</p>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'NetworkAnalytics',
  props: {
    data: {
      type: Object,
      default: () => ({
        locations: [],
        overall: {}
      })
    },
    loading: {
      type: Boolean,
      default: false
    }
  },
  methods: {
    getHealthDot(status) {
      const dots = {
        'healthy': 'bg-emerald-500',
        'warning': 'bg-amber-500',
        'critical': 'bg-red-500'
      }
      return dots[status] || 'bg-slate-500'
    },
    getHealthBadge(status) {
      const badges = {
        'healthy': 'bg-emerald-100 dark:bg-emerald-500/20 text-emerald-700 dark:text-emerald-400',
        'warning': 'bg-amber-100 dark:bg-amber-500/20 text-amber-700 dark:text-amber-400',
        'critical': 'bg-red-100 dark:bg-red-500/20 text-red-700 dark:text-red-400'
      }
      return badges[status] || 'bg-slate-100 dark:bg-slate-700'
    },
    getLocationBorder(status) {
      const borders = {
        'healthy': 'border-emerald-200 dark:border-emerald-500/20 bg-emerald-50/50 dark:bg-emerald-500/5',
        'warning': 'border-amber-200 dark:border-amber-500/20 bg-amber-50/50 dark:bg-amber-500/5',
        'critical': 'border-red-200 dark:border-red-500/20 bg-red-50/50 dark:bg-red-500/5'
      }
      return borders[status] || 'border-slate-200 dark:border-slate-700'
    },
    getUtilizationColor(utilization) {
      if (utilization > 90) return 'text-red-600 dark:text-red-400'
      if (utilization > 70) return 'text-amber-600 dark:text-amber-400'
      return 'text-emerald-600 dark:text-emerald-400'
    },
    getUtilizationBar(utilization) {
      if (utilization > 90) return 'bg-red-500'
      if (utilization > 70) return 'bg-amber-500'
      return 'bg-emerald-500'
    }
  }
}
</script>
