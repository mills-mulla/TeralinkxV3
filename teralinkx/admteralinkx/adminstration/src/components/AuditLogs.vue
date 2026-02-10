<template>
  <div class="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-5">
    <div class="flex items-center justify-between mb-4">
      <div class="flex items-center gap-2">
        <svg class="w-5 h-5 text-indigo-500" fill="currentColor" viewBox="0 0 24 24">
          <path d="M19 3h-4.18C14.4 1.84 13.3 1 12 1c-1.3 0-2.4.84-2.82 2H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-7 0c.55 0 1 .45 1 1s-.45 1-1 1-1-.45-1-1 .45-1 1-1zm2 14H7v-2h7v2zm3-4H7v-2h10v2zm0-4H7V7h10v2z"/>
        </svg>
        <h3 class="text-sm font-medium text-slate-900 dark:text-white">Audit Logs</h3>
      </div>
      <input
        type="text"
        placeholder="Search logs..."
        class="px-3 py-1.5 text-xs bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white"
      />
    </div>

    <div v-if="loading" class="text-center py-8 text-slate-400">Loading...</div>

    <div v-else class="space-y-2">
      <div
        v-for="log in data.logs"
        :key="log.id"
        class="flex items-center justify-between p-3 bg-slate-50 dark:bg-slate-700/50 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors"
      >
        <div class="flex items-center gap-3 flex-1">
          <div class="w-8 h-8 rounded-full flex items-center justify-center" :class="getActionColor(log.action)">
            <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24" v-html="getActionIcon(log.action)"></svg>
          </div>
          <div class="flex-1 min-w-0">
            <p class="text-sm text-slate-900 dark:text-white">
              <span class="font-medium">{{ log.user }}</span>
              <span class="text-slate-600 dark:text-slate-400"> {{ log.action.toLowerCase() }}d </span>
              <span class="font-medium">{{ log.resource }}</span>
              <span class="text-slate-600 dark:text-slate-400"> #{{ log.resource_id }}</span>
            </p>
            <div class="flex items-center gap-3 mt-1">
              <p class="text-xs text-slate-500 dark:text-slate-400">{{ formatTime(log.timestamp) }}</p>
              <p class="text-xs text-slate-500 dark:text-slate-400">{{ log.ip }}</p>
            </div>
          </div>
        </div>
        <button class="p-1.5 hover:bg-slate-200 dark:hover:bg-slate-600 rounded transition-colors">
          <svg class="w-4 h-4 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
          </svg>
        </button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'AuditLogs',
  props: {
    data: {
      type: Object,
      default: () => ({ logs: [] })
    },
    loading: {
      type: Boolean,
      default: false
    }
  },
  methods: {
    getActionColor(action) {
      const colors = {
        'CREATE': 'bg-emerald-100 dark:bg-emerald-500/20 text-emerald-600 dark:text-emerald-400',
        'UPDATE': 'bg-blue-100 dark:bg-blue-500/20 text-blue-600 dark:text-blue-400',
        'DELETE': 'bg-red-100 dark:bg-red-500/20 text-red-600 dark:text-red-400',
        'VIEW': 'bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-400'
      }
      return colors[action] || 'bg-slate-100 dark:bg-slate-700'
    },
    getActionIcon(action) {
      const icons = {
        'CREATE': '<path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm5 11h-4v4h-2v-4H7v-2h4V7h2v4h4v2z"/>',
        'UPDATE': '<path d="M3 17.25V21h3.75L17.81 9.94l-3.75-3.75L3 17.25zM20.71 7.04c.39-.39.39-1.02 0-1.41l-2.34-2.34c-.39-.39-1.02-.39-1.41 0l-1.83 1.83 3.75 3.75 1.83-1.83z"/>',
        'DELETE': '<path d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z"/>',
        'VIEW': '<path d="M12 4.5C7 4.5 2.73 7.61 1 12c1.73 4.39 6 7.5 11 7.5s9.27-3.11 11-7.5c-1.73-4.39-6-7.5-11-7.5zM12 17c-2.76 0-5-2.24-5-5s2.24-5 5-5 5 2.24 5 5-2.24 5-5 5zm0-8c-1.66 0-3 1.34-3 3s1.34 3 3 3 3-1.34 3-3-1.34-3-3-3z"/>'
      }
      return icons[action] || icons['VIEW']
    },
    formatTime(timestamp) {
      const date = new Date(timestamp)
      const now = new Date()
      const diff = Math.floor((now - date) / 1000)
      
      if (diff < 60) return 'Just now'
      if (diff < 3600) return `${Math.floor(diff / 60)}m ago`
      if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`
      return date.toLocaleDateString()
    }
  }
}
</script>
