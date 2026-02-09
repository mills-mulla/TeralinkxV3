<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50/30 p-6">
    <div class="mb-8">
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-3xl font-bold bg-gradient-to-r from-slate-800 to-blue-600 bg-clip-text text-transparent mb-2">🔌 Session Management</h1>
          <p class="text-slate-600 font-light">Monitor active user sessions</p>
        </div>
        <button @click="refreshData" class="p-2 hover:bg-white/50 rounded-xl transition-all duration-300"><ArrowPathIcon class="w-6 h-6 text-slate-600" /></button>
      </div>
    </div>

    <div v-if="error" class="bg-rose-50 border border-rose-200 rounded-2xl p-6 mb-6">
      <div class="flex items-center justify-between">
        <div class="flex items-center space-x-3"><ExclamationTriangleIcon class="w-6 h-6 text-rose-600" /><div><h3 class="text-rose-800 font-semibold">Failed to load session data</h3><p class="text-rose-600 text-sm">{{ error }}</p></div></div>
        <button @click="fetchSessions" class="px-4 py-2 bg-rose-600 text-white rounded-lg hover:bg-rose-700">Retry</button>
      </div>
    </div>

    <div v-if="loading && !error" class="flex items-center justify-center py-20">
      <div class="text-center"><div class="relative"><div class="w-16 h-16 border-4 border-blue-200 rounded-full"></div><div class="w-16 h-16 border-4 border-transparent border-t-blue-500 rounded-full animate-spin absolute top-0 left-0"></div></div><p class="mt-4 text-slate-500 font-light">Loading sessions...</p></div>
    </div>

    <div v-else-if="!loading" class="space-y-8">
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <ModernMetricCard title="Total Sessions" :value="stats.total_sessions" icon="🔌" color="blue" :formatted="true" />
        <ModernMetricCard title="Active Sessions" :value="stats.active_sessions" icon="✅" color="emerald" :formatted="true" />
        <ModernMetricCard title="With Vouchers" :value="stats.voucher_sessions" icon="🎫" color="purple" :formatted="true" />
        <ModernMetricCard title="Inactive" :value="stats.inactive_sessions" icon="⏸️" color="slate" :formatted="true" />
      </div>

      <SearchBar v-model="searchTerm" placeholder="Search sessions..." :filters="filters" @filter-change="handleFilterChange" @clear="clearFilters" :show-add-button="false" />

      <DataTable title="Session Records" :data="filteredSessions" :columns="columns" :actions="['delete']" @delete="openDeleteModal">
        <template #cell-is_active="{ value }"><span :class="value ? 'bg-emerald-100 text-emerald-800' : 'bg-slate-100 text-slate-800'" class="px-2 py-1 text-xs font-medium rounded-full">{{ value ? 'Active' : 'Inactive' }}</span></template>
        <template #custom-actions="{ item }"><button v-if="item.is_active" @click="terminateSession(item)" class="text-rose-600 hover:text-rose-800 p-1 rounded" title="Terminate">⏹️</button></template>
      </DataTable>
    </div>

    <ConfirmDialog :show="showDeleteModal" title="Delete Session" :message="`Delete session <strong>${sessionToDelete?.session_id}</strong>?`" type="danger" :loading="deleteLoading" @confirm="confirmDelete" @cancel="closeDeleteModal" />
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

    const filters = [{ key: 'is_active', label: 'Status', options: [{ value: 'true', label: 'Active' }, { value: 'false', label: 'Inactive' }] }]

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

    const fetchSessions = async () => { try { const data = await makeRequest('get', 'sessions/'); sessions.value = data.results || data } catch (err) { console.error('Error:', err) } }
    const fetchStats = async () => { try { stats.value = await makeRequest('get', 'sessions/stats/') } catch (err) { console.error('Error:', err) } }
    const refreshData = () => Promise.all([fetchSessions(), fetchStats()])
    const handleFilterChange = ({ all }) => { activeFilters.value = all }
    const clearFilters = () => { searchTerm.value = ''; activeFilters.value = {} }

    const terminateSession = async (session) => {
      try {
        await makeRequest('post', `sessions/${session.id}/terminate/`, { reason: 'Admin action' })
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
        await makeRequest('delete', `sessions/${sessionToDelete.value.id}/`)
        await refreshData()
        closeDeleteModal()
      } catch (err) {
        alert('Error: ' + (err.response?.data?.error || err.message))
      } finally {
        deleteLoading.value = false
      }
    }

    onMounted(refreshData)

    return { loading, error, sessions, stats, searchTerm, showDeleteModal, sessionToDelete, deleteLoading, columns, filters, filteredSessions, fetchSessions, refreshData, handleFilterChange, clearFilters, terminateSession, openDeleteModal, closeDeleteModal, confirmDelete }
  }
}
</script>
