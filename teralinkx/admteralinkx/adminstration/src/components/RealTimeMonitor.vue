<template>
  <div class="space-y-4">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div class="flex items-center gap-3">
        <div class="w-3 h-3 bg-emerald-500 rounded-full animate-pulse"></div>
        <h2 class="text-lg font-semibold text-slate-900 dark:text-white">Real-Time Monitoring</h2>
        <span class="text-xs text-slate-500 dark:text-slate-400">Updates every 5s</span>
      </div>
      <button 
        @click="toggleAutoRefresh"
        class="px-3 py-1.5 text-xs rounded-lg transition-colors"
        :class="autoRefresh ? 'bg-emerald-500 text-white' : 'bg-slate-200 dark:bg-slate-700 text-slate-900 dark:text-white'"
      >
        {{ autoRefresh ? 'Live' : 'Paused' }}
      </button>
    </div>

    <!-- Live Metrics -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
      <div class="bg-white dark:bg-slate-800 rounded-xl p-4 border border-slate-200 dark:border-slate-700">
        <div class="flex items-center gap-3 mb-2">
          <svg class="w-5 h-5 text-blue-500" fill="currentColor" viewBox="0 0 24 24">
            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
          </svg>
          <span class="text-xs text-slate-600 dark:text-slate-400">Active Sessions</span>
        </div>
        <p class="text-2xl font-bold text-slate-900 dark:text-white">{{ liveMetrics.activeSessions }}</p>
        <p class="text-xs text-emerald-600 dark:text-emerald-400 mt-1">+{{ liveMetrics.sessionChange }} in last min</p>
      </div>

      <div class="bg-white dark:bg-slate-800 rounded-xl p-4 border border-slate-200 dark:border-slate-700">
        <div class="flex items-center gap-3 mb-2">
          <svg class="w-5 h-5 text-emerald-500" fill="currentColor" viewBox="0 0 24 24">
            <path d="M11.8 10.9c-2.27-.59-3-1.2-3-2.15 0-1.09 1.01-1.85 2.7-1.85 1.78 0 2.44.85 2.5 2.1h2.21c-.07-1.72-1.12-3.3-3.21-3.81V3h-3v2.16c-1.94.42-3.5 1.68-3.5 3.61 0 2.31 1.91 3.46 4.7 4.13 2.5.6 3 1.48 3 2.41 0 .69-.49 1.79-2.7 1.79-2.06 0-2.87-.92-2.98-2.1h-2.2c.12 2.19 1.76 3.42 3.68 3.83V21h3v-2.15c1.95-.37 3.5-1.5 3.5-3.55 0-2.84-2.43-3.81-4.7-4.4z"/>
          </svg>
          <span class="text-xs text-slate-600 dark:text-slate-400">Revenue Today</span>
        </div>
        <p class="text-2xl font-bold text-slate-900 dark:text-white">KSh {{ formatNumber(liveMetrics.revenueToday) }}</p>
        <p class="text-xs text-blue-600 dark:text-blue-400 mt-1">{{ liveMetrics.transactionsToday }} transactions</p>
      </div>

      <div class="bg-white dark:bg-slate-800 rounded-xl p-4 border border-slate-200 dark:border-slate-700">
        <div class="flex items-center gap-3 mb-2">
          <svg class="w-5 h-5 text-purple-500" fill="currentColor" viewBox="0 0 24 24">
            <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/>
          </svg>
          <span class="text-xs text-slate-600 dark:text-slate-400">Online Users</span>
        </div>
        <p class="text-2xl font-bold text-slate-900 dark:text-white">{{ liveMetrics.onlineUsers }}</p>
        <p class="text-xs text-slate-500 dark:text-slate-400 mt-1">{{ liveMetrics.peakToday }} peak today</p>
      </div>

      <div class="bg-white dark:bg-slate-800 rounded-xl p-4 border border-slate-200 dark:border-slate-700">
        <div class="flex items-center gap-3 mb-2">
          <svg class="w-5 h-5 text-amber-500" fill="currentColor" viewBox="0 0 24 24">
            <path d="M13 3c-4.97 0-9 4.03-9 9H1l3.89 3.89.07.14L9 12H6c0-3.87 3.13-7 7-7s7 3.13 7 7-3.13 7-7 7c-1.93 0-3.68-.79-4.94-2.06l-1.42 1.42C8.27 19.99 10.51 21 13 21c4.97 0 9-4.03 9-9s-4.03-9-9-9zm-1 5v5l4.28 2.54.72-1.21-3.5-2.08V8H12z"/>
          </svg>
          <span class="text-xs text-slate-600 dark:text-slate-400">Avg Response</span>
        </div>
        <p class="text-2xl font-bold text-slate-900 dark:text-white">{{ liveMetrics.avgResponse }}ms</p>
        <p class="text-xs" :class="liveMetrics.responseStatus === 'good' ? 'text-emerald-600 dark:text-emerald-400' : 'text-amber-600 dark:text-amber-400'">
          {{ liveMetrics.responseStatus === 'good' ? 'Excellent' : 'Normal' }}
        </p>
      </div>
    </div>

    <!-- Live Activity Stream -->
    <div class="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-5">
      <div class="flex items-center gap-2 mb-4">
        <svg class="w-5 h-5 text-blue-500" fill="currentColor" viewBox="0 0 24 24">
          <path d="M3.9 12c0-1.71 1.39-3.1 3.1-3.1h4V7H7c-2.76 0-5 2.24-5 5s2.24 5 5 5h4v-1.9H7c-1.71 0-3.1-1.39-3.1-3.1zM8 13h8v-2H8v2zm9-6h-4v1.9h4c1.71 0 3.1 1.39 3.1 3.1s-1.39 3.1-3.1 3.1h-4V17h4c2.76 0 5-2.24 5-5s-2.24-5-5-5z"/>
        </svg>
        <h3 class="text-sm font-medium text-slate-900 dark:text-white">Live Activity Stream</h3>
      </div>
      <div class="space-y-2 max-h-96 overflow-y-auto">
        <div 
          v-for="(activity, idx) in liveActivities" 
          :key="idx"
          class="flex items-start gap-3 p-3 bg-slate-50 dark:bg-slate-700/50 rounded-lg animate-slide-in"
        >
          <div class="w-2 h-2 rounded-full mt-1.5" :class="getActivityColor(activity.type)"></div>
          <div class="flex-1 min-w-0">
            <p class="text-sm text-slate-900 dark:text-white">{{ activity.message }}</p>
            <p class="text-xs text-slate-500 dark:text-slate-400 mt-0.5">{{ activity.time }}</p>
          </div>
          <span class="text-xs px-2 py-1 rounded-full" :class="getActivityBadge(activity.type)">
            {{ activity.type }}
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'RealTimeMonitor',
  data() {
    return {
      autoRefresh: true,
      refreshInterval: null,
      liveMetrics: {
        activeSessions: 0,
        sessionChange: 0,
        revenueToday: 0,
        transactionsToday: 0,
        onlineUsers: 0,
        peakToday: 0,
        avgResponse: 0,
        responseStatus: 'good'
      },
      liveActivities: []
    }
  },
  mounted() {
    this.fetchLiveData()
    this.startAutoRefresh()
  },
  beforeUnmount() {
    this.stopAutoRefresh()
  },
  methods: {
    async fetchLiveData() {
      // Simulate live data - replace with actual API calls
      this.liveMetrics = {
        activeSessions: Math.floor(Math.random() * 500) + 100,
        sessionChange: Math.floor(Math.random() * 20),
        revenueToday: Math.floor(Math.random() * 50000) + 10000,
        transactionsToday: Math.floor(Math.random() * 200) + 50,
        onlineUsers: Math.floor(Math.random() * 300) + 50,
        peakToday: Math.floor(Math.random() * 400) + 100,
        avgResponse: Math.floor(Math.random() * 100) + 50,
        responseStatus: Math.random() > 0.3 ? 'good' : 'normal'
      }

      // Add new activity
      const activities = [
        { type: 'payment', message: 'New payment of KSh 500 received', time: 'Just now' },
        { type: 'signup', message: 'New user registered', time: 'Just now' },
        { type: 'voucher', message: 'Voucher activated', time: 'Just now' },
        { type: 'session', message: 'User logged in', time: 'Just now' }
      ]
      
      const newActivity = activities[Math.floor(Math.random() * activities.length)]
      this.liveActivities.unshift(newActivity)
      
      if (this.liveActivities.length > 20) {
        this.liveActivities.pop()
      }
    },

    startAutoRefresh() {
      if (this.autoRefresh) {
        this.refreshInterval = setInterval(() => {
          this.fetchLiveData()
        }, 5000)
      }
    },

    stopAutoRefresh() {
      if (this.refreshInterval) {
        clearInterval(this.refreshInterval)
        this.refreshInterval = null
      }
    },

    toggleAutoRefresh() {
      this.autoRefresh = !this.autoRefresh
      if (this.autoRefresh) {
        this.startAutoRefresh()
      } else {
        this.stopAutoRefresh()
      }
    },

    getActivityColor(type) {
      const colors = {
        payment: 'bg-emerald-500',
        signup: 'bg-blue-500',
        voucher: 'bg-purple-500',
        session: 'bg-amber-500'
      }
      return colors[type] || 'bg-slate-500'
    },

    getActivityBadge(type) {
      const badges = {
        payment: 'bg-emerald-100 dark:bg-emerald-500/20 text-emerald-700 dark:text-emerald-400',
        signup: 'bg-blue-100 dark:bg-blue-500/20 text-blue-700 dark:text-blue-400',
        voucher: 'bg-purple-100 dark:bg-purple-500/20 text-purple-700 dark:text-purple-400',
        session: 'bg-amber-100 dark:bg-amber-500/20 text-amber-700 dark:text-amber-400'
      }
      return badges[type] || 'bg-slate-100 dark:bg-slate-700 text-slate-700 dark:text-slate-400'
    },

    formatNumber(num) {
      return new Intl.NumberFormat().format(num)
    }
  }
}
</script>

<style scoped>
@keyframes slide-in {
  from {
    opacity: 0;
    transform: translateX(-20px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

.animate-slide-in {
  animation: slide-in 0.3s ease-out;
}
</style>
