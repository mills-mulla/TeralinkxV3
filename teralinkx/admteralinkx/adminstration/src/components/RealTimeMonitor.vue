<template>
  <div class="bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl overflow-hidden">
    <!-- Header bar -->
    <div class="flex items-center justify-between px-4 py-2.5 border-b border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-900/50">
      <div class="flex items-center gap-2">
        <span class="relative flex h-2 w-2">
          <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
          <span class="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
        </span>
        <span class="text-xs font-semibold text-slate-700 dark:text-slate-300">Live Monitor</span>
      </div>
      <div class="flex items-center gap-3">
        <span class="text-[10px] text-slate-400">{{ lastUpdated }}</span>
        <span class="text-[10px] px-1.5 py-0.5 rounded bg-emerald-100 dark:bg-emerald-500/20 text-emerald-700 dark:text-emerald-400">5s</span>
      </div>
    </div>

    <!-- Metrics row -->
    <div class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 divide-x divide-y md:divide-y-0 divide-slate-200 dark:divide-slate-700">

      <!-- Today's Revenue -->
      <div class="px-4 py-3">
        <p class="text-[10px] text-slate-500 dark:text-slate-400 mb-1">Today's Revenue</p>
        <div class="flex items-center gap-1.5">
          <span class="text-sm font-bold text-slate-900 dark:text-white" :class="hideRevenue ? 'blur-sm select-none' : ''">
            KSh {{ formatNumber(todayRevenue) }}
          </span>
          <button @click="hideRevenue = !hideRevenue" class="text-slate-300 dark:text-slate-600 hover:text-slate-500 dark:hover:text-slate-400 transition-colors">
            <svg v-if="hideRevenue" class="w-3 h-3" fill="currentColor" viewBox="0 0 24 24"><path d="M12 4.5C7 4.5 2.73 7.61 1 12c1.73 4.39 6 7.5 11 7.5s9.27-3.11 11-7.5c-1.73-4.39-6-7.5-11-7.5zM12 17c-2.76 0-5-2.24-5-5s2.24-5 5-5 5 2.24 5 5-2.24 5-5 5zm0-8c-1.66 0-3 1.34-3 3s1.34 3 3 3 3-1.34 3-3-1.34-3-3-3z"/></svg>
            <svg v-else class="w-3 h-3" fill="currentColor" viewBox="0 0 24 24"><path d="M12 7c2.76 0 5 2.24 5 5 0 .65-.13 1.26-.36 1.83l2.92 2.92c1.51-1.26 2.7-2.89 3.43-4.75-1.73-4.39-6-7.5-11-7.5-1.4 0-2.74.25-3.98.7l2.16 2.16C10.74 7.13 11.35 7 12 7zM2 4.27l2.28 2.28.46.46C3.08 8.3 1.78 10.02 1 12c1.73 4.39 6 7.5 11 7.5 1.55 0 3.03-.3 4.38-.84l.42.42L19.73 22 21 20.73 3.27 3 2 4.27zM7.53 9.8l1.55 1.55c-.05.21-.08.43-.08.65 0 1.66 1.34 3 3 3 .22 0 .44-.03.65-.08l1.55 1.55c-.67.33-1.41.53-2.2.53-2.76 0-5-2.24-5-5 0-.79.2-1.53.53-2.2zm4.31-.78l3.15 3.15.02-.16c0-1.66-1.34-3-3-3l-.17.01z"/></svg>
          </button>
        </div>
        <p class="text-[10px] text-slate-400 mt-0.5">{{ todayTransactions }} txns</p>
      </div>

      <!-- Online Users -->
      <div class="px-4 py-3">
        <p class="text-[10px] text-slate-500 dark:text-slate-400 mb-1">Online Now</p>
        <p class="text-sm font-bold text-slate-900 dark:text-white">{{ onlineUsers }}</p>
        <p class="text-[10px] text-slate-400 mt-0.5">{{ activeSessions }} sessions</p>
      </div>

      <!-- Active Ratio -->
      <div class="px-4 py-3">
        <p class="text-[10px] text-slate-500 dark:text-slate-400 mb-1">Active Ratio</p>
        <p class="text-sm font-bold" :class="activeRatio > 50 ? 'text-emerald-600 dark:text-emerald-400' : 'text-amber-600 dark:text-amber-400'">{{ activeRatio }}%</p>
        <p class="text-[10px] text-slate-400 mt-0.5">clients online</p>
      </div>

      <!-- New Today -->
      <div class="px-4 py-3">
        <p class="text-[10px] text-slate-500 dark:text-slate-400 mb-1">New Today</p>
        <p class="text-sm font-bold text-slate-900 dark:text-white">{{ newClientsToday }}</p>
        <p class="text-[10px] text-slate-400 mt-0.5">signups</p>
      </div>

      <!-- Response Time -->
      <div class="px-4 py-3">
        <p class="text-[10px] text-slate-500 dark:text-slate-400 mb-1">API Response</p>
        <p class="text-sm font-bold" :class="avgResponseTime < 200 ? 'text-emerald-600 dark:text-emerald-400' : avgResponseTime < 500 ? 'text-amber-600 dark:text-amber-400' : 'text-rose-600 dark:text-rose-400'">
          {{ avgResponseTime }}ms
        </p>
        <p class="text-[10px] mt-0.5" :class="avgResponseTime < 200 ? 'text-emerald-500' : avgResponseTime < 500 ? 'text-amber-500' : 'text-rose-500'">
          {{ avgResponseTime < 200 ? 'Excellent' : avgResponseTime < 500 ? 'Normal' : 'Slow' }}
        </p>
      </div>

      <!-- Packages Sold Today -->
      <div class="px-4 py-3">
        <p class="text-[10px] text-slate-500 dark:text-slate-400 mb-1">Packages Sold</p>
        <p class="text-sm font-bold text-slate-900 dark:text-white">{{ todayTransactions }}</p>
        <p class="text-[10px] text-slate-400 mt-0.5">today</p>
      </div>

    </div>

    <!-- Activity ticker -->
    <div v-if="recentActivity.length > 0" class="border-t border-slate-200 dark:border-slate-700 px-4 py-2 flex items-center gap-3 overflow-hidden">
      <span class="text-[10px] font-medium text-slate-400 flex-shrink-0">LIVE</span>
      <div class="flex-1 overflow-hidden">
        <transition name="ticker" mode="out-in">
          <p :key="tickerIndex" class="text-[10px] text-slate-600 dark:text-slate-400 truncate">
            <span class="font-medium text-slate-900 dark:text-white">{{ recentActivity[tickerIndex]?.user }}</span>
            {{ recentActivity[tickerIndex]?.description }}
            <span class="text-slate-400 ml-1">{{ recentActivity[tickerIndex]?.time }}</span>
          </p>
        </transition>
      </div>
    </div>
  </div>
