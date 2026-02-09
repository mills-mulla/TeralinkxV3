<template>
  <div class="space-y-6 animate-fade-in">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-semibold text-slate-900 dark:text-white">Sessions</h1>
        <p class="text-sm text-slate-500 dark:text-slate-400 mt-1">Monitor active user sessions</p>
      </div>
      <button @click="refreshData" class="p-2 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-lg transition-colors" :class="{ 'animate-spin': loading }">
        <ArrowPathIcon class="w-5 h-5 text-slate-600 dark:text-slate-400" />
      </button>
    </div>

    <!-- Error State -->
    <div v-if="error" class="bg-rose-50 dark:bg-rose-500/10 border border-rose-200 dark:border-rose-500/20 rounded-lg p-4">
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-3">
          <ExclamationTriangleIcon class="w-5 h-5 text-rose-600 dark:text-rose-400" />
          <div>
            <h3 class="text-sm font-medium text-rose-800 dark:text-rose-400">Failed to load sessions</h3>
            <p class="text-xs text-rose-600 dark:text-rose-500 mt-1">{{ error }}</p>
          </div>
        </div>
        <button @click="fetchSessions" class="px-3 py-1.5 bg-rose-600 text-white rounded-lg hover:bg-rose-700 text-sm">Retry</button>
      </div>
    </div>

    <!-- Metrics -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 animate-slide-up">
      <ModernMetricCard title="Total Sessions" :value="stats.total_sessions" icon="🔌" color="blue" />
      <ModernMetricCard title="Active" :value="stats.active_sessions" icon="✅" color="emerald" />
      <ModernMetricCard title="With Vouchers" :value="stats.voucher_sessions" icon="🎫" color="purple" />
      <ModernMetricCard title="Inactive" :value="stats.inactive_sessions" icon="⏸️" color="slate" />
    </div>

    <!-- Search & Table -->
    <div class="space-y-4 animate-slide-up" style="animation-delay: 0.1s">
      <SearchBar
        v-model="searchTerm"
        placeholder="Search sessions..."
        :filters="filters"
        @filter-change="handleFilterChange"
        @clear="clearFilters"
        :show-add-button="false"
      />

      <DataTable
        title="Session Records"
        :data="filteredSessions"
        :columns="columns"
        :actions="['delete']"
        @delete="openDeleteModal"
      >
        <template #cell-is_active="{ value }">
          <span :class="value ? 'bg-emerald-100 dark:bg-emerald-500/20 text-emerald-700 dark:text-emerald-400' : 'bg-slate-100 dark:bg-slate-700 text-slate-700 dark:text-slate-400'" class="px-2 py-0.5 text-xs font-medium rounded-full">
            {{ value ? 'Active' : 'Inactive' }}
          </span>
        </template>
        <template #custom-actions="{ item }">
          <button v-if="item.is_active" @click="terminateSession(item)" class="text-rose-600 dark:text-rose-400 hover:text-rose-800 dark:hover:text-rose-300 p-1 rounded" title="Terminate">⏹️</button>
        </template>
      </DataTable>
    </div>

    <!-- Delete Modal -->
    <ConfirmDialog
      :show="showDeleteModal"
      title="Delete Session"
      :message="`Delete session <strong>${sessionToDelete?.session_id}</strong>?`"
      type="danger"
      :loading="deleteLoading"
      @confirm="confirmDelete"
      @cancel="closeDeleteModal"
    />
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useApi } from '../composables/useApi'
import ModernMetricCard from '../components/MetricCard.vue'
import SearchBar from '../components/SearchBar.vue'
import DataTable from '../components/DataTable.vue'
import ConfirmDialog from '../components/ConfirmDialog.vue'
import { ArrowPathIcon, ExclamationTriangleIcon } from '@heroicons/vue/24/outline'

export default {
  name: 'Sessions',
  components: { ModernMetricCard, SearchBar, DataTable, ConfirmDialog, ArrowPathIcon, ExclamationTriangleIcon },
  setup() {
    const { loading, error, makeRequest } = useApi()
    const sessions = ref([])
    const stats = ref({})
    const searchTerm = ref('')
    const activeFilters = ref({})
    const showDeleteModal = ref(false)
    const sessionToDelete = ref(null)
    const deleteLoading = ref(false)

    const columns = [
      { key: 'id', label: 'ID', sortable: true },
      { key: 'session_id', label: 'Session ID', sortable: true, format: (v) => v?.substring(0, 12) + '...' },
      { key: 'user_account', label: 'User', sortable: true },
      { key: 'device_name', label: 'Device', sortable: true },
      { key: 'ip_address', label: 'IP Address', sortable: true },
      { key: 'is_active', label: 'Status', sortable: true },
      { key: 'duration', label: 'Duration', sortable: true }
    ]

    const filters = [
      { key: 'is_active', label: 'Status', options: [{ value: 'true', label: 'Active' }, { value: 'false', label: 'Inactive' }] }
    ]

    const filteredSessions = computed(() => {
      let result = sessions.value
      if (searchTerm.value) {
        const term = searchTerm.value.toLowerCase()
        result = result.filter(s => s.session_id?.toLowerCase().includes(term) || s.user_account?.toLowerCase().includes(term) || s.ip_address?.includes(term))
      }
      Object.keys(activeFilters.value).forEach(key => {
        const value = activeFilters.value[key]
        if (value) result = result.filter(s => s[key] === (value === 'true'))
      })
      return result
    })

    const fetchSessions = async () => {
      try {
        const data = await makeRequest('get', 'suapi/sessions/')
        sessions.value = data.results || data
      } catch (err) {
        console.error('Error:', err)
      }
    }

    const fetchStats = async () => {
      try {
        stats.value = await makeRequest('get', 'suapi/sessions/stats/')
      } catch (err) {
        console.error('Error:', err)
      }
    }

    const refreshData = () => Promise.all([fetchSessions(), fetchStats()])
    const handleFilterChange = ({ all }) => { activeFilters.value = all }
    const clearFilters = () => { searchTerm.value = ''; activeFilters.value = {} }

    const terminateSession = async (session) => {
      try {
        await makeRequest('post', `suapi/sessions/${session.id}/terminate/`, { reason: 'Admin action' })
        await refreshData()
      } catch (err) {
        alert('Error: ' + (err.response?.data?.error || err.message))
      }
    }

    const openDeleteModal = (session) => { sessionToDelete.value = session; showDeleteModal.value = true }
    const closeDeleteModal = () => { showDeleteModal.value = false; sessionToDelete.value = null }

    const confirmDelete = async () => {
      deleteLoading.value = true
      try {
        await makeRequest('delete', `suapi/sessions/${sessionToDelete.value.id}/`)
        await refreshData()
        closeDeleteModal()
      } catch (err) {
        alert('Error: ' + (err.response?.data?.error || err.message))
      } finally {
        deleteLoading.value = false
      }
    }

    onMounted(refreshData)

    return {
      loading, error, sessions, stats, searchTerm, showDeleteModal, sessionToDelete, deleteLoading,
      columns, filters, filteredSessions, fetchSessions, refreshData, handleFilterChange, clearFilters,
      terminateSession, openDeleteModal, closeDeleteModal, confirmDelete
    }
  }
}
</script>

<style scoped>
@keyframes fade-in {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes slide-up {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

.animate-fade-in {
  animation: fade-in 0.3s ease-out;
}

.animate-slide-up {
  animation: slide-up 0.4s ease-out;
}
</style>
