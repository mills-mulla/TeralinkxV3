<template>
  <div class="space-y-4 animate-fade-in">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-lg font-semibold text-slate-900 dark:text-white">Sessions</h1>
        <p class="text-xs text-slate-500 dark:text-slate-400 mt-0.5">Monitor active user sessions</p>
      </div>
      <div class="flex items-center gap-2">
        <button @click="openAddModal" class="px-3 py-1.5 bg-blue-500 hover:bg-blue-600 text-white rounded-lg text-xs flex items-center gap-1.5">
          <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
          </svg>
          Add Session
        </button>
        <button @click="refreshData" class="p-1.5 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-lg transition-colors" :class="{ 'animate-spin': loading }">
          <svg class="w-4 h-4 text-slate-600 dark:text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
        </button>
      </div>
    </div>

    <!-- Error State -->
    <div v-if="error" class="bg-rose-50 dark:bg-rose-500/10 border border-rose-200 dark:border-rose-500/20 rounded-lg p-4">
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-3">
          <svg class="w-5 h-5 text-rose-600 dark:text-rose-400" fill="currentColor" viewBox="0 0 24 24">
            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z"/>
          </svg>
          <div>
            <h3 class="text-sm font-medium text-rose-800 dark:text-rose-400">Failed to load sessions</h3>
            <p class="text-xs text-rose-600 dark:text-rose-500 mt-1">{{ error }}</p>
          </div>
        </div>
        <button @click="fetchSessions" class="px-3 py-1.5 bg-rose-600 text-white rounded-lg hover:bg-rose-700 text-sm">Retry</button>
      </div>
    </div>

    <!-- Metrics -->
    <div class="grid grid-cols-2 md:grid-cols-4 gap-3 animate-slide-up">
      <ModernMetricCard title="Total" :value="stats.total_sessions" color="blue">
        <svg class="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
          <path d="M11.99 2C6.47 2 2 6.48 2 12s4.47 10 9.99 10C17.52 22 22 17.52 22 12S17.52 2 11.99 2zM12 20c-4.42 0-8-3.58-8-8s3.58-8 8-8 8 3.58 8 8-3.58 8-8 8zm.5-13H11v6l5.25 3.15.75-1.23-4.5-2.67z"/>
        </svg>
      </ModernMetricCard>
      <ModernMetricCard title="Active" :value="stats.active_sessions" color="emerald">
        <svg class="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
          <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
        </svg>
      </ModernMetricCard>
      <ModernMetricCard title="Vouchers" :value="stats.voucher_sessions" color="purple">
        <svg class="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
          <path d="M21.41 11.58l-9-9C12.05 2.22 11.55 2 11 2H4c-1.1 0-2 .9-2 2v7c0 .55.22 1.05.59 1.42l9 9c.36.36.86.58 1.41.58.55 0 1.05-.22 1.41-.59l7-7c.37-.36.59-.86.59-1.41 0-.55-.23-1.06-.59-1.42zM5.5 7C4.67 7 4 6.33 4 5.5S4.67 4 5.5 4 7 4.67 7 5.5 6.33 7 5.5 7z"/>
        </svg>
      </ModernMetricCard>
      <ModernMetricCard title="Inactive" :value="stats.inactive_sessions" color="slate">
        <svg class="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
          <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm5 11H7v-2h10v2z"/>
        </svg>
      </ModernMetricCard>
    </div>

    <!-- Search & Filters -->
    <div class="space-y-3 animate-slide-up" style="animation-delay: 0.1s">
      <div class="flex items-center gap-2">
        <div class="flex-1">
          <input v-model="searchTerm" type="text" placeholder="Search sessions..." class="w-full px-3 py-1.5 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white text-xs" />
        </div>
        <select v-model="statusFilter" class="px-3 py-1.5 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white text-xs">
          <option value="">All Status</option>
          <option value="true">Active</option>
          <option value="false">Inactive</option>
        </select>
      </div>

      <!-- Table -->
      <div class="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 overflow-hidden">
        <div class="overflow-x-auto">
          <table class="w-full">
            <thead class="bg-slate-50 dark:bg-slate-900 border-b border-slate-200 dark:border-slate-700">
              <tr>
                <th class="px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400">Session</th>
                <th class="px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400">User</th>
                <th class="px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400">Device</th>
                <th class="px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400">IP Address</th>
                <th class="px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400">Status</th>
                <th class="px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400">Duration</th>
                <th class="px-3 py-2 text-right text-[10px] font-medium text-slate-600 dark:text-slate-400">Actions</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-200 dark:divide-slate-700">
              <tr v-for="session in filteredSessions" :key="session.id" @click="openEditModal(session)" class="hover:bg-slate-50 dark:hover:bg-slate-700/50 transition-colors cursor-pointer">
                <td class="px-3 py-2">
                  <div class="flex items-center gap-2">
                    <div class="w-7 h-7 rounded-lg bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
                      <svg class="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 24 24">
                        <path d="M11.99 2C6.47 2 2 6.48 2 12s4.47 10 9.99 10C17.52 22 22 17.52 22 12S17.52 2 11.99 2zM12 20c-4.42 0-8-3.58-8-8s3.58-8 8-8 8 3.58 8 8-3.58 8-8 8z"/>
                      </svg>
                    </div>
                    <div>
                      <p class="text-xs font-medium text-slate-900 dark:text-white font-mono">{{ session.session_id?.substring(0, 8) }}</p>
                      <p class="text-[10px] text-slate-500 dark:text-slate-400">ID: {{ session.id }}</p>
                    </div>
                  </div>
                </td>
                <td class="px-3 py-2 text-xs text-slate-900 dark:text-white">{{ session.user_account || 'N/A' }}</td>
                <td class="px-3 py-2 text-xs text-slate-900 dark:text-white">{{ session.device_name || 'Unknown' }}</td>
                <td class="px-3 py-2 text-xs text-slate-900 dark:text-white font-mono">{{ session.ip_address || 'N/A' }}</td>
                <td class="px-3 py-2">
                  <span class="px-1.5 py-0.5 text-[10px] font-medium rounded-full" :class="session.is_active ? 'bg-emerald-100 dark:bg-emerald-500/20 text-emerald-700 dark:text-emerald-400' : 'bg-slate-100 dark:bg-slate-700 text-slate-700 dark:text-slate-400'">
                    {{ session.is_active ? 'Active' : 'Inactive' }}
                  </span>
                </td>
                <td class="px-3 py-2 text-xs text-slate-900 dark:text-white">{{ session.duration || 'N/A' }}</td>
                <td class="px-3 py-2 text-right">
                  <div class="flex items-center justify-end gap-0.5">
                    <button @click.stop="openEditModal(session)" class="p-1 hover:bg-blue-100 dark:hover:bg-blue-600 rounded transition-colors" title="Edit">
                      <svg class="w-3.5 h-3.5 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                      </svg>
                    </button>
                    <button v-if="session.is_active" @click.stop="terminateSession(session)" class="p-1 hover:bg-amber-100 dark:hover:bg-amber-600 rounded transition-colors" title="Terminate">
                      <svg class="w-3.5 h-3.5 text-amber-600 dark:text-amber-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 10a1 1 0 011-1h4a1 1 0 011 1v4a1 1 0 01-1 1h-4a1 1 0 01-1-1v-4z" />
                      </svg>
                    </button>
                    <button @click.stop="openDeleteModal(session)" class="p-1 hover:bg-red-100 dark:hover:bg-red-600 rounded transition-colors" title="Delete">
                      <svg class="w-3.5 h-3.5 text-red-600 dark:text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                      </svg>
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Edit Session Modal -->
    <div v-if="showFormModal" class="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4" @click.self="closeFormModal">
      <div class="bg-white dark:bg-slate-800 rounded-xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-hidden">
        <div class="flex items-center justify-between p-5 border-b border-slate-200 dark:border-slate-700">
          <h2 class="text-base font-semibold text-slate-900 dark:text-white">{{ selectedSession?.id ? 'Edit Session' : 'Add Session' }}</h2>
          <button @click="closeFormModal" class="p-2 hover:bg-slate-100 dark:hover:bg-slate-700 rounded-lg transition-colors">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        <div class="p-5 overflow-y-auto max-h-[calc(90vh-140px)]">
          <div class="grid grid-cols-2 gap-4">
            <div class="col-span-2">
              <label class="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1">Session ID</label>
              <input v-model="formData.session_id" type="text" class="w-full px-3 py-2 text-xs bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white" disabled />
            </div>
            <div>
              <label class="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1">IP Address</label>
              <input v-model="formData.ip_address" type="text" class="w-full px-3 py-2 text-xs bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white" />
            </div>
            <div class="flex items-center">
              <label class="flex items-center gap-2 cursor-pointer">
                <input v-model="formData.is_active" type="checkbox" class="w-4 h-4 text-blue-600 border-slate-300 dark:border-slate-600 rounded" />
                <span class="text-xs text-slate-700 dark:text-slate-300">Active Session</span>
              </label>
            </div>
          </div>
        </div>
        <div class="flex items-center justify-end gap-2 p-5 border-t border-slate-200 dark:border-slate-700">
          <button @click="closeFormModal" class="px-3 py-2 text-xs bg-slate-200 dark:bg-slate-700 hover:bg-slate-300 dark:hover:bg-slate-600 text-slate-900 dark:text-white rounded-lg">Cancel</button>
          <button @click="saveSession" :disabled="saveLoading" class="px-3 py-2 text-xs bg-blue-500 hover:bg-blue-600 text-white rounded-lg" :class="{ 'opacity-50': saveLoading }">{{ saveLoading ? 'Saving...' : (selectedSession?.id ? 'Update' : 'Create') }}</button>
        </div>
      </div>
    </div>

    <!-- Delete Confirmation -->
    <ConfirmDialog :show="showDeleteModal" title="Delete Session" :message="`Delete session ${sessionToDelete?.session_id?.substring(0, 8)}?`" type="danger" @confirm="confirmDelete" @cancel="closeDeleteModal" />
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useApi } from '../composables/useApi'
import ModernMetricCard from '../components/MetricCard.vue'
import ConfirmDialog from '../components/ConfirmDialog.vue'

