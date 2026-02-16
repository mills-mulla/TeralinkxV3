<template>
  <div class="bg-gradient-to-r from-blue-500 to-purple-600 rounded-xl p-6 text-white shadow-lg">
    <div class="flex items-center justify-between mb-4">
      <h2 class="text-lg font-semibold flex items-center gap-2">
        <div class="w-2 h-2 bg-white rounded-full animate-pulse"></div>
        Real-Time Monitor
      </h2>
      <span class="text-xs opacity-75">Updates every 5s</span>
    </div>
    
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
      <!-- Today's Revenue -->
      <div class="bg-white/10 backdrop-blur-sm rounded-lg p-4">
        <div class="flex items-center gap-2 mb-2">
          <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
            <path d="M11.8 10.9c-2.27-.59-3-1.2-3-2.15 0-1.09 1.01-1.85 2.7-1.85 1.78 0 2.44.85 2.5 2.1h2.21c-.07-1.72-1.12-3.3-3.21-3.81V3h-3v2.16c-1.94.42-3.5 1.68-3.5 3.61 0 2.31 1.91 3.46 4.7 4.13 2.5.6 3 1.48 3 2.41 0 .69-.49 1.79-2.7 1.79-2.06 0-2.87-.92-2.98-2.1h-2.2c.12 2.19 1.76 3.42 3.68 3.83V21h3v-2.15c1.95-.37 3.5-1.5 3.5-3.55 0-2.84-2.43-3.81-4.7-4.4z"/>
          </svg>
          <span class="text-sm opacity-90">Today's Revenue</span>
        </div>
        <p class="text-3xl font-bold">KSh {{ formatNumber(todayRevenue) }}</p>
        <p class="text-xs opacity-75 mt-1">{{ todayTransactions }} transactions</p>
      </div>

      <!-- Online Users -->
      <div class="bg-white/10 backdrop-blur-sm rounded-lg p-4">
        <div class="flex items-center gap-2 mb-2">
          <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
            <path d="M16 11c1.66 0 2.99-1.34 2.99-3S17.66 5 16 5c-1.66 0-3 1.34-3 3s1.34 3 3 3zm-8 0c1.66 0 2.99-1.34 2.99-3S9.66 5 8 5C6.34 5 5 6.34 5 8s1.34 3 3 3zm0 2c-2.33 0-7 1.17-7 3.5V19h14v-2.5c0-2.33-4.67-3.5-7-3.5zm8 0c-.29 0-.62.02-.97.05 1.16.84 1.97 1.97 1.97 3.45V19h6v-2.5c0-2.33-4.67-3.5-7-3.5z"/>
          </svg>
          <span class="text-sm opacity-90">Online Users</span>
        </div>
        <p class="text-3xl font-bold">{{ onlineUsers }}</p>
        <p class="text-xs opacity-75 mt-1">{{ activeSessions }} active sessions</p>
      </div>

      <!-- Avg Response Time -->
      <div class="bg-white/10 backdrop-blur-sm rounded-lg p-4">
        <div class="flex items-center gap-2 mb-2">
          <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
            <path d="M11.99 2C6.47 2 2 6.48 2 12s4.47 10 9.99 10C17.52 22 22 17.52 22 12S17.52 2 11.99 2zM12 20c-4.42 0-8-3.58-8-8s3.58-8 8-8 8 3.58 8 8-3.58 8-8 8zm.5-13H11v6l5.25 3.15.75-1.23-4.5-2.67z"/>
          </svg>
          <span class="text-sm opacity-90">Avg Response</span>
        </div>
        <p class="text-3xl font-bold">{{ avgResponseTime }}ms</p>
        <p class="text-xs opacity-75 mt-1" :class="responseStatus === 'good' ? 'text-emerald-200' : 'text-amber-200'">
          {{ responseStatus === 'good' ? 'Excellent' : 'Normal' }}
        </p>
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
      updateInterval: null
    }
  },
  computed: {
    responseStatus() {
      return this.avgResponseTime < 200 ? 'good' : 'normal'
    }
  },
  mounted() {
    this.fetchRealTimeData()
    // Update every 5 seconds
    this.updateInterval = setInterval(() => {
      this.fetchRealTimeData()
    }, 5000)
  },
  beforeUnmount() {
    if (this.updateInterval) {
      clearInterval(this.updateInterval)
    }
  },
  methods: {
    async fetchRealTimeData() {
      try {
        const startTime = Date.now()
        const metrics = await this.makeRequest('get', 'suapi/dashboard-metrics/', null, true)
        
        this.todayRevenue = metrics.totalRevenue || 0
        this.todayTransactions = metrics.totalPackagesSold || 0
        this.onlineUsers = metrics.activeUsers || 0
        this.activeSessions = metrics.activeUsers || 0
        this.avgResponseTime = Math.round(Date.now() - startTime)
      } catch (error) {
        // Silent fail for real-time updates
      }
    },
    
    formatNumber(num) {
      return new Intl.NumberFormat().format(Math.round(num))
    }
  }
}
</script>

<style scoped>
@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.animate-pulse {
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}
</style>