</template>

<script>
import { useApi } from '../composables/useApi'

export default {
  name: 'RealTimeMonitor',
  setup() {
    const { makeRequest } = useApi()
    return { makeRequest }
  },
  data() {
    return {
      todayRevenue: 0,
      todayTransactions: 0,
      onlineUsers: 0,
      activeSessions: 0,
      avgResponseTime: 0,
      activeRatio: 0,
      newClientsToday: 0,
      recentActivity: [],
      tickerIndex: 0,
      hideRevenue: false,
      lastUpdated: 'Loading...',
      updateInterval: null,
      tickerInterval: null
    }
  },
  mounted() {
    this.fetchRealTimeData()
    this.updateInterval = setInterval(() => this.fetchRealTimeData(), 5000)
    this.tickerInterval = setInterval(() => {
      if (this.recentActivity.length > 1) {
        this.tickerIndex = (this.tickerIndex + 1) % this.recentActivity.length
      }
    }, 3000)
  },
  beforeUnmount() {
    clearInterval(this.updateInterval)
    clearInterval(this.tickerInterval)
  },
  methods: {
    async fetchRealTimeData() {
      try {
        const startTime = Date.now()
        const [metrics, activity] = await Promise.all([
          this.makeRequest('get', 'suapi/dashboard-metrics/', null, true),
          this.makeRequest('get', 'suapi/dashboard-metrics/recent-activity/', null, false).catch(() => ({ data: [] }))
        ])
        this.avgResponseTime = Math.round(Date.now() - startTime)
        this.todayRevenue = metrics.totalRevenue || 0
        this.todayTransactions = metrics.totalPackagesSold || 0
        this.onlineUsers = metrics.activeUsers || 0
        this.activeSessions = metrics.activeUsers || 0
        this.activeRatio = metrics.activeRatio || 0
        this.newClientsToday = metrics.newClientsToday || 0
        this.recentActivity = (activity.data || []).slice(0, 10)
        this.lastUpdated = new Date().toLocaleTimeString()
      } catch (error) {
        this.lastUpdated = 'Error'
      }
    },
    formatNumber(num) {
      return new Intl.NumberFormat().format(Math.round(num))
    }
  }
}
</script>

<style scoped>
.ticker-enter-active, .ticker-leave-active { transition: all 0.4s ease; }
.ticker-enter-from { opacity: 0; transform: translateY(8px); }
.ticker-leave-to { opacity: 0; transform: translateY(-8px); }
@keyframes ping { 75%, 100% { transform: scale(2); opacity: 0; } }
.animate-ping { animation: ping 1.5s cubic-bezier(0, 0, 0.2, 1) infinite; }
</style>
