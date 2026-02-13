<template>
  <div class="space-y-4">
    <!-- Header with Stats -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
      <div class="bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl p-4 text-white">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-blue-100 text-xs font-medium">Total Logs (24h)</p>
            <p class="text-2xl font-bold mt-1">{{ data.summary?.total_24h || 0 }}</p>
          </div>
          <svg class="w-10 h-10 text-blue-200" fill="currentColor" viewBox="0 0 24 24">
            <path d="M19 3h-4.18C14.4 1.84 13.3 1 12 1c-1.3 0-2.4.84-2.82 2H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-7 0c.55 0 1 .45 1 1s-.45 1-1 1-1-.45-1-1 .45-1 1-1zm2 14H7v-2h7v2zm3-4H7v-2h10v2zm0-4H7V7h10v2z"/>
          </svg>
        </div>
      </div>

      <div class="bg-gradient-to-br from-red-500 to-red-600 rounded-xl p-4 text-white">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-red-100 text-xs font-medium">Critical Events</p>
            <p class="text-2xl font-bold mt-1">{{ data.summary?.critical_24h || 0 }}</p>
          </div>
          <svg class="w-10 h-10 text-red-200" fill="currentColor" viewBox="0 0 24 24">
            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z"/>
          </svg>
        </div>
      </div>

      <div class="bg-gradient-to-br from-amber-500 to-amber-600 rounded-xl p-4 text-white">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-amber-100 text-xs font-medium">Suspicious Activity</p>
            <p class="text-2xl font-bold mt-1">{{ data.summary?.suspicious_24h || 0 }}</p>
          </div>
          <svg class="w-10 h-10 text-amber-200" fill="currentColor" viewBox="0 0 24 24">
            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-6h2v6zm0-8h-2V7h2v2z"/>
          </svg>
        </div>
      </div>

      <div class="bg-gradient-to-br from-emerald-500 to-emerald-600 rounded-xl p-4 text-white">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-emerald-100 text-xs font-medium">Active Users</p>
            <p class="text-2xl font-bold mt-1">{{ activeUsers }}</p>
          </div>
          <svg class="w-10 h-10 text-emerald-200" fill="currentColor" viewBox="0 0 24 24">
            <path d="M16 11c1.66 0 2.99-1.34 2.99-3S17.66 5 16 5c-1.66 0-3 1.34-3 3s1.34 3 3 3zm-8 0c1.66 0 2.99-1.34 2.99-3S9.66 5 8 5C6.34 5 5 6.34 5 8s1.34 3 3 3zm0 2c-2.33 0-7 1.17-7 3.5V19h14v-2.5c0-2.33-4.67-3.5-7-3.5zm8 0c-.29 0-.62.02-.97.05 1.16.84 1.97 1.97 1.97 3.45V19h6v-2.5c0-2.33-4.67-3.5-7-3.5z"/>
          </svg>
        </div>
      </div>
    </div>

    <!-- Search and Filters -->
    <div class="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-4">
      <div class="flex flex-col md:flex-row gap-3">
        <div class="flex-1">
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Search by user, action, resource, IP address..."
            class="w-full px-4 py-2 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white text-sm"
          />
        </div>
        <select v-model="filterAction" class="px-4 py-2 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white text-sm">
          <option value="">All Actions</option>
          <option value="CREATE">Create</option>
          <option value="UPDATE">Update</option>
          <option value="DELETE">Delete</option>
          <option value="LOGIN">Login</option>
          <option value="LOGOUT">Logout</option>
          <option value="VIEW">View</option>
        </select>
        <select v-model="filterSeverity" class="px-4 py-2 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white text-sm">
          <option value="">All Severity</option>
          <option value="info">Info</option>
          <option value="warning">Warning</option>
          <option value="critical">Critical</option>
        </select>
        <button @click="clearFilters" class="px-4 py-2 bg-slate-200 dark:bg-slate-700 hover:bg-slate-300 dark:hover:bg-slate-600 text-slate-900 dark:text-white rounded-lg text-sm transition-colors">
          Clear
        </button>
      </div>
    </div>

    <!-- Logs Table -->
    <div class="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 overflow-hidden">
      <div v-if="loading" class="text-center py-12 text-slate-400">
        <svg class="animate-spin h-8 w-8 mx-auto mb-2" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        Loading audit logs...
      </div>

      <div v-else-if="filteredLogs.length === 0" class="text-center py-12 text-slate-400">
        <svg class="w-12 h-12 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        No logs found
      </div>

      <div v-else class="overflow-x-auto">
        <table class="w-full">
          <thead class="bg-slate-50 dark:bg-slate-900 border-b border-slate-200 dark:border-slate-700">
            <tr>
              <th class="px-4 py-3 text-left text-xs font-medium text-slate-500 dark:text-slate-400 uppercase">Time</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-slate-500 dark:text-slate-400 uppercase">User</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-slate-500 dark:text-slate-400 uppercase">Action</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-slate-500 dark:text-slate-400 uppercase">Resource</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-slate-500 dark:text-slate-400 uppercase">IP Address</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-slate-500 dark:text-slate-400 uppercase">Severity</th>
              <th class="px-4 py-3 text-right text-xs font-medium text-slate-500 dark:text-slate-400 uppercase">Actions</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-200 dark:divide-slate-700">
            <tr
              v-for="log in paginatedLogs"
              :key="log.id"
              class="hover:bg-slate-50 dark:hover:bg-slate-700/50 transition-colors"
              :class="{ 'bg-red-50 dark:bg-red-900/10': log.is_suspicious }"
            >
              <td class="px-4 py-3 whitespace-nowrap">
                <div class="text-xs text-slate-900 dark:text-white font-medium">{{ formatTime(log.timestamp) }}</div>
                <div class="text-xs text-slate-500 dark:text-slate-400">{{ formatDate(log.timestamp) }}</div>
              </td>
              <td class="px-4 py-3 whitespace-nowrap">
                <div class="flex items-center gap-2">
                  <div class="w-8 h-8 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white text-xs font-bold">
                    {{ log.user.charAt(0).toUpperCase() }}
                  </div>
                  <span class="text-sm font-medium text-slate-900 dark:text-white">{{ log.user }}</span>
                </div>
              </td>
              <td class="px-4 py-3 whitespace-nowrap">
                <div class="flex items-center gap-2">
                  <div class="w-8 h-8 rounded-lg flex items-center justify-center" :class="getActionColor(log.action)">
                    <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24" v-html="getActionIcon(log.action)"></svg>
                  </div>
                  <span class="text-sm text-slate-900 dark:text-white">{{ log.action }}</span>
                </div>
              </td>
              <td class="px-4 py-3">
                <div class="text-sm text-slate-900 dark:text-white">{{ log.category }}</div>
                <div class="text-xs text-slate-500 dark:text-slate-400">{{ log.description }}</div>
              </td>
              <td class="px-4 py-3 whitespace-nowrap">
                <span class="text-xs font-mono text-slate-600 dark:text-slate-400">{{ log.ip_address }}</span>
              </td>
              <td class="px-4 py-3 whitespace-nowrap">
                <span class="px-2 py-1 text-xs font-medium rounded-full" :class="getSeverityBadge(log.severity)">
                  {{ log.severity }}
                </span>
                <span v-if="log.is_suspicious" class="ml-1 px-2 py-1 text-xs font-medium rounded-full bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400">
                  ⚠️ Suspicious
                </span>
              </td>
              <td class="px-4 py-3 whitespace-nowrap text-right">
                <button @click="showDetails(log)" class="px-3 py-1 bg-blue-500 hover:bg-blue-600 text-white text-xs rounded-lg transition-colors">
                  Details
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Pagination -->
      <div v-if="filteredLogs.length > 0" class="px-4 py-3 border-t border-slate-200 dark:border-slate-700 flex items-center justify-between">
        <div class="text-sm text-slate-600 dark:text-slate-400">
          Showing {{ (currentPage - 1) * pageSize + 1 }} to {{ Math.min(currentPage * pageSize, filteredLogs.length) }} of {{ filteredLogs.length }} logs
        </div>
        <div class="flex gap-2">
          <button
            @click="currentPage--"
            :disabled="currentPage === 1"
            class="px-3 py-1 bg-slate-200 dark:bg-slate-700 hover:bg-slate-300 dark:hover:bg-slate-600 text-slate-900 dark:text-white rounded-lg text-sm transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Previous
          </button>
          <button
            @click="currentPage++"
            :disabled="currentPage >= totalPages"
            class="px-3 py-1 bg-slate-200 dark:bg-slate-700 hover:bg-slate-300 dark:hover:bg-slate-600 text-slate-900 dark:text-white rounded-lg text-sm transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Next
          </button>
        </div>
      </div>
    </div>

    <!-- Details Modal -->
    <div v-if="selectedLog" class="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4" @click.self="selectedLog = null">
      <div class="bg-white dark:bg-slate-800 rounded-xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-hidden">
        <div class="flex items-center justify-between p-6 border-b border-slate-200 dark:border-slate-700">
          <h2 class="text-lg font-semibold text-slate-900 dark:text-white">Audit Log Details</h2>
          <button @click="selectedLog = null" class="p-2 hover:bg-slate-100 dark:hover:bg-slate-700 rounded-lg transition-colors">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        <div class="p-6 overflow-y-auto max-h-[calc(90vh-140px)] space-y-4">
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-xs font-medium text-slate-500 dark:text-slate-400 mb-1">Timestamp</label>
              <p class="text-sm text-slate-900 dark:text-white">{{ formatFullDate(selectedLog.timestamp) }}</p>
            </div>
            <div>
              <label class="block text-xs font-medium text-slate-500 dark:text-slate-400 mb-1">User</label>
              <p class="text-sm text-slate-900 dark:text-white">{{ selectedLog.user }}</p>
            </div>
            <div>
              <label class="block text-xs font-medium text-slate-500 dark:text-slate-400 mb-1">Action</label>
              <p class="text-sm text-slate-900 dark:text-white">{{ selectedLog.action }}</p>
            </div>
            <div>
              <label class="block text-xs font-medium text-slate-500 dark:text-slate-400 mb-1">Category</label>
              <p class="text-sm text-slate-900 dark:text-white">{{ selectedLog.category }}</p>
            </div>
            <div>
              <label class="block text-xs font-medium text-slate-500 dark:text-slate-400 mb-1">IP Address</label>
              <p class="text-sm font-mono text-slate-900 dark:text-white">{{ selectedLog.ip_address }}</p>
            </div>
            <div>
              <label class="block text-xs font-medium text-slate-500 dark:text-slate-400 mb-1">Severity</label>
              <span class="px-2 py-1 text-xs font-medium rounded-full" :class="getSeverityBadge(selectedLog.severity)">
                {{ selectedLog.severity }}
              </span>
            </div>
          </div>
          <div>
            <label class="block text-xs font-medium text-slate-500 dark:text-slate-400 mb-1">Description</label>
            <p class="text-sm text-slate-900 dark:text-white">{{ selectedLog.description }}</p>
          </div>
          <div v-if="selectedLog.is_suspicious" class="p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-500/30 rounded-lg">
            <div class="flex items-center gap-2 mb-2">
              <svg class="w-5 h-5 text-red-600 dark:text-red-400" fill="currentColor" viewBox="0 0 24 24">
                <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z"/>
              </svg>
              <span class="text-sm font-semibold text-red-900 dark:text-red-400">Suspicious Activity Detected</span>
            </div>
            <p class="text-xs text-red-700 dark:text-red-300">This activity has been flagged as potentially suspicious and requires review.</p>
          </div>
        </div>
        <div class="flex items-center justify-end gap-3 p-6 border-t border-slate-200 dark:border-slate-700">
          <button @click="selectedLog = null" class="px-4 py-2 bg-slate-200 dark:bg-slate-700 hover:bg-slate-300 dark:hover:bg-slate-600 text-slate-900 dark:text-white rounded-lg">Close</button>
        </div>
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
      default: () => ({ logs: [], summary: {} })
    },
    loading: {
      type: Boolean,
      default: false
    }
  },
  data() {
    return {
      searchQuery: '',
      filterAction: '',
      filterSeverity: '',
      selectedLog: null,
      currentPage: 1,
      pageSize: 20
    }
  },
  computed: {
    filteredLogs() {
      let logs = this.data.logs || []
      
      // Search filter
      if (this.searchQuery) {
        const query = this.searchQuery.toLowerCase()
        logs = logs.filter(log =>
          log.user.toLowerCase().includes(query) ||
          log.action.toLowerCase().includes(query) ||
          log.category.toLowerCase().includes(query) ||
          log.description.toLowerCase().includes(query) ||
          log.ip_address.includes(query)
        )
      }
      
      // Action filter
      if (this.filterAction) {
        logs = logs.filter(log => log.action === this.filterAction)
      }
      
      // Severity filter
      if (this.filterSeverity) {
        logs = logs.filter(log => log.severity === this.filterSeverity)
      }
      
      return logs
    },
    paginatedLogs() {
      const start = (this.currentPage - 1) * this.pageSize
      const end = start + this.pageSize
      return this.filteredLogs.slice(start, end)
    },
    totalPages() {
      return Math.ceil(this.filteredLogs.length / this.pageSize)
    },
    activeUsers() {
      const users = new Set((this.data.logs || []).map(log => log.user))
      return users.size
    }
  },
  watch: {
    searchQuery() {
      this.currentPage = 1
    },
    filterAction() {
      this.currentPage = 1
    },
    filterSeverity() {
      this.currentPage = 1
    }
  },
  methods: {
    clearFilters() {
      this.searchQuery = ''
      this.filterAction = ''
      this.filterSeverity = ''
      this.currentPage = 1
    },
    showDetails(log) {
      this.selectedLog = log
    },
    getActionColor(action) {
      const colors = {
        'CREATE': 'bg-emerald-100 dark:bg-emerald-500/20 text-emerald-600 dark:text-emerald-400',
        'UPDATE': 'bg-blue-100 dark:bg-blue-500/20 text-blue-600 dark:text-blue-400',
        'DELETE': 'bg-red-100 dark:bg-red-500/20 text-red-600 dark:text-red-400',
        'LOGIN': 'bg-purple-100 dark:bg-purple-500/20 text-purple-600 dark:text-purple-400',
        'LOGOUT': 'bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-400',
        'VIEW': 'bg-cyan-100 dark:bg-cyan-500/20 text-cyan-600 dark:text-cyan-400'
      }
      return colors[action] || 'bg-slate-100 dark:bg-slate-700'
    },
    getActionIcon(action) {
      const icons = {
        'CREATE': '<path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm5 11h-4v4h-2v-4H7v-2h4V7h2v4h4v2z"/>',
        'UPDATE': '<path d="M3 17.25V21h3.75L17.81 9.94l-3.75-3.75L3 17.25zM20.71 7.04c.39-.39.39-1.02 0-1.41l-2.34-2.34c-.39-.39-1.02-.39-1.41 0l-1.83 1.83 3.75 3.75 1.83-1.83z"/>',
        'DELETE': '<path d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z"/>',
        'LOGIN': '<path d="M11 7L9.6 8.4l2.6 2.6H2v2h10.2l-2.6 2.6L11 17l5-5-5-5zm9 12h-8v2h8c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2h-8v2h8v14z"/>',
        'LOGOUT': '<path d="M17 7l-1.41 1.41L18.17 11H8v2h10.17l-2.58 2.58L17 17l5-5-5-5zM4 5h8V3H4c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h8v-2H4V5z"/>',
        'VIEW': '<path d="M12 4.5C7 4.5 2.73 7.61 1 12c1.73 4.39 6 7.5 11 7.5s9.27-3.11 11-7.5c-1.73-4.39-6-7.5-11-7.5zM12 17c-2.76 0-5-2.24-5-5s2.24-5 5-5 5 2.24 5 5-2.24 5-5 5zm0-8c-1.66 0-3 1.34-3 3s1.34 3 3 3 3-1.34 3-3-1.34-3-3-3z"/>'
      }
      return icons[action] || icons['VIEW']
    },
    getSeverityBadge(severity) {
      const badges = {
        'info': 'bg-blue-100 dark:bg-blue-500/20 text-blue-700 dark:text-blue-400',
        'warning': 'bg-amber-100 dark:bg-amber-500/20 text-amber-700 dark:text-amber-400',
        'critical': 'bg-red-100 dark:bg-red-500/20 text-red-700 dark:text-red-400'
      }
      return badges[severity] || badges['info']
    },
    formatTime(timestamp) {
      const date = new Date(timestamp)
      const now = new Date()
      const diff = Math.floor((now - date) / 1000)
      
      if (diff < 60) return 'Just now'
      if (diff < 3600) return `${Math.floor(diff / 60)}m ago`
      if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`
      return `${Math.floor(diff / 86400)}d ago`
    },
    formatDate(timestamp) {
      return new Date(timestamp).toLocaleDateString('en-US', { 
        month: 'short', 
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })
    },
    formatFullDate(timestamp) {
      return new Date(timestamp).toLocaleString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
      })
    }
  }
}
</script>
