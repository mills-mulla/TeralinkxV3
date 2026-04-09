<template>
  <div class="space-y-4 animate-fade-in">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-lg font-semibold text-slate-900 dark:text-white">Devices</h1>
        <p class="text-xs text-slate-500 dark:text-slate-400 mt-0.5">Monitor and manage user devices</p>
      </div>
      <div class="flex items-center gap-2">
        <button @click="openAddModal" class="px-3 py-1.5 bg-blue-500 hover:bg-blue-600 text-white rounded-lg text-xs flex items-center gap-1.5">
          <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
          </svg>
          Add Device
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
            <h3 class="text-sm font-medium text-rose-800 dark:text-rose-400">Failed to load devices</h3>
            <p class="text-xs text-rose-600 dark:text-rose-500 mt-1">{{ error }}</p>
          </div>
        </div>
        <button @click="fetchDevices" class="px-3 py-1.5 bg-rose-600 text-white rounded-lg hover:bg-rose-700 text-sm">Retry</button>
      </div>
    </div>

    <!-- Metrics -->
    <div class="grid grid-cols-2 md:grid-cols-4 gap-3 animate-slide-up">
      <ModernMetricCard title="Total Devices" :value="stats.total_devices" color="blue">
        <svg class="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
          <path d="M17 1.01L7 1c-1.1 0-2 .9-2 2v18c0 1.1.9 2 2 2h10c1.1 0 2-.9 2-2V3c0-1.1-.9-1.99-2-1.99zM17 19H7V5h10v14z"/>
        </svg>
      </ModernMetricCard>
      <ModernMetricCard title="Active" :value="stats.active_devices" color="emerald">
        <svg class="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
          <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
        </svg>
      </ModernMetricCard>
      <ModernMetricCard title="Online" :value="stats.online_devices" color="cyan">
        <svg class="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
          <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
        </svg>
      </ModernMetricCard>
      <ModernMetricCard title="Trusted" :value="stats.trusted_devices" color="purple">
        <svg class="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
          <path d="M12 1L3 5v6c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V5l-9-4zm-2 16l-4-4 1.41-1.41L10 14.17l6.59-6.59L18 9l-8 8z"/>
        </svg>
      </ModernMetricCard>
    </div>

    <!-- Search & Filters -->
    <div class="space-y-3 animate-slide-up" style="animation-delay: 0.1s">
      <div class="flex items-center gap-2">
        <div class="flex-1">
          <input v-model="searchTerm" type="text" placeholder="Search devices..." class="w-full px-3 py-1.5 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white text-xs" />
        </div>
        <select v-model="statusFilter" class="px-3 py-1.5 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white text-xs">
          <option value="">All Status</option>
          <option value="active">Active</option>
          <option value="inactive">Inactive</option>
          <option value="suspended">Suspended</option>
        </select>
        <select v-model="typeFilter" class="px-3 py-1.5 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white text-xs">
          <option value="">All Types</option>
          <option value="phone">Phone</option>
          <option value="laptop">Laptop</option>
          <option value="tablet">Tablet</option>
          <option value="desktop">Desktop</option>
        </select>
      </div>

      <!-- Table -->
      <div class="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 overflow-hidden">
        <div class="overflow-x-auto">
          <table class="w-full">
            <thead class="bg-slate-50 dark:bg-slate-900 border-b border-slate-200 dark:border-slate-700">
              <tr>
                <th class="px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400">Device</th>
                <th class="px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400">User</th>
                <th class="px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400">Type</th>
                <th class="px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400">Status</th>
                <th class="px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400">Online</th>
                <th class="px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400">Connections</th>
                <th class="px-3 py-2 text-right text-[10px] font-medium text-slate-600 dark:text-slate-400">Actions</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-200 dark:divide-slate-700">
              <tr v-for="device in filteredDevices" :key="device.id" @click="openEditModal(device)" class="hover:bg-slate-50 dark:hover:bg-slate-700/50 transition-colors cursor-pointer">
                <td class="px-3 py-2">
                  <div class="flex items-center gap-2">
                    <div class="w-7 h-7 rounded-lg bg-gradient-to-br from-blue-500 to-cyan-600 flex items-center justify-center">
                      <svg class="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 24 24">
                        <path d="M17 1.01L7 1c-1.1 0-2 .9-2 2v18c0 1.1.9 2 2 2h10c1.1 0 2-.9 2-2V3c0-1.1-.9-1.99-2-1.99zM17 19H7V5h10v14z"/>
                      </svg>
                    </div>
                    <div>
                      <p class="text-xs font-medium text-slate-900 dark:text-white">{{ device.device_name || 'Unknown' }}</p>
                      <p class="text-[10px] text-slate-500 dark:text-slate-400">{{ device.mac_address }}</p>
                    </div>
                  </div>
                </td>
                <td class="px-3 py-2 text-xs text-slate-900 dark:text-white">{{ device.user_account || 'N/A' }}</td>
                <td class="px-3 py-2">
                  <span class="px-1.5 py-0.5 text-[10px] font-medium rounded-full bg-slate-100 dark:bg-slate-700 text-slate-700 dark:text-slate-300">
                    {{ device.device_type || 'unknown' }}
                  </span>
                </td>
                <td class="px-3 py-2">
                  <span class="px-1.5 py-0.5 text-[10px] font-medium rounded-full" :class="getStatusBadge(device.status)">
                    {{ device.status }}
                  </span>
                </td>
                <td class="px-3 py-2">
                  <span class="flex items-center gap-1 text-xs" :class="device.is_online ? 'text-emerald-600 dark:text-emerald-400' : 'text-slate-400 dark:text-slate-600'">
                    <span class="w-1.5 h-1.5 rounded-full" :class="device.is_online ? 'bg-emerald-500' : 'bg-slate-400'"></span>
                    {{ device.is_online ? 'Online' : 'Offline' }}
                  </span>
                </td>
                <td class="px-3 py-2 text-xs text-slate-900 dark:text-white">{{ device.total_connections || 0 }}</td>
                <td class="px-3 py-2 text-right">
                  <div class="flex items-center justify-end gap-0.5">
                    <button @click.stop="openEditModal(device)" class="p-1 hover:bg-blue-100 dark:hover:bg-blue-600 rounded transition-colors" title="Edit">
                      <svg class="w-3.5 h-3.5 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                      </svg>
                    </button>
                    <button v-if="device.status === 'active'" @click.stop="blockDevice(device)" class="p-1 hover:bg-amber-100 dark:hover:bg-amber-600 rounded transition-colors" title="Block">
                      <svg class="w-3.5 h-3.5 text-amber-600 dark:text-amber-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728A9 9 0 015.636 5.636m12.728 12.728L5.636 5.636" />
                      </svg>
                    </button>
                    <button v-else @click.stop="unblockDevice(device)" class="p-1 hover:bg-emerald-100 dark:hover:bg-emerald-600 rounded transition-colors" title="Unblock">
                      <svg class="w-3.5 h-3.5 text-emerald-600 dark:text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                    </button>
                    <button @click.stop="openDeleteModal(device)" class="p-1 hover:bg-red-100 dark:hover:bg-red-600 rounded transition-colors" title="Delete">
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

    <!-- Edit Device Modal -->
    <div v-if="showFormModal" class="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4" @click.self="closeFormModal">
      <div class="bg-white dark:bg-slate-800 rounded-xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-hidden">
        <div class="flex items-center justify-between p-5 border-b border-slate-200 dark:border-slate-700">
          <h2 class="text-base font-semibold text-slate-900 dark:text-white">{{ selectedDevice?.id ? 'Edit Device' : 'Add Device' }}</h2>
          <button @click="closeFormModal" class="p-2 hover:bg-slate-100 dark:hover:bg-slate-700 rounded-lg transition-colors">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        <div class="p-5 overflow-y-auto max-h-[calc(90vh-140px)]">
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1">MAC Address</label>
              <input v-model="formData.mac_address" type="text" placeholder="00:11:22:33:44:55" class="w-full px-3 py-2 text-xs bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white" />
            </div>
            <div>
              <label class="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1">Device Name</label>
              <input v-model="formData.device_name" type="text" class="w-full px-3 py-2 text-xs bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white" />
            </div>
            <div>
              <label class="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1">Device Type</label>
              <select v-model="formData.device_type" class="w-full px-3 py-2 text-xs bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white">
                <option value="phone">Phone</option>
                <option value="laptop">Laptop</option>
                <option value="tablet">Tablet</option>
                <option value="desktop">Desktop</option>
              </select>
            </div>
            <div>
              <label class="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1">Platform</label>
              <select v-model="formData.device_platform" class="w-full px-3 py-2 text-xs bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white">
                <option value="windows">Windows</option>
                <option value="macos">macOS</option>
                <option value="linux">Linux</option>
                <option value="android">Android</option>
                <option value="ios">iOS</option>
              </select>
            </div>
            <div>
              <label class="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1">Status</label>
              <select v-model="formData.status" class="w-full px-3 py-2 text-xs bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white">
                <option value="active">Active</option>
                <option value="inactive">Inactive</option>
                <option value="suspended">Suspended</option>
              </select>
            </div>
            <div class="flex items-center">
              <label class="flex items-center gap-2 cursor-pointer">
                <input v-model="formData.is_trusted" type="checkbox" class="w-4 h-4 text-blue-600 border-slate-300 dark:border-slate-600 rounded" />
                <span class="text-xs text-slate-700 dark:text-slate-300">Trusted Device</span>
              </label>
            </div>
          </div>
        </div>
        <div class="flex items-center justify-end gap-2 p-5 border-t border-slate-200 dark:border-slate-700">
          <button @click="closeFormModal" class="px-3 py-2 text-xs bg-slate-200 dark:bg-slate-700 hover:bg-slate-300 dark:hover:bg-slate-600 text-slate-900 dark:text-white rounded-lg">Cancel</button>
          <button @click="saveDevice" :disabled="saveLoading" class="px-3 py-2 text-xs bg-blue-500 hover:bg-blue-600 text-white rounded-lg" :class="{ 'opacity-50': saveLoading }">{{ saveLoading ? 'Saving...' : (selectedDevice?.id ? 'Update' : 'Create') }}</button>
        </div>
      </div>
    </div>

    <!-- Delete Confirmation -->
    <ConfirmDialog :show="showDeleteModal" title="Delete Device" :message="`Delete device ${deviceToDelete?.device_name}?`" type="danger" @confirm="confirmDelete" @cancel="closeDeleteModal" />
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useApi } from '../composables/useApi'
import ModernMetricCard from '../components/MetricCard.vue'
import ConfirmDialog from '../components/ConfirmDialog.vue'