export default {
  name: 'Sessions',
  components: { ModernMetricCard, ConfirmDialog },
  setup() {
    const { loading, error, makeRequest } = useApi()
    const sessions = ref([])
    const stats = ref({})
    const searchTerm = ref('')
    const statusFilter = ref('')
    const showFormModal = ref(false)
    const showDeleteModal = ref(false)
    const selectedSession = ref(null)
    const sessionToDelete = ref(null)
    const saveLoading = ref(false)
    const deleteLoading = ref(false)
    const formData = ref({
      session_id: '',
      ip_address: '',
      is_active: true
    })

    const filteredSessions = computed(() => {
      let result = sessions.value
      if (searchTerm.value) {
        const term = searchTerm.value.toLowerCase()
        result = result.filter(s => s.session_id?.toLowerCase().includes(term) || s.user_account?.toLowerCase().includes(term) || s.ip_address?.includes(term))
      }
      if (statusFilter.value) {
        result = result.filter(s => s.is_active === (statusFilter.value === 'true'))
      }
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
    
    const openAddModal = () => {
      selectedSession.value = null
      formData.value = {
        session_id: '',
        ip_address: '',
        is_active: true
      }
      showFormModal.value = true
    }
    
    const openEditModal = (session) => {
      selectedSession.value = session
      formData.value = {
        session_id: session.session_id || '',
        ip_address: session.ip_address || '',
        is_active: session.is_active || false
      }
      showFormModal.value = true
    }
    
    const closeFormModal = () => {
      showFormModal.value = false
      selectedSession.value = null
      formData.value = {
        session_id: '',
        ip_address: '',
        is_active: true
      }
    }

    const saveSession = async () => {
      saveLoading.value = true
      try {
        if (selectedSession.value?.id) {
          await makeRequest('patch', `suapi/sessions/${selectedSession.value.id}/`, formData.value)
        } else {
          await makeRequest('post', 'suapi/sessions/', formData.value)
        }
        await refreshData()
        closeFormModal()
      } catch (err) {
        alert('Error: ' + (err.response?.data?.error || err.message))
      } finally {
        saveLoading.value = false
      }
    }

    const terminateSession = async (session) => {
      if (!confirm(`Terminate session ${session.session_id?.substring(0, 8)}?`)) return
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
      loading, error, sessions, stats, searchTerm, statusFilter, showFormModal, showDeleteModal, selectedSession, sessionToDelete,
      saveLoading, deleteLoading, formData, filteredSessions, fetchSessions, refreshData,
      openAddModal, openEditModal, closeFormModal, saveSession, terminateSession, openDeleteModal, closeDeleteModal, confirmDelete
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