export default {
  name: 'Devices',
  components: { ModernMetricCard, ConfirmDialog },
  setup() {
    const { loading, error, makeRequest } = useApi()
    const devices = ref([])
    const stats = ref({})
    const searchTerm = ref('')
    const statusFilter = ref('')
    const typeFilter = ref('')
    const showFormModal = ref(false)
    const showDeleteModal = ref(false)
    const selectedDevice = ref(null)
    const deviceToDelete = ref(null)
    const saveLoading = ref(false)
    const deleteLoading = ref(false)
    const formData = ref({
      mac_address: '',
      device_name: '',
      device_type: 'phone',
      device_platform: 'android',
      status: 'active',
      is_trusted: false
    })

    const filteredDevices = computed(() => {
      let result = devices.value
      if (searchTerm.value) {
        const term = searchTerm.value.toLowerCase()
        result = result.filter(d => d.mac_address?.toLowerCase().includes(term) || d.device_name?.toLowerCase().includes(term) || d.user_account?.toLowerCase().includes(term))
      }
      if (statusFilter.value) {
        result = result.filter(d => d.status === statusFilter.value)
      }
      if (typeFilter.value) {
        result = result.filter(d => d.device_type === typeFilter.value)
      }
      return result
    })

    const fetchDevices = async () => {
      try {
        const data = await makeRequest('get', 'suapi/devices/')
        devices.value = data.results || data
      } catch (err) {
        console.error('Error:', err)
      }
    }

    const fetchStats = async () => {
      try {
        stats.value = await makeRequest('get', 'suapi/devices/stats/')
      } catch (err) {
        console.error('Error:', err)
      }
    }

    const refreshData = () => Promise.all([fetchDevices(), fetchStats()])
    
    const openAddModal = () => {
      selectedDevice.value = null
      formData.value = {
        mac_address: '',
        device_name: '',
        device_type: 'phone',
        device_platform: 'android',
        status: 'active',
        is_trusted: false
      }
      showFormModal.value = true
    }
    
    const openEditModal = (device) => {
      selectedDevice.value = device
      formData.value = {
        mac_address: device.mac_address || '',
        device_name: device.device_name || '',
        device_type: device.device_type || 'phone',
        device_platform: device.device_platform || 'android',
        status: device.status || 'active',
        is_trusted: device.is_trusted || false
      }
      showFormModal.value = true
    }
    
    const closeFormModal = () => {
      showFormModal.value = false
      selectedDevice.value = null
      formData.value = {
        mac_address: '',
        device_name: '',
        device_type: 'phone',
        device_platform: 'android',
        status: 'active',
        is_trusted: false
      }
    }

    const saveDevice = async () => {
      saveLoading.value = true
      try {
        if (selectedDevice.value?.id) {
          await makeRequest('patch', `suapi/devices/${selectedDevice.value.id}/`, formData.value)
        } else {
          await makeRequest('post', 'suapi/devices/', formData.value)
        }
        await refreshData()
        closeFormModal()
      } catch (err) {
        alert('Error: ' + (err.response?.data?.error || err.message))
      } finally {
        saveLoading.value = false
      }
    }

    const blockDevice = async (device) => {
      try {
        await makeRequest('post', `suapi/devices/${device.id}/block/`, { reason: 'Admin action' })
        await refreshData()
      } catch (err) {
        alert('Error: ' + (err.response?.data?.error || err.message))
      }
    }

    const unblockDevice = async (device) => {
      try {
        await makeRequest('post', `suapi/devices/${device.id}/unblock/`, { reason: 'Admin action' })
        await refreshData()
      } catch (err) {
        alert('Error: ' + (err.response?.data?.error || err.message))
      }
    }

    const openDeleteModal = (device) => { deviceToDelete.value = device; showDeleteModal.value = true }
    const closeDeleteModal = () => { showDeleteModal.value = false; deviceToDelete.value = null }

    const confirmDelete = async () => {
      deleteLoading.value = true
      try {
        await makeRequest('delete', `suapi/devices/${deviceToDelete.value.id}/`)
        await refreshData()
        closeDeleteModal()
      } catch (err) {
        alert('Error: ' + (err.response?.data?.error || err.message))
      } finally {
        deleteLoading.value = false
      }
    }

    const getStatusBadge = (status) => {
      const badges = {
        'active': 'bg-emerald-100 dark:bg-emerald-500/20 text-emerald-700 dark:text-emerald-400',
        'inactive': 'bg-slate-100 dark:bg-slate-700 text-slate-700 dark:text-slate-400',
        'suspended': 'bg-red-100 dark:bg-red-500/20 text-red-700 dark:text-red-400'
      }
      return badges[status] || badges.inactive
    }

    onMounted(refreshData)

    return {
      loading, error, devices, stats, searchTerm, statusFilter, typeFilter, showFormModal, showDeleteModal, selectedDevice, deviceToDelete,
      saveLoading, deleteLoading, formData, filteredDevices, fetchDevices, refreshData,
      openAddModal, openEditModal, closeFormModal, saveDevice, blockDevice, unblockDevice, openDeleteModal, closeDeleteModal, confirmDelete, getStatusBadge
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
